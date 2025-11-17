// pages/login/login.js
const userApi = require('../../api/user');
const auth = require('../../utils/auth');
const storage = require('../../utils/storage');

Page({
  data: {
    loading: false,
    redirectUrl: '',
    isAgree: false,
  },

  onLoad(options) {
    console.log('登录页加载', options);
    
    // 获取重定向参数
    if (options.redirect) {
      this.setData({
        redirectUrl: decodeURIComponent(options.redirect)
      });
    }
    
    // 如果已登录，验证 token 有效性
    if (auth.isLogined()) {
      console.log('已检测到登录状态，验证 token 有效性');
      // 简单验证 token 是否有效
      userApi.getCurrentUser()
        .then(() => {
          console.log('Token 有效，直接跳转');
          this.handleLoginSuccess();
        })
        .catch((error) => {
          console.log('Token 无效，清除登录状态:', error);
          storage.clearToken();
          auth.clearUserInfo();
        });
    }
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
      success: (loginRes) => {
        console.log('获取 code 成功:', loginRes.code);
        
        // 调用后端登录接口
        userApi.wechatLogin({
          code: loginRes.code
        })
        .then((res) => {
          console.log('登录成功:', res);

          // 保存 token 和用户信息
          const userInfo = res.user || res;
          
          // 使用 storage 模块直接保存 token，并检查是否成功
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
          
          // 保存用户信息
          auth.setUserInfo(userInfo);

          // 更新全局数据
          const app = getApp();
          if (app && app.globalData) {
            app.globalData.userInfo = userInfo;
            app.globalData.token = res.access_token;
            app.globalData.refreshToken = res.refresh_token;
          }

          // 重置 request 刷新状态
          const request = require('../../utils/request');
          request.resetRefreshState();

          wx.showToast({
            title: '登录成功',
            icon: 'success'
          });

          this.handleLoginSuccess();
        })
        .catch((error) => {
          console.error('登录失败:', error);
          wx.showToast({
            title: error.message || '登录失败，请重试',
            icon: 'none'
          });
        })
        .finally(() => {
          this.setData({ loading: false });
        });
      },
      fail: (error) => {
        console.error('wx.login 失败:', error);
        wx.showToast({
          title: '微信登录失败',
          icon: 'none'
        });
        this.setData({ loading: false });
      }
    });
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
      // 获取当前用户信息
      const userInfo = await userApi.getCurrentUser();
      console.log('获取用户信息:', userInfo);
      
      // 检查信息是否完善
      if (!userInfo.is_profile_complete) {
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
          wx.redirectTo({
            url: targetUrl,
            fail: () => {
              wx.switchTab({
                url: targetUrl,
                fail: () => {
                  wx.reLaunch({ url: targetUrl });
                }
              });
            }
          });
        } else {
          wx.reLaunch({ url: targetUrl });
        }
      }, 500);
      
    } catch (error) {
      console.error('获取用户信息失败:', error);
      // 如果获取用户信息失败，仍然跳转到首页
      const targetUrl = this.data.redirectUrl || '/pages/index/index';
      setTimeout(() => {
        wx.reLaunch({ url: targetUrl });
      }, 500);
    }
  }
});

// TODO: 需要新建 miniprogram/pages/agreement/user-agreement 与 privacy-policy 页面及内容文件
