<script>
  //speech emotion recognition model's training data was sampled with 48kHz
  let sampleRate = 48000;
  let audioCtx = new AudioContext({ sampleRate: sampleRate });

  // pause audio context. audio context will be resumed by button click
  audioCtx.suspend();

  let AUDIO_BUFFER_SIZE = 4096;
  let audioBufferOutputData;
  let audioScriptNode = audioCtx.createScriptProcessor(AUDIO_BUFFER_SIZE, 1, 1);
  let analyser = audioCtx.createAnalyser();
  let source;
  let canvas;

  let isStreamingAudio = false;

  let portManager;

  export const initComponent = (portComponent) => {
    portManager = portComponent;
    canvas = document.getElementById("oscilloscope");
    initAudioStream();
    initStartBttn();
/*
--- Debugging Code Start ---
*/
    initSaveAudioBttn();
/*
--- Debugging Code End ---
*/
  };

  function initAudioStream() {
    navigator.mediaDevices
      .getUserMedia({ audio: { sampleRate: sampleRate}, video: false })
      .then((stream) => {
        handleAudioStream(stream);
        console.log("Sampling at Rate: ", audioCtx.sampleRate);
      })
      .catch((err) => {
        console.log(`There has been an error: ${err}`);
      });
  }

  function initStartBttn() {
    let startBttn = document.getElementById("start-oscilloscope");
    startBttn.addEventListener("click", (e) => {
      audioCtx.resume().then(() => {
        console.log("Audio context resumed");
        e.target.disabled = true;
      });
      isStreamingAudio = true;
    });
  }

/*
--- Debugging Code Start ---
*/
  function initSaveAudioBttn() {
    let saveButton = document.getElementById("save-audio");
    saveButton.addEventListener("click", function() {
      const wavBlob = bufferArrayToWave(audioData, audioCtx.sampleRate);
      const url = URL.createObjectURL(wavBlob);

      // Create a new anchor element
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = 'test.wav';

      // Append anchor to the DOM, click it to initiate download, and clean up
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    });
  }
/*
--- Debugging Code End ---
*/
  function handleAudioStream(stream) {
    initSourceAndAnalyser(stream);
    initSendingAudioOverPort();
    drawAudioStreamToCanvas(canvas.getContext("2d"));
  }

  function initSourceAndAnalyser(stream) {
    source = audioCtx.createMediaStreamSource(stream);
    source.connect(analyser);
    // set window size of Fast Fourier Transformation to (default) 2048
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0;
  }

  function initSendingAudioOverPort() {
    audioScriptNode.onaudioprocess = (event) => {
      let inputBuffer = event.inputBuffer;
      let outputBuffer = event.outputBuffer;
      let inputData = inputBuffer.getChannelData(0);
      audioBufferOutputData = outputBuffer.getChannelData(0);

      for (let i = 0; i < inputBuffer.length; i++) {
        audioBufferOutputData[i] = inputData[i];
      }
      streamAudioOverPort();
    };
    source.connect(audioScriptNode);
    audioScriptNode.connect(audioCtx.destination);
  }

  function streamAudioOverPort() {
    if (isStreamingAudio) {
      portManager.streamAudioOverPort(audioBufferOutputData);
/*
--- Debugging Code Start ---
*/
      // Append new buffer data
      audioData.push(new Float32Array(audioBufferOutputData));
      // Trim old data to keep only last 4 seconds
      while (audioData.length > maxBufferLength) {
        audioData.shift();
      }
/*
--- Debugging Code End ---
*/
    }
  }

  function drawAudioStreamToCanvas(canvasCtx) {
    resetCanvasFill(canvasCtx);
    const freqBarArray = getFreqBarArrFromAnalyser();
    drawFrequencyBarsToCanvas(freqBarArray, canvasCtx);
    // loop drawing of the audio stream
    requestAnimationFrame(() => {
      drawAudioStreamToCanvas(canvasCtx);
    });
  }

  function resetCanvasFill(canvasCtx) {
    canvasCtx.fillStyle = "rgb(0, 0, 0)";
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
  }

  function getFreqBarArrFromAnalyser() {
    let dataArray = new Uint8Array(analyser.frequencyBinCount);
    // copy current frequency data into `dataArray`
    analyser.getByteFrequencyData(dataArray);
    return dataArray;
  }

  function drawFrequencyBarsToCanvas(freqDataArray, canvasCtx) {
    let barWidth = (canvas.width / freqDataArray.length) * 2.5;
    let offset = 0;
    for (let i = 0; i < freqDataArray.length; i++) {
      drawBarToCanvas(offset, barWidth, freqDataArray[i], canvasCtx);
      offset += barWidth + 1;
    }
  }

  function drawBarToCanvas(x, barWidth, barHeight, canvasCtx) {
    canvasCtx.fillStyle = "rgb(" + (barHeight + 100) + ",50,50)";
    canvasCtx.fillRect(
      x,
      canvas.height - barHeight / 2,
      barWidth,
      barHeight / 2
    );
  }

/*
--- Debugging Code Start ---
*/

  let audioData = [];
  let maxBufferLength = 4 * audioCtx.sampleRate / AUDIO_BUFFER_SIZE; // For 4 seconds

  function bufferArrayToWave(audioData, sampleRate) {
    let length = audioData.length * audioData[0].length;
    const tempBuffer = new ArrayBuffer(44 + length * 2);
    const view = new DataView(tempBuffer);
    const numOfChan = 1;

    view.setUint32(0, 1380533830, false);
    view.setUint32(4, 36 + length, true);
    view.setUint32(8, 1463899717, false);
    view.setUint32(12, 1718449184, false);
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numOfChan, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 4, true);
    view.setUint16(32, numOfChan * 2, true);
    view.setUint16(34, 16, true);
    view.setUint32(36, 1684108385, false);
    view.setUint32(40, length, true);

    let offset = 44;
    const isLittleEndian = true;
    for (let i = 0; i < audioData.length; i++) {
      let nowBuffering = audioData[i];
      for (let j = 0; j < nowBuffering.length; j++) {
        view.setInt16(offset, nowBuffering[j] * 0x7FFF, isLittleEndian);
        offset += 2;
      }
    }

    console.log(view);
    return new Blob([view], { type: 'audio/wav' });
  }
/*
--- Debugging Code End ---
*/

</script>

<div class="content">
  <div class="header">
    <h1>MICROPHONE</h1>
  </div>

  <canvas id="oscilloscope" />
  <button id="start-oscilloscope" class="button">Start audio stream</button>
  <button id="save-audio" class="button">Save Audio</button>
</div>
