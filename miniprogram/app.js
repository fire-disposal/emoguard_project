// app.js
const auth = require('./utils/auth');
const storage = require('./utils/storage');
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
    
    // 本地恢复流程更健壮，单独捕获每项异常，避免全局阻断
    let userInfo = null, token = null, refreshToken = null;
    try {
      userInfo = auth.getUserInfo();
      if (userInfo) this.globalData.userInfo = userInfo;
    } catch (error) {
      console.warn('恢复用户信息失败:', error);
    }
    try {
      token = storage.getToken();
      if (token) this.globalData.token = token;
    } catch (error) {
      console.warn('恢复token失败:', error);
    }
    try {
      refreshToken = storage.getRefreshToken();
      if (refreshToken) this.globalData.refreshToken = refreshToken;
    } catch (error) {
      console.warn('恢复refreshToken失败:', error);
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

    try {
      const pages = getCurrentPages();
      if (pages.length === 0) {
        return;
      }
      
      const currentPage = pages[pages.length - 1];
      const route = currentPage.route;
      
      // 登录页和信息完善页不需要检查
      if (route === 'pages/login/login' || route === 'pages/profile/complete/complete') {
        return;
      }
      
      // 检查是否登录
      if (!auth.isLogined()) {
        console.log('未登录，跳转登录页');
        auth.navigateToLogin(route);
        return;
      }
      
      // 检查信息是否完善
      const userInfo = this.globalData.userInfo;
      if (userInfo && !userInfo.is_profile_complete) {
        console.log('用户信息未完善，跳转信息完善页面');
        wx.reLaunch({
          url: '/pages/profile/complete/complete'
        });
        return;
      }
      
      // 如果本地没有用户信息或信息不完整，从服务器获取
      if (!userInfo || userInfo.is_profile_complete === undefined) {
        const freshUserInfo = await userApi.getCurrentUser();
        this.globalData.userInfo = freshUserInfo;
        auth.setUserInfo(freshUserInfo);
        
        if (!freshUserInfo.is_profile_complete) {
          console.log('用户信息未完善，跳转信息完善页面');
          wx.reLaunch({
            url: '/pages/profile/complete/complete'
          });
        }
      }
    } catch (error) {
      console.error('检查用户信息失败:', error);
      
      // 如果是401错误（token失效），跳转登录页
      if (error.message && error.message.includes('401')) {
        console.log('Token失效，跳转登录页');
        const pages = getCurrentPages();
        const currentPage = pages[pages.length - 1];
        auth.navigateToLogin(currentPage?.route);
      }
      // 其他错误允许继续使用，避免阻塞
    } finally {
      this._checkingUserInfo = false;
    }
  }
});
