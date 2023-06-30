import { Chart } from "chart.js/auto";

export default class TiltCharts {
  private pulseTimestamps = [];
  private ferTimestamps = [];
  private serTimestamps = [];

  private pulseHeartRateData = [];
  private ferResultData = {
    neutral: [],
    happy: [],
    sad: [],
    angry: [],
    surprise: [],
  };

  private serResultData = {
    neutral: [],
    happy: [],
    sad: [],
    angry: [],
    surprise: [],
  };

  // limit graph-rendering to once every ... secs
  private renderFrequency = 5;
  private lastPulseRender = Date.now() - this.renderFrequency * 1000;
  private lastFerRender = Date.now() - this.renderFrequency * 1000;
  private lastSerRender = Date.now() - this.renderFrequency * 1000;

  private pulseChartData = {
    labels: [],
    datasets: [
      {
        label: "Pulse",
        data: [],
        fill: false,
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1,
      },
    ],
  };

  private ferChartData = {
    labels: [],
    datasets: [
      {
        label: "Angry",
        data: [],
        fill: false,
        borderColor: "#e49376",
        tension: 0.1,
      },
      {
        label: "Sad",
        data: [],
        fill: false,
        borderColor: "orange",
        tension: 0.1,
      },
      {
        label: "Neutral",
        data: [],
        fill: false,
        borderColor: "#fff589",
        tension: 0.1,
      },
      {
        label: "Surprise",
        data: [],
        fill: false,
        borderColor: "silver",
        tension: 0.1,
      },
      {
        label: "Happy",
        data: [],
        fill: false,
        borderColor: "rgb(125, 203, 119)",
        tension: 0.1,
      },
    ],
  };

  private serChartData = {
    labels: [],
    datasets: [
      {
        label: "Angry",
        data: [],
        fill: false,
        borderColor: "#e49376",
        tension: 0.1,
      },
      {
        label: "Sad",
        data: [],
        fill: false,
        borderColor: "orange",
        tension: 0.1,
      },
      {
        label: "Neutral",
        data: [],
        fill: false,
        borderColor: "#fff589",
        tension: 0.1,
      },
      {
        label: "Surprised",
        data: [],
        fill: false,
        borderColor: "silver",
        tension: 0.1,
      },
      {
        label: "Happy",
        data: [],
        fill: false,
        borderColor: "rgb(125, 203, 119)",
        tension: 0.1,
      },
    ],
  };

  private pulseChart;
  private ferChart;
  private serChart;

  constructor(
    pulseChartCanvas: HTMLCanvasElement,
    ferChartCanvas: HTMLCanvasElement,
    serChartCanvas: HTMLCanvasElement
  ) {
    const pulseChartConfig = {
      type: "line",
      data: this.pulseChartData,
      options: {
        scales: {
          y: {
            beginAtZero: true,
            suggestedMax: 110,
          },
        },
      },
    };
    const ferChartConfig = {
      type: "line",
      data: this.ferChartData,
      options: {
        scales: {
          y: {
            beginAtZero: true,
            suggestedMax: 1,
          },
        },
      },
    };
    const serChartConfig = {
      type: "line",
      data: this.serChartData,
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
    this.pulseChart = new Chart(pulseChartCanvas, pulseChartConfig);
    // @ts-ignore
    this.ferChart = new Chart(ferChartCanvas, ferChartConfig);
    // @ts-ignore
    this.serChart = new Chart(serChartCanvas, serChartConfig);
  }

  updatePulseGraph(heartRate, timestamp) {
    const timeNow = Date.now();
    if ((timeNow - this.lastPulseRender) / 1000 >= this.renderFrequency) {
      this.pulseHeartRateData.push(parseInt(heartRate));
      this.pulseTimestamps.push(timestamp);
      this.pulseChart.data.datasets[0].data = this.pulseHeartRateData;
      this.pulseChart.data.labels = this.pulseTimestamps;
      this.pulseChart.update();
      // update last rendering timestamp
      this.lastPulseRender = timeNow;
    }
  }
  updateFerGraph(ferData, timestamp) {
    const timeNow = Date.now();
    if (!((timeNow - this.lastFerRender) / 1000 >= this.renderFrequency))
      return;

    this.ferResultData.angry.push(ferData.angry);
    this.ferResultData.happy.push(ferData.happy);
    this.ferResultData.neutral.push(ferData.neutral);
    this.ferResultData.sad.push(ferData.sad);
    this.ferResultData.surprise.push(ferData.surprise);
    this.ferTimestamps.push(timestamp);
    this.ferChart.data.datasets[0].data = this.ferResultData.angry;
    this.ferChart.data.datasets[1].data = this.ferResultData.sad;
    this.ferChart.data.datasets[2].data = this.ferResultData.neutral;
    this.ferChart.data.datasets[3].data = this.ferResultData.surprise;
    this.ferChart.data.datasets[4].data = this.ferResultData.happy;
    this.ferChart.data.labels = this.ferTimestamps;
    this.ferChart.update();
    // update last rendering timestamp
    this.lastFerRender = timeNow;
  }
  updateSerGraph(serData, timestamp) {
    console.log("SER GRAPH update");
    console.log(serData);
    const timeNow = Date.now();
    if (!((timeNow - this.lastSerRender) / 1000 >= this.renderFrequency))
      return;

    this.serResultData.neutral.push(serData.neutral);
    this.serResultData.happy.push(serData.happy);
    this.serResultData.sad.push(serData.sad);
    this.serResultData.angry.push(serData.angry);
    this.serResultData.surprise.push(serData.surprise);

    this.serTimestamps.push(timestamp);

    this.serChart.data.datasets[0].data = this.serResultData.angry;
    this.serChart.data.datasets[1].data = this.serResultData.sad;
    this.serChart.data.datasets[2].data = this.serResultData.neutral;
    this.serChart.data.datasets[3].data = this.serResultData.surprise;
    this.serChart.data.datasets[4].data = this.serResultData.happy;
    this.serChart.data.labels = this.serTimestamps;
    this.serChart.update();
    // update last rendering timestamp
    this.lastSerRender = timeNow;
  }
}
