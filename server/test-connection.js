// const WebSocketClient = require('ws').Client
const WebSocket = require('ws').WebSocket

//  ein paar Codes, um zwischen Port-Nachrichten zu unterscheiden
const MSG_CODE = {
    CONNECT: 0,
    AUDIO_INPUT: 1,
    SER_INPUT: 2,
    SER_RESULT: 3,
    IMAGE_INPUT: 4,
    FER_INPUT: 5,
    FER_RESULT: 6,
    PULSE_INPUT: 7,
    PULSE_DATA: 8,
};

const uri = "ws://127.0.0.1:5002"
// let wsc = new WebSocketClient("ws://127.0.0.1:5000");
let wsc = new WebSocket(uri);
// wsc.connect("ws://127.0.0.1:5000")

wsc.onopen = handleConnectionOpened;
wsc.onmessage = handleMessage;

function handleConnectionOpened() {
    const greetingString = "Hello from DEVICE-MANAGER";
    console.log("Sending connection message to server");
    // wsc.send(JSON.stringify([MSG_CODE["CONNECT"], greetingString]));
    wsc.send(greetingString);
}
function handleMessage(mssgEvent) {
    console.log("Message received over websocket");
    console.log(mssgEvent.data);
}

const sendPulseResultOverPort = (heartRate) => {
    console.log(`Sending heart rate (${heartRate}) to server`);
    wsc.send(JSON.stringify([MSG_CODE["PULSE_INPUT"], heartRate]));
};