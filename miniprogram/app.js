const auth = require('./utils/auth');
const storage = require('./utils/storage');
const userApi = require('./api/user');
const { debounce, createCachedRequest } = require('./utils/debounce');
const request = require('./utils/request'); // 引入 request 以便重置状态

// 常量定义
const AGREEMENT_STATUS_KEY = 'agreement_status';
const AUTO_LOGIN_KEY = 'auto_login_enabled';

App({
  globalData: {
    userInfo: null,
    token: null,
    refreshToken: null,
    systemInfo: null,
    agreementStatus: false,
    autoLoginEnabled: true,
    // [新增] 用于组件或页面判断当前是否正在进行静默登录
    loginPromise: null
  },

  // 内部状态标识
  _checkingUserInfo: false,
  cachedGetCurrentUser: null,
  debouncedCheckAuth: null,

  onLaunch() {
    console.log('小程序启动');

    // 1. 初始化系统信息
    this.initSystemInfo();

    // 2. 恢复本地存储数据
    this.restoreLocalData();

    // 3. 初始化工具函数（防抖与缓存）
    this.initUtils();

    // 4. 尝试自动登录
    // 将 promise 挂载到 globalData，供 checkAuth 等待
    this.globalData.loginPromise = this.tryAutoLogin();
  },

  onShow() {
    // 每次切回前台时检查（使用防抖）
    if (this.debouncedCheckAuth) {
      this.debouncedCheckAuth();
    }
  },

  // --- 初始化逻辑封装 ---

  initSystemInfo() {
    try {
      this.globalData.systemInfo = wx.getSystemInfoSync();
    } catch (e) {
      console.error('获取系统信息失败:', e);
      this.globalData.systemInfo = {};
    }
  },

  restoreLocalData() {
    try {
      // 恢复 Token
      const token = storage.getToken();
      const refreshToken = storage.getRefreshToken();
      if (token) this.globalData.token = token;
      if (refreshToken) this.globalData.refreshToken = refreshToken;

      // 恢复用户信息
      const userInfo = auth.getUserInfo();
      if (userInfo) this.globalData.userInfo = userInfo;

      // 恢复配置状态
      const agreement = storage.getItem(AGREEMENT_STATUS_KEY);
      const autoLogin = storage.getItem(AUTO_LOGIN_KEY);

      // 注意：从 storage 取出的 boolean 可能是字符串，需要根据实际 storage 逻辑确保类型
      if (agreement !== null) this.globalData.agreementStatus = agreement;
      if (autoLogin !== null) this.globalData.autoLoginEnabled = autoLogin;

      console.log('本地数据恢复完成:', {
        hasToken: !!token,
        hasUser: !!userInfo,
        agreement: this.globalData.agreementStatus
      });
    } catch (error) {
      console.warn('本地数据恢复异常:', error);
    }
  },

  initUtils() {
    // checkAuth 防抖：500ms
    this.debouncedCheckAuth = debounce(this.checkAuth.bind(this), 500, false);

    // 用户信息获取缓存：30s
    this.cachedGetCurrentUser = createCachedRequest(
      userApi.getCurrentUser,
      'getCurrentUser',
      30000
    );
  },

  // --- 核心鉴权逻辑 ---

  /**
   * 检查登录状态和信息完善状态
   * [关键优化]：增加对自动登录 Promise 的等待
   */
  async checkAuth() {
    if (this._checkingUserInfo) return;
    this._checkingUserInfo = true;

    try {
      // 1. 等待自动登录（如果有）
      if (this.globalData.loginPromise) {
        try { await this.globalData.loginPromise; } catch (e) { }
      }

      const pages = getCurrentPages();
      if (pages.length === 0) return;
      const route = pages[pages.length - 1].route;

      // 2. 白名单：如果在登录页或注册页，不需要检查“是否未登录”
      // 因为这些页面本来就是给未登录用户看的
      const whiteList = ['pages/login/login', 'pages/profile/complete/complete'];
      if (whiteList.includes(route)) {
        // [可选优化]：为了防止用户手动点分享链接进入登录页，
        // 这里依然可以保留“如果已登录则踢回首页”的逻辑，但不是必须的了。
        if (route === 'pages/login/login' && auth.isLogined()) {
          wx.switchTab({ url: '/pages/index/index' });
        }
        return;
      }

      // 3. 核心拦截：如果未登录，直接踢去登录页
      if (!auth.isLogined()) {
        console.log('首页/内页检测到未登录，跳转登录页');
        // redirect 参数设为当前页，方便登录后跳回来
        auth.navigateToLogin(route);
        return;
      }

      // 4. 信息完善度检查 (保持不变)
      let userInfo = this.globalData.userInfo;
      if (!userInfo || userInfo.is_profile_complete === undefined) {
        userInfo = await this.cachedGetCurrentUser();
        this.updateGlobalUserInfo(userInfo);
      }
      if (userInfo && !userInfo.is_profile_complete) {
        wx.reLaunch({ url: '/pages/profile/complete/complete' });
      }

    } catch (error) {
      console.error(error);
    } finally {
      this._checkingUserInfo = false;
    }
  },

  /**
   * 尝试自动登录
   * @returns {Promise} 无论成功失败，resolve，避免阻塞
   */
  async tryAutoLogin() {
    // 1. 前置检查：如果已登录 或 未开启自动登录 或 协议未勾选
    if (auth.isLogined()) {
      console.log('Token有效，跳过自动登录');
      return Promise.resolve();
    }

    if (!this.globalData.autoLoginEnabled || !this.globalData.agreementStatus) {
      console.log('自动登录条件不满足(未开启或未勾选协议)');
      return Promise.resolve();
    }

    console.log('>>> 开始自动登录流程');

    try {
      // 2. 获取微信 Code
      const { code } = await wx.login();

      // 3. 换取 Token
      const res = await userApi.wechatLogin({ code });
      console.log('自动登录成功');

      // 4. 存储 Token
      storage.setToken(res.access_token, res.refresh_token);
      this.globalData.token = res.access_token;
      this.globalData.refreshToken = res.refresh_token;

      // 5. 重置请求模块状态（如刷新锁）
      if (request.resetRefreshState) request.resetRefreshState();

      // 6. 获取最新用户信息
      await this.refreshUserInfo();

      // 7. 自动登录成功后，通常保留在当前页，不需要强制跳转首页
      // 除非你在 login 页启动的自动登录。
      // 如果非要跳转：
      // wx.reLaunch({ url: '/pages/index/index' });

    } catch (error) {
      console.error('自动登录失败:', error);
      // 失败了清除自动登录标记，防止死循环重试？视业务而定
      // this.clearAutoLoginState(); 
    } finally {
      // 清除 promise 标记，释放 checkAuth
      this.globalData.loginPromise = null;
    }
  },

  // --- 通用 Helper ---

  updateGlobalUserInfo(userInfo) {
    this.globalData.userInfo = userInfo;
    auth.setUserInfo(userInfo);
  },

  async refreshUserInfo() {
    try {
      const userInfo = await userApi.getCurrentUser();
      this.updateGlobalUserInfo(userInfo);
      return userInfo;
    } catch (e) {
      console.error('刷新用户信息失败', e);
      return null;
    }
  },

  handleTokenExpired() {
    console.log('检测到 Token 失效，执行登出');
    auth.clearAuth();
    this.globalData.token = null;
    this.globalData.userInfo = null;

    const pages = getCurrentPages();
    const currentPage = pages[pages.length - 1];
    auth.navigateToLogin(currentPage?.route);
  },

  // --- Getters / Setters ---

  getUserInfoSync() { return this.globalData.userInfo; },

  async getUserInfoAsync() {
    if (this.globalData.userInfo?.is_profile_complete !== undefined) {
      return this.globalData.userInfo;
    }
    const userInfo = await this.cachedGetCurrentUser();
    this.updateGlobalUserInfo(userInfo);
    return userInfo;
  },

  setAgreementStatus(status) {
    this.globalData.agreementStatus = status;
    storage.setItem(AGREEMENT_STATUS_KEY, status);
  },

  getAgreementStatus() { return this.globalData.agreementStatus; },

  setAutoLoginEnabled(enabled) {
    this.globalData.autoLoginEnabled = enabled;
    storage.setItem(AUTO_LOGIN_KEY, enabled);
  },

  clearAutoLoginState() {
    this.globalData.agreementStatus = false;
    this.globalData.autoLoginEnabled = false;
    storage.removeItem(AGREEMENT_STATUS_KEY);
    storage.removeItem(AUTO_LOGIN_KEY);
  }
});