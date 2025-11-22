const userApi = require('../../api/user');
const errorUtil = require('../../utils/error');
const auth = require('../../utils/auth'); // 引入统一的 auth 工具
const storage = require('../../utils/storage');
const request = require('../../utils/request'); // 提前引入，避免函数内 require

const app = getApp(); // 获取全局实例

Page({
  data: {
    loading: false,
    redirectUrl: '',
    isAgree: false, // 协议状态
  },

  onLoad(options) {
    // 1. 解析重定向参数
    if (options.redirect) {
      // 兼容处理：确保 url 解码正确
      let url = decodeURIComponent(options.redirect);
      // 补全斜杠（如果缺失）
      if (!url.startsWith('/')) {
        url = '/' + url;
      }
      this.setData({ redirectUrl: url });
      console.log('登录后重定向目标:', url);
    }

    // 2. 恢复协议勾选状态
    // 直接从 app.globalData 或方法获取，减少 storage 读取
    const agreementStatus = app.getAgreementStatus();
    this.setData({ isAgree: agreementStatus });
  },

  /**
   * 微信登录 (Async/Await 扁平化写法)
   */
  async handleWechatLogin() {
    // 1. 防抖与校验
    if (this.data.loading) return; 
    
    if (!this.data.isAgree) {
      wx.showToast({
        title: '请阅读并勾选用户协议',
        icon: 'none'
      });
      // 震动反馈，提示用户
      wx.vibrateShort({ type: 'medium' }); 
      return;
    }

    this.setData({ loading: true });

    try {
      // 2. 获取微信 Code (微信新版支持返回 Promise，如果不支持请看下方注释*)
      const { code } = await wx.login();
      
      console.log('获取 Code 成功，准备登录...');

      // 3. 调用后端登录
      const res = await userApi.wechatLogin({ code });

      // 4. 保存 Token (使用 auth 工具封装的方法，或者直接 storage)
      // 建议直接更新 globalData 和 storage
      storage.setToken(res.access_token, res.refresh_token);
      app.globalData.token = res.access_token;
      app.globalData.refreshToken = res.refresh_token;

      // 5. 重置请求锁 (防止死锁)
      if (request.resetRefreshState) {
        request.resetRefreshState();
      }

      // 6. 强制刷新用户信息 (并行处理提升速度，但需 await 确保数据到位)
      await app.refreshUserInfo();

      wx.showToast({ title: '登录成功', icon: 'success' });

      // 7. 执行跳转逻辑
      this.handleLoginSuccess();

    } catch (error) {
      console.error('登录流程异常:', error);
      errorUtil.handleError(error);
      this.setData({ loading: false }); // 只有出错才需要在这里重置，成功后页面会跳转
    }
    // 注意：成功时不设置 loading = false，防止跳转间隙用户重复点击
  },

  /**
   * 协议勾选变更
   */
  onAgreementChange(e) {
    const isChecked = e.detail.value.length > 0; // 只要数组不为空即为选中
    this.setData({ isAgree: isChecked });
    
    // 同步状态到全局
    app.setAgreementStatus(isChecked);
    
    // 只有勾选时才开启自动登录，取消勾选不一定需要关闭(看业务需求)，这里保持原逻辑
    if (isChecked) {
      app.setAutoLoginEnabled(true);
    }
  },

  openUserAgreement() {
    wx.navigateTo({ url: '/pages/agreement/user-agreement/user-agreement' });
  },

  openPrivacyPolicy() {
    wx.navigateTo({ url: '/pages/agreement/privacy-policy/privacy-policy' });
  },

  /**
   * 登录成功后的智能跳转
   */
  handleLoginSuccess() {
    const userInfo = app.globalData.userInfo;
    
    // 1. 检查信息完整性
    if (!userInfo || !userInfo.is_profile_complete) {
      console.log('信息未完善，跳转完善页');
      wx.reLaunch({ url: '/pages/profile/complete/complete' });
      return;
    }

    // 2. 确定目标页面
    // 如果没有重定向地址，默认去首页
    const targetUrl = this.data.redirectUrl || '/pages/index/index';
    
    console.log('准备跳转至:', targetUrl);

    // 3. 智能跳转策略
    // 优先尝试 switchTab (针对 TabBar 页面)
    wx.switchTab({
      url: targetUrl,
      success: () => {
        console.log('switchTab 成功');
      },
      fail: () => {
        // 如果不是 TabBar 页面，switchTab 会失败，此时尝试 reLaunch
        // 使用 reLaunch 而不是 redirectTo，是为了清除登录页的历史栈，防止安卓物理返回键回到登录页
        wx.reLaunch({
          url: targetUrl,
          fail: (err) => {
             console.error('跳转失败，回退到首页', err);
             wx.reLaunch({ url: '/pages/index/index' });
          }
        });
      }
    });
  }
});