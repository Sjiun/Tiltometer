import { OWGames, OWGamesEvents, OWHotkeys } from "@overwolf/overwolf-api-ts";
import { AppWindow } from "../AppWindow";
import { kHotkeys, kWindowNames, kGamesFeatures } from "../consts";
import WindowState = overwolf.windows.WindowStateEx;

import { MSG_CODE } from "../socket/client";
import TiltDetailChart from "../tilt_o_meter/tilt_detail_chart";
import TiltLog from "../tilt_o_meter/tilt_log";
import TiltRawLog from "../tilt_o_meter/tilt_raw_log";
import TiltCharts from "../tilt_o_meter/tilt_charts";
import TiltOMeter from "../tilt_o_meter/tilt_o_meter";

// The window displayed in-game while a game is running.
// It listens to all info events and to the game events listed in the consts.ts file
// and writes them to the relevant log using <pre> tags.
// The window also sets up Ctrl+F as the minimize/restore hotkey.
// Like the background window, it also implements the Singleton design pattern.
class InGame extends AppWindow {
  private static _instance: InGame;
  private _gameEventsListener: OWGamesEvents;
  private _eventsLog: HTMLElement;
  private _infoLog: HTMLElement;

  private constructor() {
    super(kWindowNames.inGame);

    this._eventsLog = document.getElementById("eventsLog");
    this._infoLog = document.getElementById("infoLog");

    this.setToggleHotkeyBehavior();
    this.setToggleHotkeyText();
  }

  public static instance() {
    if (!this._instance) {
      this._instance = new InGame();
    }

    return this._instance;
  }

  public async run() {
    const gameClassId = await this.getCurrentGameClassId();

    const gameFeatures = kGamesFeatures.get(gameClassId);

    if (gameFeatures && gameFeatures.length) {
      this._gameEventsListener = new OWGamesEvents(
        {
          onInfoUpdates: this.onInfoUpdates.bind(this),
          onNewEvents: this.onNewEvents.bind(this),
        },
        gameFeatures
      );

      this._gameEventsListener.start();
    }
  }

  private onInfoUpdates(info) {
    this.logLine(this._infoLog, info, false);
  }

  private onNewEvents(e) {
    // skip clock event
    if (e.events[0].name == "match_clock") return false;

    handleTiltingRelevantEvents(e);

    // special events will be highlighted in the event log
    const shouldHighlight = e.events.some((event) => {
      switch (event.name) {
        case "kill":
        case "death":
        case "assist":
        case "level":
        case "matchStart":
        case "match_start":
        case "matchEnd":
        case "match_end":
          return true;
      }

      return false;
    });
    this.logLine(this._eventsLog, e, shouldHighlight);
  }

  // Displays the toggle minimize/restore hotkey in the window header
  private async setToggleHotkeyText() {
    const gameClassId = await this.getCurrentGameClassId();
    const hotkeyText = await OWHotkeys.getHotkeyText(
      kHotkeys.toggle,
      gameClassId
    );
    const hotkeyElem = document.getElementById("hotkey");
    hotkeyElem.textContent = hotkeyText;
  }

  // Sets toggleInGameWindow as the behavior for the Ctrl+F hotkey
  private async setToggleHotkeyBehavior() {
    const toggleInGameWindow = async (
      hotkeyResult: overwolf.settings.hotkeys.OnPressedEvent
    ): Promise<void> => {
      console.log(`pressed hotkey for ${hotkeyResult.name}`);
      const inGameState = await this.getWindowState();

      if (
        inGameState.window_state === WindowState.NORMAL ||
        inGameState.window_state === WindowState.MAXIMIZED
      ) {
        this.currWindow.minimize();
      } else if (
        inGameState.window_state === WindowState.MINIMIZED ||
        inGameState.window_state === WindowState.CLOSED
      ) {
        this.currWindow.restore();
      }
    };

    OWHotkeys.onHotkeyDown(kHotkeys.toggle, toggleInGameWindow);
  }

  // Appends a new line to the specified log
  private logLine(log: HTMLElement, data, highlight) {
    const line = document.createElement("pre");
    line.textContent = JSON.stringify(data);

    if (highlight) {
      line.className = "highlight";
    }

    // Check if scroll is near bottom
    const shouldAutoScroll =
      log.scrollTop + log.offsetHeight >= log.scrollHeight - 10;

    log.appendChild(line);

    if (shouldAutoScroll) {
      log.scrollTop = log.scrollHeight;
    }
  }

