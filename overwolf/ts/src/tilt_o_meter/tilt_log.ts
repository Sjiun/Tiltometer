export default class TiltLog {
  constructor(private tableBody: HTMLElement, private detailChart) {}

  renderPulseEvent(pulseEvent) {
    const logRow = document.createElement("tr");
    logRow.setAttribute("data-event-id", pulseEvent.id);
    logRow.classList.add("pulseRow");

    const tdTime = document.createElement("td");
    const tdType = document.createElement("td");
    const tdData = document.createElement("td");
    const tdId = document.createElement("td");
    const tdTiltMod = document.createElement("td");
    tdTime.innerText = pulseEvent.time;
    tdType.innerText = pulseEvent.type;
    tdData.innerText = pulseEvent.data;
    tdId.innerText = pulseEvent.id;
    tdTiltMod.innerText =
      pulseEvent.tilt_mod > 0 ? "+" + pulseEvent.tilt_mod : pulseEvent.tilt_mod;
    logRow.appendChild(tdTime);
    logRow.appendChild(tdType);
    logRow.appendChild(tdData);
    logRow.appendChild(tdId);
    logRow.appendChild(tdTiltMod);
    this.tableBody.append(logRow);
  }

  renderGameEvent(gameEvent) {
    const logRow = document.createElement("tr");
    logRow.setAttribute("data-event-id", gameEvent.id);
    logRow.classList.add("gameEventRow");

    const tdTime = document.createElement("td");
    const tdType = document.createElement("td");
    const tdData = document.createElement("td");
    const tdId = document.createElement("td");
    const tdTiltMod = document.createElement("td");
    tdTime.innerText = gameEvent.time;
    tdType.innerText = gameEvent.type;
    tdData.innerText = gameEvent.data;
    tdId.innerText = gameEvent.id;
    const roundedTiltMod = gameEvent.tilt_mod.toFixed(4);
    tdTiltMod.innerText =
      gameEvent.tilt_mod > 0 ? "+" + roundedTiltMod : roundedTiltMod;
    logRow.appendChild(tdTime);
    logRow.appendChild(tdType);
    logRow.appendChild(tdData);
    logRow.appendChild(tdId);
    logRow.appendChild(tdTiltMod);
    this.tableBody.append(logRow);
  }

  renderFerResultEvent(ferResEvent) {
    const logRow = document.createElement("tr");
    logRow.setAttribute("data-event-id", ferResEvent.id);
    logRow.onclick = () => {
      this.detailChart.renderDetailChartOfRowEl(logRow);
    };
    const tdTime = document.createElement("td");
    const tdType = document.createElement("td");
    const tdData = document.createElement("td");
    const tdId = document.createElement("td");
    const tdTiltMod = document.createElement("td");
    tdTime.innerText = ferResEvent.time;
    tdType.innerText = ferResEvent.type;
    tdData.innerText = "[...]";
    tdId.innerText = ferResEvent.id;
    const roundedTiltMod = ferResEvent.tilt_mod.toFixed(4);
    tdTiltMod.innerText =
      ferResEvent.tilt_mod > 0 ? "+" + roundedTiltMod : roundedTiltMod;
    logRow.appendChild(tdTime);
    logRow.appendChild(tdType);
    logRow.appendChild(tdData);
    logRow.appendChild(tdId);
    logRow.appendChild(tdTiltMod);
    this.tableBody.append(logRow);
  }

  renderSerResultEvent(serResEvent) {
    const logRow = document.createElement("tr");
    logRow.setAttribute("data-event-id", serResEvent.id);
    logRow.onclick = () => {
      this.detailChart.renderDetailChartOfRowEl(logRow);
    };
    const tdTime = document.createElement("td");
    const tdType = document.createElement("td");
    const tdData = document.createElement("td");
    const tdId = document.createElement("td");
    const tdTiltMod = document.createElement("td");
    tdTime.innerText = serResEvent.time;
    tdType.innerText = serResEvent.type;
    tdData.innerText = "[...]";
    tdId.innerText = serResEvent.id;
    const roundedTiltMod = serResEvent.tilt_mod.toFixed(4);
    tdTiltMod.innerText =
      serResEvent.tilt_mod > 0 ? "+" + roundedTiltMod : roundedTiltMod;
    logRow.appendChild(tdTime);
    logRow.appendChild(tdType);
    logRow.appendChild(tdData);
    logRow.appendChild(tdId);
    logRow.appendChild(tdTiltMod);
    this.tableBody.append(logRow);
  }
}
