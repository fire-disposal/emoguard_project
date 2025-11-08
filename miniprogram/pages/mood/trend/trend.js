import * as echarts from '../../../ec-canvas/echarts';
const emotionApi = require('../../../api/emotiontracker');

const app = getApp();

// 图表初始化函数 - 增强版本
function initChart(canvas, width, height, dpr) {
  const chart = echarts.init(canvas, null, {
    width: width,
    height: height,
    devicePixelRatio: dpr
  });
  canvas.setChart(chart);
  
  // 初始显示基础图表
  const basicOption = {
    backgroundColor: 'transparent',
    legend: {
      data: ['抑郁', '焦虑', '精力', '睡眠'],
      top: 40,
      left: 'center',
      textStyle: {
        fontSize: 12,
        color: '#666'
      }
    },
    grid: {
      containLabel: true,
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: 100
    },
    tooltip: {
      show: true,
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#4facfe',
      borderWidth: 1,
      textStyle: {
        color: '#333',
        fontSize: 12
      },
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#999'
        }
      }
    },
    toolbox: {
      show: true,
      feature: {
        dataZoom: {
          yAxisIndex: 'none'
        },
        restore: {},
        saveAsImage: {}
      },
      right: 20,
      top: 20
    },
    dataZoom: [{
      type: 'inside',
      start: 0,
      end: 100
    }, {
      start: 0,
      end: 100,
      handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
      handleSize: '80%',
      handleStyle: {
        color: '#fff',
        shadowBlur: 3,
        shadowColor: 'rgba(0, 0, 0, 0.6)',
        shadowOffsetX: 2,
        shadowOffsetY: 2
      }
    }],
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [],
      axisLabel: {
        rotate: 45,
        fontSize: 10,
        color: '#666'
      },
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 10,
      axisLabel: {
        fontSize: 10,
        color: '#666'
      },
      axisLine: {
        lineStyle: {
          color: '#e0e0e0'
        }
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#f0f0f0'
        }
      }
    },
    series: [
      {
        name: '抑郁',
        type: 'line',
        smooth: true,
        data: [],
        lineStyle: { 
          color: '#ff7875',
          width: 3
        },
        itemStyle: { 
          color: '#ff7875',
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(255, 120, 117, 0.3)'
            }, {
              offset: 1, color: 'rgba(255, 120, 117, 0.05)'
            }]
          }
        }
      },
      {
        name: '焦虑',
        type: 'line',
        smooth: true,
        data: [],
        lineStyle: { 
          color: '#ffa940',
          width: 3
        },
        itemStyle: { 
          color: '#ffa940',
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(255, 169, 64, 0.3)'
            }, {
              offset: 1, color: 'rgba(255, 169, 64, 0.05)'
            }]
          }
        }
      },
      {
        name: '精力',
        type: 'line',
        smooth: true,
        data: [],
        lineStyle: { 
          color: '#52c41a',
          width: 3
        },
        itemStyle: { 
          color: '#52c41a',
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(82, 196, 26, 0.3)'
            }, {
              offset: 1, color: 'rgba(82, 196, 26, 0.05)'
            }]
          }
        }
      },
      {
        name: '睡眠',
        type: 'line',
        smooth: true,
        data: [],
        lineStyle: { 
          color: '#1890ff',
          width: 3
        },
        itemStyle: { 
          color: '#1890ff',
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: 'rgba(24, 144, 255, 0.3)'
            }, {
              offset: 1, color: 'rgba(24, 144, 255, 0.05)'
            }]
          }
        }
      }
    ]
  };
  
  chart.setOption(basicOption);
  return chart;
}

