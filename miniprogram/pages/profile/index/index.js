// pages/profile/index/index.js
const userApi = require('../../../api/user');
const auth = require('../../../utils/auth');

Page({
  data: {
    userInfo: null,
    editing: false,
    formData: {},
    loading: true
  },

  onLoad() {
    this.loadUserInfo();
  },

  onShow() {
    // 刷新用户信息
    this.loadUserInfo();
  },

  /**
   * 加载用户信息
   */
  loadUserInfo() {
    this.setData({ loading: true });

    userApi.getCurrentUser()
      .then((res) => {
        this.setData({
          userInfo: res,
          formData: {
            nickname: res.nickname || '',
            real_name: res.real_name || '',
            gender: res.gender || '',
            birthday: res.birthday || '',
            phone: res.phone || '',
            address: res.address || ''
          }
        });
      })
      .catch((error) => {
        console.error('加载用户信息失败:', error);
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  /**
   * 切换编辑模式
   */
  toggleEdit() {
    this.setData({
      editing: !this.data.editing
    });
  },

  /**
   * 输入变化
   */
  onInput(e) {
    const { field } = e.currentTarget.dataset;
    const { value } = e.detail;
    
    this.setData({
      [`formData.${field}`]: value
    });
  },

  /**
   * 保存资料
   */
  saveProfile() {
    wx.showLoading({ title: '保存中...' });

    userApi.updateProfile(this.data.formData)
      .then((res) => {
        wx.showToast({
          title: '保存成功',
          icon: 'success'
        });

        // 更新本地用户信息
        auth.setUserInfo(res);

        this.setData({
          userInfo: res,
          editing: false
        });
      })
      .catch((error) => {
        console.error('保存失败:', error);
        wx.showToast({
          title: error.message || '保存失败',
          icon: 'none'
        });
      })
      .finally(() => {
        wx.hideLoading();
      });
  },

  /**
   * 性别选择变化
   */
  onGenderChange(e) {
    const genders = ['男', '女', '其他'];
    this.setData({
      'formData.gender': genders[e.detail.value]
    });
  },

  /**
   * 日期选择变化
   */
  onDateChange(e) {
    this.setData({
      'formData.birthday': e.detail.value
    });
  },

  /**
   * 退出登录
   */
  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          auth.logout();
        }
      }
    });
  }
});
