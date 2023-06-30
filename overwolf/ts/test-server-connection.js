const WebSocket = require('ws')


let ws = new WebSocket('ws://127.0.0.1:5000');


ws.on('open', () => handleConnectionOpened())
ws.on('message', (data) => handleMessage(ws, data))
ws.on('close', () => console.log('closing websocket'))

function handleConnectionOpened() {
  const testString = 'Jon Doe';
  console.log(`connection established. Sending string: "${testString}"`)
  ws.send(testString);
}

function handleMessage(ws, data) {
  console.log('Message received over websocket')
  const text = data.toString();

  // data is unbuffered
  console.log(text)

}

function showMessage(message) {
  console.info(message)
}