Page({
  data: {
    ec: {
      onInit: initChart
    },
    trendData: null,
    loading: true,
    timeRange: 30,
    selectedMetric: 'all',
    
    // 简化的控制面板配置
    timeRanges: [
      { value: 7, label: '7天' },
      { value: 30, label: '30天' },
      { value: 90, label: '90天' }
    ],
    metricOptions: [
      { value: 'all', label: '全部' },
      { value: 'depression', label: '抑郁' },
      { value: 'anxiety', label: '焦虑' },
      { value: 'energy', label: '精力' },
      { value: 'sleep', label: '睡眠' }
    ]
  },

  onLoad() {
    this.loadEmotionTrend();
  },

  // 加载情绪趋势数据 - 带详细日志版本
  async loadEmotionTrend() {
    try {
      console.log('=== 开始加载情绪趋势数据 ===');
      console.log('时间范围:', this.data.timeRange, '天');
      
      this.setData({ loading: true });
      
      // 调用API获取数据
      console.log('调用API: getEmotionTrend, 参数:', { days: this.data.timeRange });
      const trendData = await emotionApi.getEmotionTrend(this.data.timeRange);
      
      console.log('API返回数据:', trendData);
      console.log('数据类型:', typeof trendData);
      console.log('数据键值:', trendData ? Object.keys(trendData) : '无数据');
      
      // 验证数据格式
      if (!trendData) {
        console.error('API返回数据为null或undefined');
        throw new Error('未获取到数据');
      }
      
      if (!trendData.dates || !Array.isArray(trendData.dates)) {
        console.error('数据格式错误: 缺少dates字段或dates不是数组');
        console.error('实际数据格式:', trendData);
        throw new Error('数据格式错误');
      }
      
      console.log('数据验证通过:');
      console.log('- 日期数量:', trendData.dates.length);
      console.log('- 抑郁数据数量:', trendData.depression ? trendData.depression.length : 0);
      console.log('- 焦虑数据数量:', trendData.anxiety ? trendData.anxiety.length : 0);
      console.log('- 精力数据数量:', trendData.energy ? trendData.energy.length : 0);
      console.log('- 睡眠数据数量:', trendData.sleep ? trendData.sleep.length : 0);
      
      this.setData({
        trendData: trendData,
        loading: false
      });
      
      console.log('数据设置完成，准备更新图表');
      
      // 延迟更新图表，确保DOM渲染完成
      setTimeout(() => {
        console.log('开始更新图表');
        this.updateChart();
      }, 200);
      
    } catch (error) {
      console.error('=== 加载情绪趋势数据失败 ===');
      console.error('错误信息:', error.message);
      console.error('错误堆栈:', error.stack);
      
      this.setData({ loading: false });
      
      // 用户友好的错误提示
      let errorMsg = '加载失败';
      if (error.message.includes('网络')) {
        errorMsg = '网络连接失败';
      } else if (error.message.includes('格式')) {
        errorMsg = '数据格式错误';
      }
      
      wx.showToast({
        title: errorMsg,
        icon: 'none',
        duration: 2000
      });
    }
  },

  // 更新图表 - 带详细日志版本
  updateChart() {
    try {
      console.log('=== 开始更新图表 ===');
      
      const ecComponent = this.selectComponent('#mychart-dom-line');
      if (!ecComponent) {
        console.error('图表组件未找到: #mychart-dom-line');
        return;
      }
      
      if (!ecComponent.chart) {
        console.error('图表对象未初始化');
        return;
      }

      const chart = ecComponent.chart;
      const data = this.data.trendData;
      
      console.log('图表组件获取成功');
      console.log('趋势数据:', data);
      
      if (!data) {
        console.error('趋势数据为空');
        return;
      }
      
      if (!data.dates || !Array.isArray(data.dates)) {
        console.error('日期数据格式错误:', data.dates);
        return;
      }
      
      if (data.dates.length === 0) {
        console.log('日期数据为空数组');
        return;
      }

      console.log('数据验证通过，准备配置图表');
      console.log('日期数量:', data.dates.length);
      console.log('抑郁数据:', data.depression);
      console.log('焦虑数据:', data.anxiety);
      console.log('精力数据:', data.energy);
      console.log('睡眠数据:', data.sleep);

      // 简化的图表配置
      const option = {
        legend: {
          data: ['抑郁', '焦虑', '精力', '睡眠'],
          top: 30
        },
        grid: {
          containLabel: true,
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: 80
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: data.dates
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 10
        },
        series: [
          {
            name: '抑郁',
            type: 'line',
            data: data.depression || [],
            lineStyle: { color: '#ff7875' },
            itemStyle: { color: '#ff7875' }
          },
          {
            name: '焦虑',
            type: 'line',
            data: data.anxiety || [],
            lineStyle: { color: '#ffa940' },
            itemStyle: { color: '#ffa940' }
          },
          {
            name: '精力',
            type: 'line',
            data: data.energy || [],
            lineStyle: { color: '#52c41a' },
            itemStyle: { color: '#52c41a' }
          },
          {
            name: '睡眠',
            type: 'line',
            data: data.sleep || [],
            lineStyle: { color: '#1890ff' },
            itemStyle: { color: '#1890ff' }
          }
        ]
      };

      console.log('图表配置完成，开始设置选项');
      chart.setOption(option);
      console.log('=== 图表更新成功 ===');
      
    } catch (error) {
      console.error('=== 图表更新失败 ===');
      console.error('错误信息:', error.message);
      console.error('错误堆栈:', error.stack);
    }
  },

  // 获取过滤后的系列数据 - 简化版本
  getFilteredSeries() {
    const data = this.data.trendData;
    const allSeries = [
      {
        name: '抑郁',
        type: 'line',
        data: data.depression || [],
        lineStyle: { color: '#ff7875' },
        itemStyle: { color: '#ff7875' }
      },
      {
        name: '焦虑',
        type: 'line',
        data: data.anxiety || [],
        lineStyle: { color: '#ffa940' },
        itemStyle: { color: '#ffa940' }
      },
      {
        name: '精力',
        type: 'line',
        data: data.energy || [],
        lineStyle: { color: '#52c41a' },
        itemStyle: { color: '#52c41a' }
      },
      {
        name: '睡眠',
        type: 'line',
        data: data.sleep || [],
        lineStyle: { color: '#1890ff' },
        itemStyle: { color: '#1890ff' }
      }
    ];

    if (this.data.selectedMetric === 'all') {
      return allSeries;
    }
    
    // 简单的指标过滤
    const metricMap = {
      'depression': '抑郁',
      'anxiety': '焦虑',
      'energy': '精力',
      'sleep': '睡眠'
    };
    
    return allSeries.filter(series => series.name === metricMap[this.data.selectedMetric]);
  },

  // 时间范围选择
  onTimeRangeChange(e) {
    const range = parseInt(e.currentTarget.dataset.range);
    this.setData({ timeRange: range }, () => {
      this.loadEmotionTrend();
    });
  },

  // 指标选择
  onMetricSelect(e) {
    const metric = e.currentTarget.dataset.metric;
    this.setData({ selectedMetric: metric }, () => {
      this.updateChart();
    });
  },

  // 刷新数据
  onRefresh() {
    this.loadEmotionTrend();
  },

  // 显示建议 - 最简化版本
  showAdvice() {
    wx.showModal({
      title: '健康提示',
      content: '请保持规律的作息和良好的心态，如有需要可咨询专业人士。',
      showCancel: false,
      confirmText: '知道了'
    });
  },
});
