// 趋势变化页面
Page({
  data: {
    activeTab: 'mood',
    // 心情数据
    moodData: [
      { date: '2024-01-01', score: 7, label: '很好' },
      { date: '2024-01-02', score: 6, label: '良好' },
      { date: '2024-01-03', score: 5, label: '一般' },
      { date: '2024-01-04', score: 8, label: '很好' },
      { date: '2024-01-05', score: 4, label: '较差' },
      { date: '2024-01-06', score: 7, label: '很好' },
      { date: '2024-01-07', score: 6, label: '良好' }
    ],
    // 焦虑数据
    anxietyData: [
      { date: '2024-01-01', score: 8, level: '轻度' },
      { date: '2024-01-03', score: 12, level: '中度' },
      { date: '2024-01-05', score: 6, level: '正常' },
      { date: '2024-01-07', score: 9, level: '轻度' }
    ],
    // 精力数据
    energyData: [
      { date: '2024-01-01', level: 4, status: '良好' },
      { date: '2024-01-02', level: 3, status: '一般' },
      { date: '2024-01-03', level: 5, status: '充沛' },
      { date: '2024-01-04', level: 4, status: '良好' },
      { date: '2024-01-05', level: 2, status: '不足' },
      { date: '2024-01-06', level: 4, status: '良好' },
      { date: '2024-01-07', level: 5, status: '充沛' }
    ],
    // 睡眠数据
    sleepData: [
      { date: '2024-01-01', hours: 7.5, quality: '良好' },
      { date: '2024-01-02', hours: 6.5, quality: '一般' },
      { date: '2024-01-03', hours: 8.0, quality: '很好' },
      { date: '2024-01-04', hours: 7.0, quality: '良好' },
      { date: '2024-01-05', hours: 5.5, quality: '较差' },
      { date: '2024-01-06', hours: 7.5, quality: '良好' },
      { date: '2024-01-07', hours: 8.0, quality: '很好' }
    ],
    // 统计数据
    moodAverage: '6.1',
    moodMax: '8',
    moodMin: '4',
    currentAnxietyStatus: { text: '轻度关注', class: 'status-mild' },
    anxietyTrend: { text: '趋于稳定', class: 'status-stable' },
    energyAverage: '3.9',
    currentEnergyStatus: '良好',
    energyAdvice: '保持规律作息',
    sleepAverage: '7.1',
    sleepQuality: '良好',
    sleepAdvice: '保持规律'
  },

  onLoad() {
    this.calculateStatistics();
  },

  // 切换标签页
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ activeTab: tab });
  },

  // 计算统计数据
  calculateStatistics() {
    // 计算心情统计
    const moodScores = this.data.moodData.map(item => item.score);
    const moodAvg = (moodScores.reduce((a, b) => a + b, 0) / moodScores.length).toFixed(1);
    const moodMax = Math.max(...moodScores);
    const moodMin = Math.min(...moodScores);
    
    // 计算精力统计
    const energyLevels = this.data.energyData.map(item => item.level);
    const energyAvg = (energyLevels.reduce((a, b) => a + b, 0) / energyLevels.length).toFixed(1);
    
    // 计算睡眠统计
    const sleepHours = this.data.sleepData.map(item => item.hours);
    const sleepAvg = (sleepHours.reduce((a, b) => a + b, 0) / sleepHours.length).toFixed(1);
    
    this.setData({
      moodAverage: moodAvg,
      moodMax: moodMax,
      moodMin: moodMin,
      energyAverage: energyAvg,
      sleepAverage: sleepAvg
    });
  },

  // 获取心情颜色
  getMoodColor(score) {
    if (score >= 7) return '#4CAF50';
    if (score >= 5) return '#FFC107';
    return '#F44336';
  },

  // 获取焦虑等级颜色
  getAnxietyColor(level) {
    const colors = {
      '正常': '#4CAF50',
      '轻度': '#FFC107',
      '中度': '#FF9800',
      '重度': '#F44336'
    };
    return colors[level] || '#999';
  },

  // 获取精力等级颜色
  getEnergyColor(level) {
    const colors = {
      5: '#4CAF50', // 充沛
      4: '#8BC34A', // 良好
      3: '#FFC107', // 一般
      2: '#FF9800', // 不足
      1: '#F44336'  // 很差
    };
    return colors[level] || '#999';
  },

  // 获取睡眠质量颜色
  getSleepColor(quality) {
    const colors = {
      '很好': '#4CAF50',
      '良好': '#8BC34A',
      '一般': '#FFC107',
      '较差': '#FF9800',
      '很差': '#F44336'
    };
    return colors[quality] || '#999';
  },

  // 查看详细报告
  viewDetailReport() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  // 分享趋势
  shareTrends() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    });
  },

  onShareAppMessage() {
    return {
      title: '我的情绪趋势变化',
      path: '/pages/trends/index/index',
      imageUrl: '/assets/share/trends-share.png'
    };
  }
});