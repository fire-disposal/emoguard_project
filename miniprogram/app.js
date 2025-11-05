// app.js
const auth = require('./utils/auth');
const userApi = require('./api/user');

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
   * 检查登录状态和信息完善状态
   */
  async checkAuth() {
    // 防止重复请求用户信息
    if (this._checkingUserInfo) {
      console.log('正在检查用户信息，跳过本次调用');
      return;
    }
    this._checkingUserInfo = true;

    const pages = getCurrentPages();
    if (pages.length === 0) {
      this._checkingUserInfo = false;
      return;
    }
    
    const currentPage = pages[pages.length - 1];
    const route = currentPage.route;
    
    // 登录页和信息完善页不需要检查
    if (route === 'pages/login/login' || route === 'pages/profile/complete/complete') {
      this._checkingUserInfo = false;
      return;
    }
    
    // 检查是否登录
    if (!auth.isLogined()) {
      console.log('未登录，跳转登录页');
      auth.navigateToLogin(route);
      this._checkingUserInfo = false;
      return;
    }
    
    // 检查信息是否完善
    try {
      const userInfo = this.globalData.userInfo;
      if (userInfo && !userInfo.is_profile_complete) {
        console.log('用户信息未完善，跳转信息完善页面');
        wx.reLaunch({
          url: '/pages/profile/complete/complete'
        });
        this._checkingUserInfo = false;
        return;
      }
      
      // 如果本地没有用户信息或信息不完整，从服务器获取
      if (!userInfo || userInfo.is_profile_complete === undefined) {
        const freshUserInfo = await userApi.getCurrentUser();
        this.globalData.userInfo = freshUserInfo;
        
        if (!freshUserInfo.is_profile_complete) {
          console.log('用户信息未完善，跳转信息完善页面');
          wx.reLaunch({
            url: '/pages/profile/complete/complete'
          });
        }
      }
    } catch (error) {
      console.error('检查用户信息失败:', error);
      // 如果检查失败，允许用户继续使用，避免阻塞
    }
    this._checkingUserInfo = false;
  }
});
