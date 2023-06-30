<script>
  // html video element that renders the live video stream from loaded camera
  let liveVideoEl;
  // (invisible) canvas that captures frames from `liveVideoEl`
  let captureCanvas;
  const CAPTURE_FREQUENCY = 3000;
  // canvas that renders a preview of the 128x128 image sent over port.
  let previewImgCanvas;
  // Injected by App. Manages websocket connections
  let portManager;

  export const initComponent = (portComponent) => {
    portManager = portComponent;
    initVideo();
    initCanvases();
    setInterval(drawPreviewAndSendImgDataOverPort, CAPTURE_FREQUENCY);
  };

  function initVideo() {
    liveVideoEl = document.getElementById("camera-video");
    loadCameraDeviceAndPassStreamToLiveVideoSrc();
  }

  function initCanvases() {
    captureCanvas = document.createElement("canvas");
    captureCanvas.width = 240;
    captureCanvas.height = 135;
    previewImgCanvas = document.getElementById("preview-canvas");
  }

  // Modified from original: https://www.damirscorner.com/blog/posts/20170317-RenderCapturedVideoToFullPageCanvas.html
  function loadCameraDeviceAndPassStreamToLiveVideoSrc() {
    if (navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices
        .getUserMedia({
          audio: false,
          video: { facingMode: { ideal: "environment" } },
        })
        .then(
          (stream) => {
            liveVideoEl.srcObject = stream;
          },
          (error) => console.log(error)
        );
    } else {
      alert(
        "Please update browser to support the minimal requirements found here: https://caniuse.com/stream"
      );
    }
  }

  function drawPreviewAndSendImgDataOverPort() {
    drawPreviewImgToCanvas();
    const imgStringBase64 = previewImgCanvas.toDataURL();
    portManager.sendImgInputOverPort(imgStringBase64);
  }

  function drawPreviewImgToCanvas() {
    captureCanvas.getContext("2d").drawImage(liveVideoEl, 0, 0, 240, 135);
    // video / capture canvas is 240x135 -> slice 128x128 square out of it
    const xSliceStart = 32;
    const xSliceEnd = xSliceStart + 128;
    const ySliceStart = 3;
    const ySliceEnd = ySliceStart + 128;

    previewImgCanvas
      .getContext("2d")
      .drawImage(
        captureCanvas,
        xSliceStart,
        ySliceStart,
        xSliceEnd,
        ySliceEnd,
        0,
        0,
        128,
        128
      );
  }
</script>

<div class="content">
  <div class="content video-content">
    <div class="header">
      <h1>CAMERA</h1>
    </div>
    <div>
      <div class="videoWrapper">
        <div class="camVideo">
          <!-- svelte-ignore a11y-media-has-caption -->
          <video
            id="camera-video"
            autoplay="true"
            height="240"
            width="135"
            style="width: 240px; height: 135px"
          />
          <h2>Live camera</h2>
        </div>
        <div class="previewFrameWrapper">
          <div class="previewFrame">
            <canvas id="preview-canvas" width="128" height="128" />
          </div>
          <h2>Frame</h2>
        </div>
      </div>
    </div>
  </div>
</div>
