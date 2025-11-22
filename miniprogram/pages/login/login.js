const userApi = require('../../api/user');
const errorUtil = require('../../utils/error');
const auth = require('../../utils/auth');
const storage = require('../../utils/storage');

Page({
  data: {
    loading: false,
    redirectUrl: '',
    isAgree: false, // 是否同意协议
  },

  onLoad(options) {
    console.log('登录页加载', options);

    // 获取重定向参数
    if (options.redirect) {
      this.setData({
        redirectUrl: decodeURIComponent(options.redirect)
      });
    }

    // 登录校验已由 app.js 统一处理，无需在此重复判断
  },

  /**
   * 微信登录
   */
  handleWechatLogin() {
    console.log('点击登录，协议状态:', this.data.isAgree);

    if (!this.data.isAgree) {
      wx.showToast({
        title: '请先阅读并同意用户协议和隐私政策',
        icon: 'none',
        duration: 2000
      });
      return;
    }

    this.setData({ loading: true });

    // 调用 wx.login 获取 code
    wx.login({
      success: async (loginRes) => {
        console.log('获取 code 成功:', loginRes.code);

        // 调用后端登录接口
        try {
          const res = await userApi.wechatLogin({
            code: loginRes.code
          });
          console.log('登录成功:', res);

          // 保存 token
          const storage = require('../../utils/storage');
          const saveTokenResult = storage.setToken(res.access_token, res.refresh_token);

          if (!saveTokenResult) {
            wx.showToast({
              title: '本地存储失败，请重试',
              icon: 'none'
            });
            this.setData({ loading: false });
            return;
          }

          // 登录成功后，强制刷新全局用户信息
          await getApp().refreshUserInfo();

          // 重置 request 刷新状态（只保留一次调用）
          const request = require('../../utils/request');
          request.resetRefreshState();

          wx.showToast({
            title: '登录成功',
            icon: 'success'
          });

          this.handleLoginSuccess();
        } catch (error) {
          errorUtil.handleError(error);

        } finally {
          // 无论 API 调用成功或失败，都关闭 loading 状态
          this.setData({ loading: false });
        }
      }, // success 回调结束
      fail: (error) => {
        // wx.login 失败
        errorUtil.handleError(error);
        this.setData({ loading: false });
      } // fail 回调结束
    }); // wx.login 调用结束
  },

  // 协议勾选框变更
  onAgreementChange(e) {
    // 更可靠的勾选状态判断
    const isChecked = e.detail.value && e.detail.value.includes('agree');
    this.setData({
      isAgree: isChecked
    });
    console.log('协议勾选状态:', isChecked);
  },

  // 跳转用户协议
  openUserAgreement() {
    wx.navigateTo({
      url: '/pages/agreement/user-agreement/user-agreement'
    });
  },

  // 跳转隐私政策
  openPrivacyPolicy() {
    wx.navigateTo({
      url: '/pages/agreement/privacy-policy/privacy-policy'
    });
  },

  /**
   * 登录成功后跳转
   */
  async handleLoginSuccess() {
    try {
      // 直接使用全局 userInfo
      const userInfo = getApp().globalData.userInfo;
      console.log('获取用户信息:', userInfo);

      // 检查信息是否完善
      if (!userInfo || !userInfo.is_profile_complete) {
        console.log('用户信息未完善，跳转到信息完善页面');
        wx.reLaunch({
          url: '/pages/profile/complete/complete'
        });
        return;
      }

      // 信息已完善，跳转到目标页面
      const targetUrl = this.data.redirectUrl || '/pages/index/index';
      console.log('登录成功，跳转到:', targetUrl);

      setTimeout(() => {
        if (this.data.redirectUrl) {
          // 尝试使用 redirectTo (保留当前页面栈)
          wx.redirectTo({
            url: targetUrl,
            fail: () => {
              // 失败则尝试 switchTab
              wx.switchTab({
                url: targetUrl,
                fail: () => {
                  // 仍失败则使用 reLaunch (彻底重载)
                  wx.reLaunch({ url: targetUrl });
                }
              });
            }
          });
        } else {
          // 没有重定向目标，直接使用 reLaunch 回到首页
          wx.reLaunch({ url: targetUrl });
        }
      }, 500);

    } catch (error) {
      errorUtil.handleError(error);
      // 如果获取用户信息失败，仍然跳转到目标页面
      const targetUrl = this.data.redirectUrl || '/pages/index/index';
      setTimeout(() => {
        wx.reLaunch({ url: targetUrl });
      }, 500);
    }
  }
});