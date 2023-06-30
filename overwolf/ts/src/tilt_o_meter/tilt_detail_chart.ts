import { Chart } from "chart.js/auto";

export default class TiltDetailChart {
  private detailChart;

  constructor(
    private eventList,
    private detailChartCanvas: HTMLCanvasElement
  ) {}

  renderDetailChartOfRowEl(logRowEl) {
    this.detailChartCanvas.innerHTML = "";
    if (this.detailChart) {
      this.detailChart.destroy();
    }

    const eventId = logRowEl.getAttribute("data-event-id");
    const eventObj = this.eventList[eventId];

    const datasetLabel = `${eventObj.type.toUpperCase()} event - ID: ${
      eventObj.id
    } - Time: ${eventObj.time}`;
    const eventData = eventObj.data;
    const datasetData = [
      eventData.angry,
      eventData.sad,
      eventData.neutral,
      eventData.surprise,
      eventData.happy,
    ];

    let labels = ["Angry", "Sad", "Neutral", "Surprised", "Happy"];
    let bgColors = [
      "rgba(228, 147, 118, 0.2)",
      "rgba(255, 165, 0, 0.2)",
      "rgba(1255, 245, 137, 0.2)",
      "rgba(192, 192, 192, 0.2)",
      "rgba(125, 203, 119, 0.2)",
    ];

    let bgBorders = [
      "	rgb(228, 147, 118)",
      "rgb(255, 165, 0)",
      "rgb(255, 245, 137)",
      "	rgb192, 192, 192)",
      "rgb(125, 203, 119)",
    ];

    const data = {
      labels: labels,
      datasets: [
        {
          label: datasetLabel,
          data: datasetData,
          backgroundColor: bgColors,
          borderColor: bgBorders,
          borderWidth: 1,
        },
      ],
    };

    const config = {
      type: "bar",
      data: data,
      options: {
        scales: {
          y: {
            beginAtZero: true,
            suggestedMax: 1,
          },
        },
      },
    };
    // @ts-ignore
    this.detailChart = new Chart(this.detailChartCanvas, config);
    // }
  }
}