  private async getCurrentGameClassId(): Promise<number | null> {
    const info = await OWGames.getRunningGameInfo();

    return info && info.isRunning && info.classId ? info.classId : null;
  }
}

function handleTiltingRelevantEvents(event) {
  switch (event.events[0].name) {
    case "kill":
      handleKillEvent(event.events[0].data);
      break;
    case "death":
      handleDeathEvent(event.events[0].data);
      break;
    case "assist":
      handleAssistEvent(event.events[0].data);
      break;
  }
}

function handleKillEvent(eventDataString) {
  const eventData = JSON.parse(eventDataString);
  let time = new Date().toLocaleTimeString().split(" ")[0];
  const tiltModifier = calcNewTiltValueFromEvent("ge", eventData.label);
  const killEvent = {
    time: time,
    type: "ge",
    data: eventData.label,
    id: eventList.length,
    tilt_mod: tiltModifier,
  };
  eventList.push(killEvent);
  tiltLog.renderGameEvent(killEvent);

  renderTiltValue();
}

function handleDeathEvent(eventDataString) {
  const time = new Date().toLocaleTimeString().split(" ")[0];
  const tiltModifier = calcNewTiltValueFromEvent("ge", "death");
  const deathEvent = {
    time: time,
    type: "ge",
    data: "death",
    id: eventList.length,
    tilt_mod: tiltModifier,
  };
  eventList.push(deathEvent);
  tiltLog.renderGameEvent(deathEvent);
  renderTiltValue();
}

function handleAssistEvent(eventDataString) {
  const time = new Date().toLocaleTimeString().split(" ")[0];
  const tiltModifier = calcNewTiltValueFromEvent("ge", "assist");
  const assistEvent = {
    time: time,
    type: "ge",
    data: "assist",
    id: eventList.length,
    tilt_mod: tiltModifier,
  };
  eventList.push(assistEvent);
  tiltLog.renderGameEvent(assistEvent);
  renderTiltValue();
}

InGame.instance().run();

// ---------

// Magic numbers here until we have a multimodal model or empirical data
let fer_tilt_value = 0;
const ferTiltFactor = 0.6;
let last_fer_update = Date.now();
let ser_tilt_value = 0;
const serTiltFactor = 0.2;
let last_ser_update = Date.now();
let ge_tilt_value = 0;
const geTiltFactor = 0.2;
let total_tilt_value = 0;

const eventList = [];

// Tilt Event Detail Chart
const detailCanvas = document.getElementById(
  "detailChart"
) as HTMLCanvasElement;
const tiltDetailChart = new TiltDetailChart(eventList, detailCanvas);

// Tilt Event Log
const processedLogTableBody = document.getElementById("processedLogTableBody");
const tiltLog = new TiltLog(processedLogTableBody, tiltDetailChart);

// Tilt Event Raw Log
const ferList = document.getElementById("ferList");
const serList = document.getElementById("serList");
const pulseList = document.getElementById("pulseList");
const tiltRawLog = new TiltRawLog(ferList, serList, pulseList);

// Tilt Event Charts
const pulseChartCanvas = document.getElementById(
  "pulseChart"
) as HTMLCanvasElement;
const ferChartCanvas = document.getElementById("ferChart") as HTMLCanvasElement;
const serChartCanvas = document.getElementById("serChart") as HTMLCanvasElement;
const tiltCharts = new TiltCharts(
  pulseChartCanvas,
  ferChartCanvas,
  serChartCanvas
);

// Tilt Chart
const tiltOMeterDiv = document.getElementById("tiltChart") as HTMLDivElement;
const tiltOMeter = new TiltOMeter(tiltOMeterDiv);
const tiltValue = document.getElementById("tiltValue");
const chickenImg = document.getElementById("chickenImg") as HTMLImageElement;

// Websocket
let ws: WebSocket;
const wsBttn = document.getElementById("connectWsBttn") as HTMLButtonElement;
wsBttn.addEventListener("click", createWebsocketConnection);
const wsDisconnBttn = document.getElementById(
  "disconnectWsBttn"
) as HTMLButtonElement;
const exportBttn = document.getElementById("exportBttn") as HTMLButtonElement;
exportBttn.addEventListener("click", exportEventListAsCsv);
wsDisconnBttn.addEventListener("click", closeWebsocketConnection);
const wsStatus = document.getElementById("wsConnStatus");

