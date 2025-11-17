// pages/profile/index/index.js
const userApi = require('../../../api/user');
const auth = require('../../../utils/auth');

Page({
  data: {
    userInfo: null,
    loading: true
  },

  onShow() {
    if (!auth.isLogined()) {
      auth.navigateToLogin();
      return;
    }
    // 仅主页展示昵称，无需每次都加载详细信息
    userApi.getCurrentUser()
      .then((res) => {
        this.setData({
          userInfo: res,
          loading: false
        });
      })
      .catch(() => {
        this.setData({ loading: false });
      });
  },

  /**
   * 跳转到个人信息页面
   */
  // 合并后的个人信息管理入口
  goToProfileManage() {
    wx.navigateTo({
      url: '/pages/profile/userinfo/userinfo'
    });
  },

  onLoad() {
    // 仅首次进入加载一次
    userApi.getCurrentUser()
      .then((res) => {
        this.setData({
          userInfo: res,
          loading: false
        });
      })
      .catch(() => {
        this.setData({ loading: false });
      });
  },


  /**
   * 加载用户信息
   */
  // 主页无需详细资料编辑功能，loadUserInfo 可移除


  /**
   * 跳转到反馈页面
   */
  goToProfileManage(){
    wx.navigateTo({
      url: '/pages/profile/userinfo/userinfo'
    });
  },

  goToFeedback() {
    wx.navigateTo({
      url: '/pages/feedback/feedback'
    });
  },

  goToAbout() {
    wx.navigateTo({
      url: '/pages/agreement/about/about'
    });
  },

  goToPrivacyPolicy() {
    wx.navigateTo({
      url: '/pages/agreement/privacy-policy/privacy-policy'
    });
  },

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
          auth.logout();
        }
      }
    });
  },
  /**
   * 关于弹窗
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
  }
});
