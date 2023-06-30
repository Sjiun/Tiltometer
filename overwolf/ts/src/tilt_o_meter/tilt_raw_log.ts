export default class TiltRawLog {
  constructor(
    private ferList: HTMLElement,
    private serList: HTMLElement,
    private pulseList: HTMLElement
  ) {}

  renderPulseEvent(pulseEvent) {
    const dataPoint = document.createElement("p");
    dataPoint.innerText = `${pulseEvent.time} - ${pulseEvent.data}`;
    this.pulseList.appendChild(dataPoint);
  }

  renderFerResultEvent(ferEvent) {
    const dataItem = document.createElement("ul");

    const timeEl = document.createElement("li");
    timeEl.innerHTML = `--- ${ferEvent.time} ---`;
    dataItem.appendChild(timeEl);

    const anger = document.createElement("li");
    anger.innerHTML = `angry: ${ferEvent.data.angry}`;
    dataItem.appendChild(anger);
    const happy = document.createElement("li");
    happy.innerHTML = `happy: ${ferEvent.data.happy}`;
    dataItem.appendChild(happy);
    const neutral = document.createElement("li");
    neutral.innerHTML = `neutral: ${ferEvent.data.neutral}`;
    dataItem.appendChild(neutral);
    const sad = document.createElement("li");
    sad.innerHTML = `sad: ${ferEvent.data.sad}`;
    dataItem.appendChild(sad);
    const surprise = document.createElement("li");
    surprise.innerHTML = `surprise: ${ferEvent.data.surprise}`;
    dataItem.appendChild(surprise);

    this.ferList.appendChild(dataItem);
  }
  renderSerResultEvent(serEvent) {
    const dataItem = document.createElement("ul");

    const timeEl = document.createElement("li");
    timeEl.innerHTML = `--- ${serEvent.time} ---`;
    dataItem.appendChild(timeEl);

    const neutral = document.createElement("li");
    neutral.innerHTML = `neutral: ${serEvent.data.neutral}`;
    dataItem.appendChild(neutral);
    const happy = document.createElement("li");
    happy.innerHTML = `happy: ${serEvent.data.happy}`;
    dataItem.appendChild(happy);
    const sad = document.createElement("li");
    sad.innerHTML = `sad: ${serEvent.data.sad}`;
    dataItem.appendChild(sad);
    const anger = document.createElement("li");
    anger.innerHTML = `anger: ${serEvent.data.angry}`;
    dataItem.appendChild(anger);
    const surprise = document.createElement("li");
    surprise.innerHTML = `surprise: ${serEvent.data.surprise}`;
    dataItem.appendChild(surprise);

    this.serList.appendChild(dataItem);
  }
}