function closeWebsocketConnection() {
  ws.close();
  wsBttn.innerText = "connect";
  wsStatus.style.backgroundColor = "#e49376";
  wsDisconnBttn.disabled = true;
  exportBttn.disabled = true;
}

function createWebsocketConnection() {
  if (ws) ws.close();
  wsBttn.innerText = "reconnect";
  ws = new WebSocket("ws://127.0.0.1:5000");
  ws.onopen = handleConnectionOpened;
  ws.onmessage = handleMessage;
  wsDisconnBttn.disabled = false;
  exportBttn.disabled = false;
  ws.onerror = (event) => {
    console.error(event);
    wsBttn.innerText = "connect";
    wsStatus.style.backgroundColor = "#e49376";
    wsDisconnBttn.disabled = true;
    exportBttn.disabled = true;
  };
}

function handleConnectionOpened() {
  wsStatus.style.backgroundColor = "#7dcb77";
  const greetingString = "Hello from OVERWOLF-DESKTOP";
  console.log("Sending connection message to server");
  ws.send(JSON.stringify([MSG_CODE["CONNECT"], greetingString]));
}

function handleMessage(mssgEvent) {
  const message = JSON.parse(mssgEvent.data);
  const msgCode = message[0];
  const msgContent = JSON.parse(message[1]);
  const msgTimestamp = message[2];
  switch (msgCode) {
    case MSG_CODE["SER_RESULT"]:
      handleSerDataMessage(msgContent, msgTimestamp);
      break;
    case MSG_CODE["FER_RESULT"]:
      handleFerDataMessage(msgContent, msgTimestamp);
      break;
    case MSG_CODE["PULSE_DATA"]:
      handlePulseDataMessage(msgContent, msgTimestamp);
      break;
    default:
      console.log("unhandled message. Code: ", msgCode);
  }
}

function handleSerDataMessage(updContent, time) {
  const serResultEvent = addSerResultToEvents(updContent, time);
  tiltRawLog.renderSerResultEvent(serResultEvent);
  tiltLog.renderSerResultEvent(serResultEvent);
  tiltCharts.updateSerGraph(updContent, time);
  renderTiltValue();
}

function addSerResultToEvents(serResultArr, time) {
  const eventType = "ser";
  const tiltModifier = calcNewTiltValueFromEvent(eventType, serResultArr);

  const serResultEvent = {
    time: time,
    type: "ser",
    data: serResultArr,
    id: eventList.length,
    tilt_mod: tiltModifier,
  };
  eventList.push(serResultEvent);
  return serResultEvent;
}

function handleFerDataMessage(updContent, time) {
  const ferResultEvent = addFerResultToEvents(updContent, time);
  tiltRawLog.renderFerResultEvent(ferResultEvent);
  tiltLog.renderFerResultEvent(ferResultEvent);
  tiltCharts.updateFerGraph(updContent, time);
  renderTiltValue();
}
function addFerResultToEvents(ferResultArr, time) {
  const eventType = "fer";
  const tiltModifier = calcNewTiltValueFromEvent(eventType, ferResultArr);
  const ferResultEvent = {
    time: time,
    type: eventType,
    data: ferResultArr,
    id: eventList.length,
    tilt_mod: tiltModifier,
  };
  eventList.push(ferResultEvent);
  return ferResultEvent;
}

function handlePulseDataMessage(updContent, time) {
  const pulseEvent = addPulseDataToEvents(updContent, time);
  tiltRawLog.renderPulseEvent(pulseEvent);
  tiltLog.renderPulseEvent(pulseEvent);
  tiltCharts.updatePulseGraph(updContent, time);
  renderTiltValue();
}
function addPulseDataToEvents(heartRate, time) {
  const eventType = "pulse";
  const tiltModifier = calcNewTiltValueFromEvent(eventType, heartRate);
  const pulseEvent = {
    time: time,
    type: eventType,
    data: heartRate,
    id: eventList.length,
    tilt_mod: tiltModifier,
  };
  eventList.push(pulseEvent);
  return pulseEvent;
}

