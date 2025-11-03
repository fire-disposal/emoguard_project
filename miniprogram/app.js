// app.js
const auth = require('./utils/auth');

App({
  globalData: {
    userInfo: null,
    token: null,
    refreshToken: null,
    systemInfo: null
  },

  onLaunch() {
    console.log('小程序启动');
    
    // 获取系统信息
    this.globalData.systemInfo = wx.getSystemInfoSync();
    
    // 从本地存储恢复用户信息和 token
    const userInfo = auth.getUserInfo();
    const token = auth.getToken();
    const refreshToken = auth.getRefreshToken();
    
    if (userInfo) {
      this.globalData.userInfo = userInfo;
    }
    if (token) {
      this.globalData.token = token;
    }
    if (refreshToken) {
      this.globalData.refreshToken = refreshToken;
    }
    
    console.log('登录状态:', auth.isLogined());
  },

  onShow() {
    // 检查登录状态
    this.checkAuth();
  },

  /**
   * 检查登录状态
   */
  checkAuth() {
    const pages = getCurrentPages();
    if (pages.length === 0) return;
    
    const currentPage = pages[pages.length - 1];
    const route = currentPage.route;
    
    // 登录页不需要检查
    if (route === 'pages/login/login') return;
    
    // 检查是否登录
    if (!auth.isLogined()) {
      console.log('未登录，跳转登录页');
      auth.navigateToLogin(route);
    }
  }
});
