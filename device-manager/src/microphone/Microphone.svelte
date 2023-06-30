<script>
  let audioCtx = new AudioContext();
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
  };

  function initAudioStream() {
    navigator.mediaDevices
      .getUserMedia({ audio: true, video: false })
      .then((stream) => {
        handleAudioStream(stream);
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
</script>

<div class="content">
  <div class="header">
    <h1>MICROPHONE</h1>
  </div>

  <canvas id="oscilloscope" />
  <button id="start-oscilloscope" class="button">Start audio stream</button>
</div>
