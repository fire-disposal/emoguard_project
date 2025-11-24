const authCenter = require('./utils/authCenter');
const storage = require('./utils/storage');
const userApi = require('./api/user');
const emotionApi = require('./api/emotiontracker');
const { debounce, createCachedRequest } = require('./utils/debounce');

const AGREEMENT_STATUS_KEY = 'agreement_status';
const AUTO_LOGIN_KEY = 'auto_login_enabled';

App({
  globalData: {
    userInfo: null,
    systemInfo: null,
    agreementStatus: false,
    autoLoginEnabled: true,
    morningFilled: false,
    eveningFilled: false
  },

  _checkingUserInfo: false,
  cachedGetCurrentUser: null,
  debouncedCheckAuth: null,

  onLaunch() {
    console.log('小程序启动');
    authCenter.init(); // 先初始化认证中心
    this.initSystemInfo();
    this.restoreLocalData();
    this.initUtils();
    // 自动登录 promise 不再挂载 globalData，直接内部 await
    this.autoLoginWrapper();
  },

  onShow() {
    this.debouncedCheckAuth && this.debouncedCheckAuth();
  },

  /* ---------- 初始化 ---------- */
  initSystemInfo() {
    try {
      this.globalData.systemInfo = wx.getSystemInfoSync();
    } catch (e) {
      this.globalData.systemInfo = {};
    }
  },

  restoreLocalData() {
    // 协议 & 自动登录配置
    const agreement = storage.getItem(AGREEMENT_STATUS_KEY);
    const autoLogin = storage.getItem(AUTO_LOGIN_KEY);
    if (agreement !== null) this.globalData.agreementStatus = agreement;
    if (autoLogin !== null) this.globalData.autoLoginEnabled = autoLogin;
  },

  initUtils() {
    this.debouncedCheckAuth = debounce(this.checkAuth.bind(this), 500);
    this.cachedGetCurrentUser = createCachedRequest(userApi.getCurrentUser, 'getCurrentUser', 30000);
  },

  /* ---------- 自动登录 ---------- */
  async autoLoginWrapper() {
    if (authCenter.logined) return; // 已登录
    if (!this.globalData.autoLoginEnabled || !this.globalData.agreementStatus) return;

    try {
      const { code } = await wx.login();
      const res = await userApi.wechatLogin({ code });
      authCenter.login(res.access_token, res.refresh_token); // 统一入口
      await this.refreshUserInfo();
      this.fetchEmotionStatus();
    } catch (e) {
      console.error('自动登录失败', e);
      this.clearAutoLoginState();
    }
  },

  /* ---------- 前台鉴权检查 ---------- */
  async checkAuth() {
    if (this._checkingUserInfo) return;
    this._checkingUserInfo = true;

    try {
      const pages = getCurrentPages();
      if (!pages.length) return;
      const route = pages[pages.length - 1].route;

      const whiteList = ['pages/login/login', 'pages/profile/complete/complete'];
      if (whiteList.includes(route)) return;

      /* 熔断后不再请求，防止 401 风暴 */
      if (authCenter.breakdown) return;

      if (!authCenter.logined) {
        authCenter.logout();
        return;
      }

      let userInfo = this.globalData.userInfo;
      if (!userInfo || userInfo.is_profile_complete === undefined) {
        userInfo = await this.cachedGetCurrentUser();
        this.updateGlobalUserInfo(userInfo);
      }
      if (userInfo && !userInfo.is_profile_complete) {
        wx.reLaunch({ url: '/pages/profile/complete/complete' });
      }
    } catch (e) {
      console.error('checkAuth error', e);
    } finally {
      this._checkingUserInfo = false;
    }
  },

  /* ---------- 情绪状态 ---------- */
  async fetchEmotionStatus() {
    if (!authCenter.logined || authCenter.breakdown) {
      this.globalData.morningFilled = false;
      this.globalData.eveningFilled = false;
      return;
    }
    try {
      const res = await emotionApi.getTodayStatus();
      this.globalData.morningFilled = !!res.morning_filled;
      this.globalData.eveningFilled = !!res.evening_filled;
    } catch (e) {
      this.globalData.morningFilled = false;
      this.globalData.eveningFilled = false;
    }
  },

  /* ---------- 通用 helper ---------- */
  updateGlobalUserInfo(userInfo) {
    this.globalData.userInfo = userInfo;
    storage.setItem('user_info', userInfo);
  },

  async refreshUserInfo() {
    try {
      const userInfo = await this.cachedGetCurrentUser();
      this.updateGlobalUserInfo(userInfo);
      return userInfo;
    } catch (e) {
      console.error('refreshUserInfo error', e);
      return null;
    }
  },

  /* ---------- 配置项 ---------- */
  setAgreementStatus(status) {
    this.globalData.agreementStatus = status;
    storage.setItem(AGREEMENT_STATUS_KEY, status);
  },
  getAgreementStatus() {
    return this.globalData.agreementStatus;
  },
  setAutoLoginEnabled(enabled) {
    this.globalData.autoLoginEnabled = enabled;
    storage.setItem(AUTO_LOGIN_KEY, enabled);
  },
  clearAutoLoginState() {
    this.globalData.agreementStatus = false;
    this.globalData.autoLoginEnabled = false;
    storage.removeItem(AGREEMENT_STATUS_KEY);
    storage.removeItem(AUTO_LOGIN_KEY);
  },

  /* ---------- 向下兼容的接口 ---------- */
  getUserInfoSync() {
    return this.globalData.userInfo;
  },

  async getUserInfoAsync() {
    if (this.globalData.userInfo?.is_profile_complete !== undefined) {
      return this.globalData.userInfo;
    }
    const userInfo = await this.cachedGetCurrentUser();
    this.updateGlobalUserInfo(userInfo);
    return userInfo;
  }
});