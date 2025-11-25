// pages/profile/userinfo/userinfo.js
const userApi = require('../../../api/user');
const authCenter = require('../../../utils/authCenter');

Page({
  data: {
    userInfo: null,
    loading: true,
    editing: false,
    formData: {},
    genderOptions: ['男', '女', '其他'],
    educationOptions: ['文盲', '小学', '初中', '高中/中专', '大专', '本科及以上'],
    genderIndex: -1,
    educationIndex: -1,
    region: [],
    submitting: false,
    isFormValid: false
  },

  onShow() {
    if (!authCenter.logined) {
      authCenter.logout();
      wx.reLaunch({ url: '/pages/login/login' });
      return;
    }
    this.loadUserInfo();
  },

  loadUserInfo() {
    this.setData({ loading: true });
    userApi.getCurrentUser()
      .then((res) => {
        // 兼容后端字段
        const region = [res.province || '', res.city || '', res.district || ''];
        this.setData({
          userInfo: res,
          formData: {
            real_name: res.real_name || '',
            gender: res.gender || '',
            age: res.age ? String(res.age) : '',
            education: res.education || '',
            region,
            phone: res.phone || ''
          },
          genderIndex: this.data.genderOptions.indexOf(res.gender),
          educationIndex: this.data.educationOptions.indexOf(res.education),
          region: region,
          editing: false
        });
        this.validateForm();
      })
      .catch((error) => {
        wx.showToast({
          title: '获取用户信息失败',
          icon: 'none'
        });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  // 切换编辑模式
  toggleEdit() {
    const newEditing = !this.data.editing;
    if (!newEditing) {
      // 取消编辑时，重置表单数据为当前用户信息
      const userInfo = this.data.userInfo;
      const region = [userInfo.province || '', userInfo.city || '', userInfo.district || ''];
      this.setData({
        formData: {
          real_name: userInfo.real_name || '',
          gender: userInfo.gender || '',
          age: userInfo.age ? String(userInfo.age) : '',
          education: userInfo.education || '',
          region,
          phone: userInfo.phone || ''
        },
        genderIndex: this.data.genderOptions.indexOf(userInfo.gender),
        educationIndex: this.data.educationOptions.indexOf(userInfo.education),
        region: region
      });
      this.validateForm();
    }
    this.setData({ editing: newEditing });
  },

  // 输入变化
  onInputChange(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;
    this.setData({
      [`formData.${field}`]: value
    });
    this.validateForm();
  },

  onGenderChange(e) {
    const index = e.detail.value;
    const gender = this.data.genderOptions[index];
    this.setData({
      genderIndex: index,
      'formData.gender': gender
    });
    this.validateForm();
  },

  onEducationChange(e) {
    const index = e.detail.value;
    const education = this.data.educationOptions[index];
    this.setData({
      educationIndex: index,
      'formData.education': education
    });
    this.validateForm();
  },

  onRegionChange(e) {
    const region = e.detail.value;
    this.setData({
      region,
      'formData.region': region,
      'formData.province': region[0] || '',
      'formData.city': region[1] || '',
      'formData.district': region[2] || ''
    });
    this.validateForm();
  },

  validateForm() {
    const { formData } = this.data;
    const isValid =
      formData.real_name.trim() !== '' &&
      formData.gender !== '' &&
      formData.age !== '' &&
      parseInt(formData.age) >= 1 && parseInt(formData.age) <= 100 &&
      formData.education !== '' &&
      formData.region && formData.region.length === 3 &&
      this.validatePhone(formData.phone);
    this.setData({ isFormValid: isValid });
  },

  validatePhone(phone) {
    if (!phone) return false;
    const phoneRegex = /^1[3-9]\d{9}$/;
    return phoneRegex.test(phone);
  },

  async submitForm() {
    if (!this.data.isFormValid || this.data.submitting) {
      return;
    }
    this.setData({ submitting: true });
    try {
      const submitData = {
        real_name: this.data.formData.real_name.trim(),
        gender: this.data.formData.gender,
        age: parseInt(this.data.formData.age),
        education: this.data.formData.education,
        province: this.data.formData.province,
        city: this.data.formData.city,
        district: this.data.formData.district,
        phone: this.data.formData.phone
      };
      const result = await userApi.updateProfile(submitData);
      authCenter.setUserInfo(result);
      wx.showToast({
        title: '保存成功',
        icon: 'success',
        duration: 2000
      });
      this.setData({ editing: false, userInfo: result });
      this.loadUserInfo();
    } catch (error) {
      wx.showToast({
        title: error.message || '保存失败',
        icon: 'none'
      });
    } finally {
      this.setData({ submitting: false });
    }
  },


});