const auth = require('../../utils/auth');
const emotionApi = require('../../api/emotiontracker');
const errorUtil = require('../../utils/error');

Page({
  data: {
    currentDate: '', // 格式：2023年10月26日 星期四
    currentTime: '', // 格式：14:30
    userNickname: '',
    currentPeriod: '', // 当前时段标识: 'morning', 'afternoon', 'evening'
    currentPeriodText: '', // 当前时段中文: '早间', '下午', '晚间'
    showCognitiveGuide: false, // 是否显示认知评估引导卡片
    hasCompletedAssessment: false, // 是否已完成认知评估
    morningFilled: false, // 早上情绪记录是否已填写
    eveningFilled: false // 晚上情绪记录是否已填写
  },

  onShow() {
    // 统一调用全局防抖鉴权检查
    getApp().debouncedCheckAuth();
    // 页面显示时加载情绪状态（从其他页面返回时会触发）
    this.loadEmotionStatus();
  },

  onLoad() {
    this.getCurrentDate();
    this.loadUserInfo();

    // 初始化时间/时段并设置定时器
    this.updateTimeAndPeriod();
    this.loadEmotionStatus();

    // 每分钟更新时间
    this.timer = setInterval(() => {
      this.updateTimeAndPeriod();
    }, 60000);
  },

  onUnload() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  },

  /**
   * 加载今日情绪记录状态
   */
  loadEmotionStatus() {
    emotionApi.getTodayStatus().then(res => {
      console.log('获取今日状态成功:', res);
      this.setData({
        morningFilled: !!res.morning_filled,
        eveningFilled: !!res.evening_filled
      });
    }).catch((error) => {
      errorUtil.handleError(error);
      // 获取失败时，默认设置为未完成，避免前端逻辑错误
      this.setData({
        morningFilled: false,
        eveningFilled: false
      });
      console.log('获取今日状态失败，使用默认状态: 均未完成');
    });
  },

  /**
   * 获取当前日期
   */
  getCurrentDate() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    const day = now.getDate();
    const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
    const weekday = weekdays[now.getDay()];

    this.setData({
      currentDate: `${year}年${month}月${day}日 ${weekday}`
    });
  },

  /**
   * 更新当前时间和时段
   */
  updateTimeAndPeriod() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');

    let period = '';
    let periodText = '';

    // 时段划分逻辑：
    if (hours >= 5 && hours < 12) {
      period = 'morning'; // 5:00 - 11:59
      periodText = '早间';
    } else if (hours >= 12 && hours < 18) {
      period = 'afternoon'; // 12:00 - 17:59
      periodText = '下午';
    } else {
      period = 'evening'; // 18:00 - 4:59 (晚间/夜间)
      periodText = '晚间';
    }

    this.setData({
      currentTime: `${hours}:${minutes}`,
      currentPeriod: period,
      currentPeriodText: periodText
    });
  },

  /**
   * 加载用户信息
   */
  async loadUserInfo() {
    let userInfo = getApp().globalData.userInfo;
    if (!userInfo || userInfo.is_profile_complete === undefined) {
      // 若无全局用户信息则异步获取
      userInfo = await getApp().getUserInfoAsync();
    }

    // 检查是否完成认知评估
    const hasCompleted = userInfo?.has_completed_cognitive_assessment || false;

    this.setData({
      userNickname: userInfo?.nickname || '用户',
      hasCompletedAssessment: hasCompleted,
      // 仅在未完成评估时显示引导
      showCognitiveGuide: !hasCompleted
    });
  },

  /**
   * 跳转到情绪记录
   */
  goToMoodRecord() {
    wx.switchTab({ url: '/pages/mood/journal/journal' });
  },

  /**
   * 跳转到测评页面
   */
  goToAssessment() {
    wx.navigateTo({ url: '/pages/assessment/select/select' });
  },

  /**
   * 跳转到文章列表
   */
  goToArticles() {
    wx.navigateTo({ url: '/pages/articles/list/list' });
  },

  /**
   * 跳转到健康报告
   */
  goToReports() {
    wx.navigateTo({ url: '/pages/reports/list/list' });
  },

  /**
   * 跳转到情绪测试
   * @param {Object} e - 事件对象，dataset.period 可用于指定早间/晚间
   */
  goToEmotionTest(e) {
    const period = e?.currentTarget?.dataset?.period || this.data.currentPeriod;
    const isEveningRecord = period === 'evening';
    const now = new Date();
    const hours = now.getHours();

    // 强制限制：晚间记录须在 14:00 (下午两点) 之后填写
    if (isEveningRecord && hours < 14) {
      wx.showToast({
        title: '晚间记录请于 14:00 后填写',
        icon: 'none'
      });
      return;
    }

    const isFilled = (period === 'morning' && this.data.morningFilled) ||
      (period === 'evening' && this.data.eveningFilled);

    if (isFilled) {
      // 已填写，弹窗确认是否重测
      wx.showModal({
        title: '提示',
        content: '您已完成本次情绪测试，是否重新测试？',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({
              url: `/pages/mood/moodtest/moodtest?period=${period}`
            });
          }
        }
      });
    } else {
      // 未填写，直接跳转
      wx.navigateTo({
        url: `/pages/mood/moodtest/moodtest?period=${period}`
      });
    }
  },

  /**
   * 开始认知评估流程 - 直接跳转到智能测评
   */
  startCognitiveFlow() {
    wx.navigateTo({
      url: '/pages/assessment/flow/flow'
    });
  },

  /**
   * 关闭引导卡片
   */
  closeCognitiveGuide() {
    this.setData({
      showCognitiveGuide: false
    });
  }
});