import * as echarts from '../../../ec-canvas/echarts';
const emotionApi = require('../../../api/emotiontracker');
const app = getApp();

function formatDateMD(dateStr) {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function initChart(canvas, width, height, dpr) {
  const chart = echarts.init(canvas, null, { width, height, devicePixelRatio: dpr });
  canvas.setChart(chart);

  const option = {
    backgroundColor: 'transparent',
    legend: {
      data: ['抑郁', '焦虑', '精力', '睡眠'],
      top: 35,
      left: 'center',
      orient: 'horizontal',
      textStyle: { fontSize: 12, color: '#666' }
    },
    grid: {
      containLabel: true,
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: 85
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#4facfe',
      borderWidth: 1,
      textStyle: { color: '#333', fontSize: 12 }
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [],
      axisLabel: {
        rotate: 45,
        fontSize: 10,
        color: '#666'
      },
      axisLine: { lineStyle: { color: '#e0e0e0' } }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 10,
      axisLabel: { fontSize: 10, color: '#666' },
      axisLine: { lineStyle: { color: '#e0e0e0' } },
      splitLine: { lineStyle: { type: 'dashed', color: '#f0f0f0' } }
    },
    series: []
  };

  chart.setOption(option);
  return chart;
}

Page({
  data: {
    ec: { onInit: initChart },
    trendData: null,
    loading: true,
    timeRange: 30,
    timeRanges: [
      { value: 7, label: '7天' },
      { value: 30, label: '30天' },
      { value: 90, label: '90天' }
    ],
    historyRecords: []
  },

  onLoad() {
    this.loadEmotionTrend();
  },

  async loadEmotionTrend() {
    try {
      this.setData({ loading: true });
      const trendData = await emotionApi.getEmotionTrend(this.data.timeRange);

      if (!trendData || !Array.isArray(trendData.dates)) {
        throw new Error('数据格式错误');
      }

      const formattedDates = trendData.dates.map(formatDateMD);

      // 构建历史记录数据
      const historyRecords = this.buildHistoryRecords(trendData);

      this.setData({
        trendData: { ...trendData, dates: formattedDates },
        historyRecords: historyRecords,
        loading: false
      });

      setTimeout(() => this.updateChart(), 150);
    } catch (error) {
      this.setData({ loading: false });

      wx.showToast({
        title: '加载失败',
        icon: 'none',
        duration: 2000
      });
    }
  },

  updateChart() {
    const ecComponent = this.selectComponent('#mychart-dom-line');
    if (!ecComponent || !ecComponent.chart || !this.data.trendData) return;

    const chart = ecComponent.chart;
    const data = this.data.trendData;

    const seriesBase = [
      { key: 'depression', name: '抑郁', color: '#ff7875' },
      { key: 'anxiety', name: '焦虑', color: '#ffa940' },
      { key: 'energy', name: '精力', color: '#52c41a' },
      { key: 'sleep', name: '睡眠', color: '#1890ff' }
    ];

    const chosen = seriesBase;

    const series = chosen.map(s => ({
      name: s.name,
      type: 'line',
      smooth: true,
      data: data[s.key] || [],
      lineStyle: { color: s.color, width: 3 },
      itemStyle: { color: s.color, borderWidth: 1 }
    }));

    chart.setOption({
      legend: { data: chosen.map(s => s.name) },
      xAxis: { data: data.dates },
      series
    });
  },

  onTimeRangeChange(e) {
    const range = Number(e.currentTarget.dataset.range);
    this.setData({ timeRange: range }, () => this.loadEmotionTrend());
  },
  
  onRefresh() {
    this.loadEmotionTrend();
  },

  showAdvice() {
    wx.showModal({
      title: '健康提示',
      content: '请保持规律作息和良好心态，如有需要可咨询专业人士。',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  // 构建历史记录数据
  buildHistoryRecords(trendData) {
    if (!trendData || !trendData.dates || !Array.isArray(trendData.dates)) {
      return [];
    }

    const records = [];
    const { dates, depression, anxiety, energy, sleep } = trendData;

    for (let i = 0; i < dates.length; i++) {
      const record = {
        date: dates[i],
        formattedDate: formatDateMD(dates[i]),
        depression: depression[i] || 0,
        anxiety: anxiety[i] || 0,
        energy: energy[i] || 0,
        sleep: sleep[i] || 0
      };
      records.push(record);
    }

    // 按日期倒序排列（最新的在前）
    return records.reverse();
  }
});
