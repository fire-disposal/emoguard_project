// pages/login/login.js
const userApi = require('../../api/user');
const auth = require('../../utils/auth');

Page({
  data: {
    loading: false,
    redirectUrl: ''
  },

  onLoad(options) {
    console.log('登录页加载', options);
    
    // 获取重定向参数
    if (options.redirect) {
      this.setData({
        redirectUrl: decodeURIComponent(options.redirect)
      });
    }
    
    // 如果已登录，直接跳转
    if (auth.isLogined()) {
      this.handleLoginSuccess();
    }
  },

  /**
   * 微信登录
   */
  handleWechatLogin() {
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
          auth.setToken(res.access_token, res.refresh_token);
          auth.setUserInfo(res.user);
          
          // 更新全局数据
          const app = getApp();
          app.globalData.userInfo = res.user;
          app.globalData.token = res.access_token;
          app.globalData.refreshToken = res.refresh_token;
          
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

  /**
   * 登录成功后跳转
   */
  handleLoginSuccess() {
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
  }
});
