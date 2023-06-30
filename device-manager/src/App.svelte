<script>
  import { onMount } from "svelte";

  import Pulse from "./pulse/Pulse.svelte";
  import Microphone from "./microphone/Microphone.svelte";
  import Camera from "./camera/Camera.svelte";
  import PortManager from "./port-manager/PortManager.svelte";

  let pulseComp;
  let micComp;
  let camComp;
  let portComp;

  onMount(async () => {
    // init pulse, camera and mic. Inject port Component as dependency
    camComp.initComponent(portComp);
    micComp.initComponent(portComp);
    pulseComp.initComponent(portComp);
  });
</script>

<div class="device-container">
  <div class="container" id="pulse-container">
    <Pulse bind:this={pulseComp} />
  </div>
  <div class="container" id="mic-container">
    <Microphone bind:this={micComp} />
  </div>
  <div class="container" id="cam-container">
    <Camera bind:this={camComp} />
  </div>
</div>

<br />
<hr />
<br />

<div class="port-container">
  <PortManager bind:this={portComp} />
</div>