// returns difference between old and new value
function calcNewTiltValueFromEvent(type, data) {
  const oldTiltValue = total_tilt_value;

  const timeNow = Date.now();
  switch (type) {
    case "pulse":
      // TODO: implement pulse
      break;
    case "fer":
      const secsSinceLastFerUpd = (timeNow - last_fer_update) / 1000;
      const ferSmoothingFactor = Math.min(secsSinceLastFerUpd / 100, 0.5);
      fer_tilt_value = ferSmoothingFactor * getTiltValueFromFerData(data) + (1 - ferSmoothingFactor) * fer_tilt_value;
      last_fer_update = timeNow;
      break;
    case "ser":
      const secsSinceLastSerUpd = (timeNow - last_ser_update) / 1000;
      const serSmoothingFactor = Math.min(secsSinceLastSerUpd / 100, 0.5);
      ser_tilt_value = serSmoothingFactor * getTiltValueFromSerData(data) + (1 - serSmoothingFactor) * ser_tilt_value;
      last_ser_update = timeNow;
      break;
    case "ge":
      ge_tilt_value += getTiltValueFromGameEventData(data);
      break;
    default:
      break;
  }
  calcTotalTiltValue();

  return total_tilt_value - oldTiltValue;
}

function getRandomFloat() {
  // get random value between 0.00 and 0.99
  const value = parseFloat(Math.random().toFixed(2));
  // return number with random sign
  return Math.random() < 0.5 ? value : -value;
}

function getTiltValueFromFerData(ferData) {
  let tilt = 0.0;
  tilt += ferData.angry;
  tilt += ferData.sad * 0.2;
  tilt -= ferData.happy;
  // surprise can be good or bad depending on which other emotions dominate
  const threshold = 0.1;
  if (
    ferData.happy - threshold >= ferData.angry &&
    ferData.happy - threshold >= ferData.sad
  ) {
    tilt -= ferData.surprise;
  }
  if (
    ferData.angry - threshold > ferData.happy ||
    ferData.sad - threshold > ferData.happy
  ) {
    tilt += ferData.surprise;
  }
  return tilt;
}

function getTiltValueFromSerData(serData) {
  let tilt = 0.0;
  tilt += serData.happy;
  tilt -= serData.sad / 2;
  tilt -= serData.angry / 2;
  // surprise can be good or bad depending on which other emotions dominate
  const threshold = 0.1;
  if (
    serData.happy - threshold >= serData.angry &&
    serData.happy - threshold >= serData.sad
  ) {
    tilt += serData.surprise;
  }
  if (
    serData.angry - threshold > serData.happy ||
    serData.sad - threshold > serData.happy
  ) {
    tilt -= serData.surprise;
  }
  return tilt / 5;
}

function getTiltValueFromGameEventData(data) {
  console.log(data);

  switch (data) {
    case "death":
      return 1.0;
    case "assist":
      return -0.4;
    case "kill":
      return -0.8;
    case "double_kill":
      return -0.9;
    case "triple_kill":
      return -1.0;
    case "quadra_kill":
      return -1.2;
    case "penta_kill":
      return -2.0;
  }
}

function calcTotalTiltValue() {
  total_tilt_value =
    serTiltFactor * ser_tilt_value +
    ferTiltFactor * fer_tilt_value +
    geTiltFactor * ge_tilt_value;

  // min bound tilt value = -1
  total_tilt_value = Math.max(total_tilt_value, -1);
  // max bound tilt value = 1
  total_tilt_value = Math.min(total_tilt_value, 1);
}

function renderTiltValue() {
  console.log("TILT: ", total_tilt_value);
  tiltValue.innerText = total_tilt_value.toFixed(4);
  tiltOMeter.updateTiltValue(total_tilt_value);
  if (total_tilt_value < -0.2) {
    chickenImg.src = "/img/chicken_happy.png";
    chickenImg.style.width = "120px";
    chickenImg.style.transform = "translate(-40px, 0%)";
  } else if (total_tilt_value > 0.5) {
    chickenImg.src = "/img/chicken_horror.png";
    chickenImg.style.width = "240px";
    chickenImg.style.transform = "translate(-30px, 0%)";
  } else {
    chickenImg.src = "/img/chicken_angry.png";
    chickenImg.style.width = "240px";
    chickenImg.style.transform = "translate(-40px, 0%)";
  }
}

function exportEventListAsCsv() {
  let csvContent = "TIME\tTYPE\tTILT_MOD\tDATA\r\n";
  eventList.forEach(function (eventData) {
    console.log(eventData.data);

    csvContent += `${eventData.time}\t${eventData.type}\t${eventData.tilt_mod
      }\t${JSON.stringify(eventData.data)}\r\n`;
  });
  console.log(csvContent);

  ws.send(JSON.stringify([MSG_CODE["CSV_EXPORT"], csvContent]));
}
