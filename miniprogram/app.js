const auth = require('./utils/auth');
const storage = require('./utils/storage');
const userApi = require('./api/user');
const { debounce, createCachedRequest } = require('./utils/debounce');

App({
  globalData: {
    userInfo: null,
    token: null,
    refreshToken: null,
    systemInfo: null
  },

  // 用于防止 checkAuth 重复执行的内部标志
  _checkingUserInfo: false,
  // 缓存的获取用户信息函数实例
  cachedGetCurrentUser: null,
  // 防抖的鉴权检查函数实例
  debouncedCheckAuth: null,

  onLaunch() {
    console.log('小程序启动');

    // [优化点 1] 使用更标准的 wx.getSystemInfoSync 获取设备信息
    try {
      this.globalData.systemInfo = wx.getSystemInfoSync();
    } catch (e) {
      console.error('获取系统信息失败:', e);
      this.globalData.systemInfo = {};
    }

    // --- 本地数据恢复流程 ---
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

    console.log('登录状态初始化:', auth.isLogined());

    // 创建防抖的鉴权检查函数 (避免 onShow 频繁触发)
    this.debouncedCheckAuth = debounce(this.checkAuth.bind(this), 500, false);

    // 创建缓存的用户信息获取函数（缓存30秒，用于优化 checkAuth 和 getUserInfoAsync）
    this.cachedGetCurrentUser = createCachedRequest(
      userApi.getCurrentUser,
      'getCurrentUser',
      30000 // 缓存有效期 30 秒
    );
  },

  onShow() {
    // 使用防抖的鉴权检查，确保进入小程序或从后台切回时进行状态检查
    this.debouncedCheckAuth();
  },

  /**
   * 检查登录状态和信息完善状态
   */
  async checkAuth() {
    if (this._checkingUserInfo) {
      console.log('正在检查用户信息，跳过本次并发调用');
      return;
    }
    this._checkingUserInfo = true; // 设置锁

    try {
      const pages = getCurrentPages();
      if (pages.length === 0) {
        return; // 页面栈为空时退出
      }

      const currentPage = pages[pages.length - 1];
      const route = currentPage.route;

      // 登录页和信息完善页不需要检查，避免无限循环跳转
      if (route === 'pages/login/login' || route === 'pages/profile/complete/complete') {
        return;
      }

      // --- 1. 检查是否登录 ---
      if (!auth.isLogined()) {
        console.log('未登录，跳转登录页，并带上重定向路由:', route);
        auth.navigateToLogin(route);
        return;
      }

      // --- 2. 检查用户信息完整性 (本地/缓存获取) ---
      let userInfo = this.globalData.userInfo;

      // 如果本地没有用户信息或信息不完整，从服务器获取（使用缓存）
      if (!userInfo || userInfo.is_profile_complete === undefined) {
        console.log('本地用户信息缺失或不完整，尝试从服务器获取...');
        const freshUserInfo = await this.cachedGetCurrentUser();

        // 更新全局和本地存储
        this.globalData.userInfo = freshUserInfo;
        auth.setUserInfo(freshUserInfo);
        userInfo = freshUserInfo;
      }

      // --- 3. 最终检查完善状态并跳转 ---
      if (userInfo && !userInfo.is_profile_complete) {
        console.log('用户信息未完善，跳转信息完善页面');
        wx.reLaunch({
          url: '/pages/profile/complete/complete'
        });
        return;
      }
    } catch (error) {
      console.error('检查用户信息或拉取失败:', error);

      // 如果是401错误（token失效），执行登出并跳转登录页
      if (error.message && error.message.includes('401')) {
        console.log('捕获到 Token 失效错误 (401)，跳转登录页');
        auth.clearAuth(); // 清除本地失效 Token

        const pages = getCurrentPages();
        const currentPage = pages[pages.length - 1];
        auth.navigateToLogin(currentPage?.route);
      }
      // 其他错误允许继续使用，避免阻塞用户
    } finally {
      this._checkingUserInfo = false; // 释放锁
    }
  },

  /**
   * 同步获取全局用户信息
   * @returns {Object|null} 用户信息
   */
  getUserInfoSync() {
    return this.globalData.userInfo;
  },

  /**
   * 异步获取用户信息（如无则用缓存接口拉取）
   * @returns {Promise<Object>} 用户信息
   */
  async getUserInfoAsync() {
    // 如果已存在完整信息，则直接返回
    if (this.globalData.userInfo && this.globalData.userInfo.is_profile_complete !== undefined) {
      return this.globalData.userInfo;
    }

    // 否则使用缓存的 API 调用获取最新信息
    const userInfo = await this.cachedGetCurrentUser();

    // 更新全局和本地存储
    this.globalData.userInfo = userInfo;
    require('./utils/auth').setUserInfo(userInfo);

    return userInfo;
  },

  /**
   * 强制刷新用户信息（不使用缓存）
   * 用于登录成功或信息更新后
   * @returns {Promise<Object>} 用户信息
   */
  async refreshUserInfo() {
    const userInfo = await require('./api/user').getCurrentUser();
    this.globalData.userInfo = userInfo;
    require('./utils/auth').setUserInfo(userInfo);
    return userInfo;
  }
});