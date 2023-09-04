const fs = require('fs')
const WebSocketServer = require('ws').Server

const isMockingPulseData = false
const isMockingFerData = false
const isMockingSerData = false


const wss = new WebSocketServer({ port: 5000 })
console.log('WebSocket server is listening on port 5000')

const MSG_CODE = {
    'CONNECT': 0,
    'AUDIO_INPUT': 1,
    'SER_INPUT': 2,
    'SER_RESULT': 3,
    'IMAGE_INPUT': 4,
    'FER_INPUT': 5,
    'FER_RESULT': 6,
    'PULSE_INPUT': 7,
    'PULSE_DATA': 8,
    'CSV_EXPORT': 9,
}


wss.on('connection', function connection(ws) {
    console.log('New Connection to WebSocket server')
    ws.on('message', function incoming(msgString) {
        handleIncomingMessageFromWs(msgString, ws)
    })
    ws.on('close', () => {
        console.log('connection closed')
        console.log(`active connections: ${wss.clients.size}`)
    })
})


if (isMockingPulseData) {
    setInterval(sendMockedPulseData, 1000)
}
if (isMockingFerData) {
    setInterval(sendMockedFerResults, 5000)
}
if (isMockingSerData) {
    setInterval(sendMockedSerResults, 5000)
}



let audioInputCounter = 0;


function handleIncomingMessageFromWs(msgString, ws) {
    const message = JSON.parse(msgString)
    const msgCode = message[0]
    const msgContent = message[1]
    const msgTime = (new Date()).toLocaleTimeString()

    switch (msgCode) {
        case MSG_CODE['CONNECT']:
            handleConnectMessage(msgContent, msgTime)
            // send dummy request to test SER/FER
            break
        // audio stream sends Buffer of size 4096 about 12 times per second
        case MSG_CODE['AUDIO_INPUT']:
            handleAudioInputMessage(msgContent, msgTime)
            break
        case MSG_CODE['SER_INPUT']:
            handleSerInputMessage(msgContent, msgTime)
            break
        case MSG_CODE['SER_RESULT']:
            handleSerResultMessage(msgContent, msgTime)
            break
        case MSG_CODE['IMAGE_INPUT']:
            handleImageInputMessage(msgContent, msgTime)
            break
        case MSG_CODE['FER_INPUT']:
            handleFerInputMessage(msgContent, msgTime)
            break
        case MSG_CODE['FER_RESULT']:
            handleFerResultMessage(msgContent, msgTime)
            break
        case MSG_CODE['PULSE_INPUT']:
            handlePulseInputMessage(msgContent, msgTime)
            break
        case MSG_CODE['CSV_EXPORT']:
            handleCsvExportMessage(msgContent)
            break
        default:
            console.log('message code unknown')

    }
}

function handleConnectMessage(content, time) {
    console.log(`${time} - received CONNECT message:`)
    console.log(`\t${content}`)
}
function handleAudioInputMessage(content, time) {
    audioInputCounter += 1;
    if (audioInputCounter >= 100) {
        console.log(`${time} - received 100 AUDIO messages`);
        audioInputCounter = 0;
    }
    broadcastSerInput(content, time)
}
function handleSerInputMessage(content, time) {
    console.log(`${time} - received SER INPUT message:`)
    console.log(`\t${content}`)
}
function handleSerResultMessage(content, time) {
    console.log(`${time} - received SER RESULT message`)
    console.log(`\t${content}`)
    broadcastSerResult(content, time)

}
function handleImageInputMessage(content, time) {
    console.log(`${time} - received IMAGE message`)
    broadcastFerInput(content, time)
}
function handleFerInputMessage(content, time) {
    console.log(`${time} - received FER INPUT message:`)
}
function handleFerResultMessage(content, time) {
    console.log(`${time} - received FER RESULT message:`)
    console.log(`\t${content}`)
    broadcastFerResult(content, time)
}
function handlePulseInputMessage(heartRate, time) {
    console.log(`${time} - received PULSE message: ${heartRate}`)
    broadcastPulseData(heartRate, time)
}
function handleCsvExportMessage(message) {
    let csvContent = message
    const fileName = Date.now()
    fs.writeFile(__dirname + `/eventLogs/${fileName}.csv`, csvContent, err => {
        if (err) {
            console.log(err)
        }
    })

}


function broadcastPulseData(heartRate, time) {
    wss.clients.forEach(ws => {
        ws.send(JSON.stringify([MSG_CODE["PULSE_DATA"], heartRate, time]));
    })
}

function broadcastFerInput(base64String, time) {
    wss.clients.forEach(ws => {
        ws.send(JSON.stringify([MSG_CODE["FER_INPUT"], base64String, time]));
    })
}
function broadcastFerResult(ferResult, time) {
    wss.clients.forEach(ws => {
        ws.send(JSON.stringify([MSG_CODE["FER_RESULT"], ferResult, time]));
    })
}

function broadcastSerInput(audioData, time) {
    wss.clients.forEach(ws => {
        ws.send(JSON.stringify([MSG_CODE["SER_INPUT"], audioData, time]));
    })
}
function broadcastSerResult(ferResult, time) {
    wss.clients.forEach(ws => {
        ws.send(JSON.stringify([MSG_CODE["SER_RESULT"], ferResult, time]));
    })
}

function sendMockedPulseData() {
    const time = (new Date()).toLocaleTimeString();
    const heartRate = randomIntFromInterval(60, 100);
    wss.clients.forEach(ws => {
        ws.send(JSON.stringify([MSG_CODE["PULSE_DATA"], heartRate, time]))
    })
}
function sendMockedFerResults() {
    const time = (new Date()).toLocaleTimeString();
    const mockFerResult = {
        "angry": Math.random(),
        "happy": Math.random(),
        "neutral": Math.random(),
        "sad": Math.random(),
        "surprise": Math.random()
    }
    wss.clients.forEach(ws => {
        ws.send(JSON.stringify([MSG_CODE["FER_RESULT"], JSON.stringify(mockFerResult), time]));
    })
}

function sendMockedSerResults() {
    const time = (new Date()).toLocaleTimeString();
    const mockSerResult = {
        "angry": Math.random(),
        "happy": Math.random(),
        "neutral": Math.random(),
        "sad": Math.random(),
        "surprise": Math.random()
    }

    wss.clients.forEach(ws => {
        ws.send(JSON.stringify([MSG_CODE["SER_RESULT"], JSON.stringify(mockSerResult), time]));
    })
}

// min and max included 
function randomIntFromInterval(min, max) {
    return Math.floor(Math.random() * (max - min + 1) + min)
}