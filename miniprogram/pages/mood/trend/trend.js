import * as echarts from '../../../ec-canvas/echarts';
const emotionApi = require('../../../api/emotiontracker');
const app = getApp();

function formatDateMD(dateStr) {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function formatDateFull(dateStr) {
  const d = new Date(dateStr);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
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
    historyRecords: [],
    // 新增：数据统计信息
    stats: {
      avgDepression: 0,
      avgAnxiety: 0,
      avgEnergy: 0,
      avgSleep: 0,
      trendDepression: 'stable',
      trendAnxiety: 'stable',
      trendEnergy: 'stable',
      trendSleep: 'stable'
    }
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

      // 构建历史记录数据，确保数据完整性
      const historyRecords = this.buildHistoryRecords(trendData);

      // 计算统计数据和趋势
      const stats = this.calculateStats(trendData);

      this.setData({
        trendData: { ...trendData, dates: formattedDates },
        historyRecords: historyRecords,
        stats: stats,
        loading: false
      });

      // 延迟更新图表，确保DOM已渲染
      setTimeout(() => this.updateChart(), 200);
    } catch (error) {
      console.error('加载情绪趋势数据失败:', error);
      this.setData({
        loading: false,
        trendData: null,
        historyRecords: [],
        stats: {
          avgDepression: 0,
          avgAnxiety: 0,
          avgEnergy: 0,
          avgSleep: 0,
          trendDepression: 'stable',
          trendAnxiety: 'stable',
          trendEnergy: 'stable',
          trendSleep: 'stable'
        }
      });

      wx.showToast({
        title: '加载失败，请重试',
        icon: 'none',
        duration: 2000
      });
    }
  },

  updateChart() {
    try {
      const ecComponent = this.selectComponent('#mychart-dom-line');
      if (!ecComponent || !ecComponent.chart || !this.data.trendData) {
        console.warn('图表组件未准备好或数据缺失');
        return;
      }

      const chart = ecComponent.chart;
      const data = this.data.trendData;

      // 确保数据数组存在且长度一致
      if (!data.dates || !Array.isArray(data.dates) || data.dates.length === 0) {
        console.warn('日期数据无效');
        return;
      }

      const seriesBase = [
        { key: 'depression', name: '抑郁', color: '#ff7875' },
        { key: 'anxiety', name: '焦虑', color: '#ffa940' },
        { key: 'energy', name: '精力', color: '#52c41a' },
        { key: 'sleep', name: '睡眠', color: '#1890ff' }
      ];

      const chosen = seriesBase;
      
      // 过滤掉数据不完整的系列
      const series = chosen.map(s => {
        const seriesData = data[s.key] || [];
        // 确保数据长度与日期长度一致，不足的用0填充
        const paddedData = seriesData.length >= data.dates.length
          ? seriesData.slice(0, data.dates.length)
          : [...seriesData, ...Array(data.dates.length - seriesData.length).fill(0)];
          
        return {
          name: s.name,
          type: 'line',
          smooth: true,
          data: paddedData,
          lineStyle: { color: s.color, width: 3 },
          itemStyle: { color: s.color, borderWidth: 1 }
        };
      });

      chart.setOption({
        legend: { data: chosen.map(s => s.name) },
        xAxis: { data: data.dates },
        series
      });
    } catch (error) {
      console.error('更新图表失败:', error);
    }
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

  // 计算统计数据和趋势
  calculateStats(trendData) {
    if (!trendData || !trendData.dates || trendData.dates.length === 0) {
      return {
        avgDepression: 0,
        avgAnxiety: 0,
        avgEnergy: 0,
        avgSleep: 0,
        trendDepression: 'stable',
        trendAnxiety: 'stable',
        trendEnergy: 'stable',
        trendSleep: 'stable'
      };
    }

    const { dates, depression = [], anxiety = [], energy = [], sleep = [] } = trendData;
    
    // 过滤掉0值（表示无数据的日期）
    const validDepression = depression.filter(v => v > 0);
    const validAnxiety = anxiety.filter(v => v > 0);
    const validEnergy = energy.filter(v => v > 0);
    const validSleep = sleep.filter(v => v > 0);

    // 计算平均值
    const avgDepression = validDepression.length > 0 ?
      Math.round(validDepression.reduce((a, b) => a + b, 0) / validDepression.length) : 0;
    const avgAnxiety = validAnxiety.length > 0 ?
      Math.round(validAnxiety.reduce((a, b) => a + b, 0) / validAnxiety.length) : 0;
    const avgEnergy = validEnergy.length > 0 ?
      Math.round(validEnergy.reduce((a, b) => a + b, 0) / validEnergy.length) : 0;
    const avgSleep = validSleep.length > 0 ?
      Math.round(validSleep.reduce((a, b) => a + b, 0) / validSleep.length) : 0;

    // 计算趋势（基于最近7天数据）
    const trendWindow = Math.min(7, dates.length);
    const recentStart = Math.max(0, dates.length - trendWindow);
    
    const calcTrend = (data, validData) => {
      if (validData.length < trendWindow * 0.5) return 'stable'; // 数据不足
      
      const recent = data.slice(recentStart).filter(v => v > 0);
      const older = data.slice(Math.max(0, recentStart - trendWindow), recentStart).filter(v => v > 0);
      
      if (recent.length === 0 || older.length === 0) return 'stable';
      
      const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
      const olderAvg = older.reduce((a, b) => a + b, 0) / older.length;
      
      const diff = recentAvg - olderAvg;
      if (Math.abs(diff) < 0.5) return 'stable';
      return diff > 0 ? 'up' : 'down';
    };

    return {
      avgDepression,
      avgAnxiety,
      avgEnergy,
      avgSleep,
      trendDepression: calcTrend(depression, validDepression),
      trendAnxiety: calcTrend(anxiety, validAnxiety),
      trendEnergy: calcTrend(energy, validEnergy),
      trendSleep: calcTrend(sleep, validSleep)
    };
  },

  // 构建历史记录数据
  buildHistoryRecords(trendData) {
    if (!trendData || !trendData.dates || !Array.isArray(trendData.dates)) {
      return [];
    }

    const records = [];
    const { dates, depression = [], anxiety = [], energy = [], sleep = [] } = trendData;

    for (let i = 0; i < dates.length; i++) {
      try {
        const record = {
          date: dates[i],
          formattedDate: formatDateMD(dates[i]),
          fullDate: formatDateFull(dates[i]),
          depression: depression[i] || 0,
          anxiety: anxiety[i] || 0,
          energy: energy[i] || 0,
          sleep: sleep[i] || 0,
          hasData: depression[i] > 0 || anxiety[i] > 0 || energy[i] > 0 || sleep[i] > 0
        };
        records.push(record);
      } catch (error) {
        console.warn(`处理第${i}条记录时出错:`, error);
        continue;
      }
    }

    // 按日期倒序排列（最新的在前）
    return records.reverse();
  }
});
