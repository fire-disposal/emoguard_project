// pages/profile/index/index.js
const userApi = require('../../../api/user');
const authCenter = require('../../../utils/authCenter');

Page({
  data: {
    userInfo: null,
    loading: true,
    abnormalScores: [],
    lastMoodTestedAt: null
  },

  onShow() {
    if (!authCenter.logined) {
      authCenter.logout();
      wx.reLaunch({ url: '/pages/login/login' });
      return;
    }
    this.loadUserInfo();
  },

  loadUserInfo() {
    userApi.getCurrentUser()
      .then((res) => {
        const abnormalScores = [];
        if (res.score_scd !== null && res.score_scd < 6) abnormalScores.push({
          key: 'SCD',
          label: '主观认知障碍',
          score: res.score_scd,
          desc: res.score_scd < 3 ? '高度异常' : '存在异常'
        });
        if (res.score_mmse !== null && res.score_mmse < 24) abnormalScores.push({
          key: 'MMSE',
          label: '简易精神状态检查',
          score: res.score_mmse,
          desc: res.score_mmse < 18 ? '重度异常' : '存在异常'
        });
        if (res.score_moca !== null && res.score_moca < 26) abnormalScores.push({
          key: 'MoCA',
          label: '蒙特利尔认知评估',
          score: res.score_moca,
          desc: res.score_moca < 18 ? '重度异常' : '存在异常'
        });
        if (res.score_gad7 !== null && res.score_gad7 >= 10) abnormalScores.push({
          key: 'GAD-7',
          label: '广泛性焦虑量表',
          score: res.score_gad7,
          desc: res.score_gad7 >= 15 ? '重度焦虑' : '存在焦虑'
        });
        if (res.score_phq9 !== null && res.score_phq9 >= 10) abnormalScores.push({
          key: 'PHQ-9',
          label: '抑郁自评量表',
          score: res.score_phq9,
          desc: res.score_phq9 >= 15 ? '重度抑郁' : '存在抑郁'
        });
        if (res.score_adl !== null && res.score_adl < 95) abnormalScores.push({
          key: 'ADL',
          label: '日常生活能力',
          score: res.score_adl,
          desc: res.score_adl < 80 ? '严重受损' : '轻度受损'
        });

        this.setData({
          userInfo: res,
          loading: false,
          abnormalScores,
          lastMoodTestedAt: res.last_mood_tested_at || null
        });

        if (res.last_mood_tested_at) {
          console.log('上次情绪测试时间:', res.last_mood_tested_at);
        }
      })
      .catch(() => {
        this.setData({ loading: false });
      });
  },

  /**
   * 跳转到个人信息页面
   */
  goToProfileManage() {
    wx.navigateTo({
      url: '/pages/profile/userinfo/userinfo'
    });
  },

  /**
   * 跳转到反馈页面
   */
  goToFeedback() {
    wx.navigateTo({
      url: '/pages/feedback/feedback'
    });
  },

  /**
   * 跳转到关于页面
   */
  goToAbout() {
    wx.showModal({
      title: '关于',
      content: '认知照顾情绪监测系统小程序\n版本：1.0.0\n版权所有 © 2025\n如需帮助请联系开发团队。',
      showCancel: false,
      confirmText: '知道了'
    });
  },

  /**
   * 跳转到隐私政策
   */
  goToPrivacyPolicy() {
    wx.navigateTo({
      url: '/pages/agreement/privacy-policy/privacy-policy'
    });
  },

  /**
   * 跳转到用户协议
   */
  goToUserAgreement() {
    wx.navigateTo({
      url: '/pages/agreement/user-agreement/user-agreement'
    });
  },

  /**
   * 退出登录
   */
  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          authCenter.logout();
        }
      }
    });
  }
});