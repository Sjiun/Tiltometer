<script>
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

  let ws = new WebSocket("ws://127.0.0.1:5000");
  ws.binaryType = 'arraybuffer';

  ws.onopen = handleConnectionOpened;
  ws.onmessage = handleMessage;

  function handleConnectionOpened() {
    const greetingString = "DEVICE MANAGER IS UP AND CONNECTED";
    console.log("Sending connection message to server");
    ws.send(JSON.stringify([MSG_CODE["CONNECT"], greetingString]));
  }
  function handleMessage(msgEvent) {
    const msgJson = JSON.parse(msgEvent.data);
    const msgCode = msgJson[0];
    const msgContent = msgJson[1];
    console.log(`Message received over websocket with code: ${msgCode}`);
  }

  export const sendPulseResultOverPort = (heartRate) => {
    console.log(`Sending heart rate (${heartRate}) to server`);
    ws.send(JSON.stringify([MSG_CODE["PULSE_INPUT"], heartRate]));
  };

  export const sendImgInputOverPort = (base64ImgString) => {
    console.log(`Sending IMG to server.`);
    ws.send(JSON.stringify([MSG_CODE["IMAGE_INPUT"], base64ImgString]));
  };
  export const streamAudioOverPort = (data) => {
    console.log("---");
    console.log(data);
    console.log("---");
    ws.send(JSON.stringify([MSG_CODE["AUDIO_INPUT"], Array.from(data)]));
  };
</script>

<div class="content">
  <div class="header">
    <h1>PORT CONNECTION</h1>
  </div>
  to be done
</div>
