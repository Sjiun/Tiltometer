import * as echarts from "echarts";

export default class TiltOMeter {
  private tiltGauge;
  private gaugeOption;

  constructor(tiltOMeterWrapperDiv: HTMLDivElement) {
    this.tiltGauge = echarts.init(tiltOMeterWrapperDiv);

    this.gaugeOption = {
      title: {
        left: "center",
      },
      series: [
        {
          type: "gauge",
          startAngle: 180,
          endAngle: 0,
          max: 1,
          min: -1,
          progress: {
            show: false,
            width: 10,
          },
          axisLine: {
            roundCap: true,
            lineStyle: {
              width: 10,
              opacity: 0,
            },
          },
          axisTick: {
            show: false,
          },
          splitLine: {
            length: 15,
            lineStyle: {
              width: 0,
              color: "#999",
            },
          },
          axisLabel: {
            show: false,
            distance: 5,
            color: "#999",
            fontSize: 14,
          },
          pointer: {
            length: "75%",
            width: 7,
            offsetCenter: [0, "0"],
            itemStyle: {
              color: "#333333",
            },
          },
          detail: {
            show: false,
            valueAnimation: true,
            fontSize: 30,
            offsetCenter: [0, "20%"],
          },
          data: [
            {
              value: -1,
            },
          ],
        },
      ],
    };

    if (this.gaugeOption && typeof this.gaugeOption === "object") {
      this.tiltGauge.setOption(this.gaugeOption, true);
    }
  }

  updateTiltValue(value) {
    this.gaugeOption.series[0].data[0].value = value;
    this.tiltGauge.setOption(this.gaugeOption);
  }
}
