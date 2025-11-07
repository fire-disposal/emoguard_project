// pages/profile/complete/complete.js
const userApi = require('../../../api/user');
const auth = require('../../../utils/auth');

Page({
  data: {
    formData: {
      real_name: '',
      gender: '',
      age: '',
      education: '',
      region: [],
      phone: ''
    },
    genderOptions: ['男', '女', '其他'],
    genderIndex: -1,
    educationOptions: ['文盲', '小学', '初中', '高中/中专', '大专', '本科及以上'],
    educationIndex: -1,
    regionIndex: -1,
    submitting: false,
    isFormValid: false
  },

  onLoad() {
    // 检查是否已登录
    if (!auth.isLogined()) {
      auth.navigateToLogin('/pages/profile/complete/complete');
      return;
    }

    // 获取当前用户信息
    this.loadUserInfo();
  },

  onShow() {
    if (!auth.isLogined()) {
      auth.navigateToLogin('/pages/profile/complete/complete');
      return;
    }
  },

  async loadUserInfo() {
    try {
      const userInfo = await userApi.getCurrentUser();
      console.log('当前用户信息:', userInfo);
      
      // 如果信息已完善，跳转到首页
      if (userInfo.is_profile_complete) {
        wx.reLaunch({
          url: '/pages/index/index'
        });
        return;
      }

      // 填充已有信息
      this.setData({
        formData: {
          real_name: userInfo.real_name || '',
          gender: userInfo.gender || '',
          age: userInfo.age ? String(userInfo.age) : '',
          education: userInfo.education || '',
          region: Array.isArray(userInfo.region) ? userInfo.region : [],
          phone: userInfo.phone || ''
        }
      });

      // 设置选择器默认值
      this.setPickerDefaults();
      this.validateForm();
    } catch (error) {
      console.error('获取用户信息失败:', error);
      wx.showToast({
        title: '获取用户信息失败',
        icon: 'none'
      });
    }
  },

  setPickerDefaults() {
    const { formData } = this.data;
    
    // 性别选择器
    const genderIndex = this.data.genderOptions.indexOf(formData.gender);
    if (genderIndex !== -1) {
      this.setData({ genderIndex });
    }

    // 学历选择器
    const educationIndex = this.data.educationOptions.indexOf(formData.education);
    if (educationIndex !== -1) {
      this.setData({ educationIndex });
    }

    // 地区选择器
    if (formData.region && formData.region.length === 3) {
      this.setData({
        regionIndex: formData.region
      });
    }
  },

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
    const region = e.detail.value; // region为数组 [省, 市, 区]
    this.setData({
      regionIndex: region,
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
      formData.region !== '' &&
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
      // 准备提交数据
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

      console.log('提交数据:', submitData);

      // 调用API更新用户信息
      const result = await userApi.updateProfile(submitData);
      
      console.log('更新成功:', result);

      // 更新本地用户信息
      auth.setUserInfo(result);

      wx.showToast({
        title: '信息完善成功',
        icon: 'success',
        duration: 2000
      });

      // 跳转到首页
      setTimeout(() => {
        wx.reLaunch({
          url: '/pages/index/index'
        });
      }, 2000);

    } catch (error) {
      console.error('提交失败:', error);
      wx.showToast({
        title: error.message || '提交失败，请重试',
        icon: 'none'
      });
    } finally {
      this.setData({ submitting: false });
    }
  }
});
