// miniprogram/pages/mood/moodtest/moodtest.js
const emotionApi = require('../../../api/emotiontracker');

Page({
  data: {
    // 四项认知测评数据
    depression: null,
    anxiety: null,
    energy: null,
    sleep: null,
    
    // 页面状态
    submitting: false,
    currentStep: 0, // 当前步骤
    currentPeriod: '', // morning/evening
    
    // 问题配置
    questions: [
      {
        key: 'depression',
        title: '情绪状态',
        question: '在过去的几个小时里，您是否觉得心情低落，或者对平常喜欢做的事情提不起兴趣？',
        type: 'radio',
        options: [
          { text: '没有', value: 0, desc: '完全没有这种感觉' },
          { text: '轻微', value: 1, desc: '偶尔有轻微的感觉' },
          { text: '中等', value: 2, desc: '有明显的感觉，影响日常生活' },
          { text: '很严重', value: 3, desc: '感觉非常强烈，严重影响生活' }
        ]
      },
      {
        key: 'anxiety',
        title: '焦虑水平',
        question: '在过去的几个小时里，您是否感到紧张、焦虑，或者坐立不安？',
        type: 'scale',
        min: 0,
        max: 10,
        minText: '完全没有',
        maxText: '非常严重',
        desc: '请根据您的实际感受选择0-10之间的数值'
      },
      {
        key: 'energy',
        title: '精力状态',
        question: '在过去的几个小时里，您是否觉得没有精力，容易感到疲劳？',
        type: 'radio',
        options: [
          { text: '没有', value: 0, desc: '精力充沛，没有疲劳感' },
          { text: '有一点', value: 1, desc: '偶尔感到轻微疲劳' },
          { text: '明显', value: 2, desc: '经常感到疲劳，影响活动' },
          { text: '非常严重', value: 3, desc: '极度疲劳，无法正常生活' }
        ]
      },
      {
        key: 'sleep',
        title: '睡眠质量',
        question: '请回顾今天（或昨晚），您的睡眠情况如何？',
        type: 'radio',
        options: [
          { text: '非常好', value: 0, desc: '睡眠质量极佳，醒来精神饱满' },
          { text: '比较好', value: 1, desc: '睡眠质量良好，基本恢复精力' },
          { text: '一般', value: 2, desc: '睡眠质量一般，略有不足' },
          { text: '不太好', value: 3, desc: '睡眠质量较差，影响精神状态' },
          { text: '很差', value: 4, desc: '睡眠质量极差，严重缺乏休息' }
        ]
      }
    ]
  },

  onLoad(options) {
    // 接收period参数（morning/evening），用于区分早晚记录
    if (options && options.period) {
      this.setData({
        currentPeriod: options.period
      });
    }
    
    // 设置页面标题
    const periodText = this.data.currentPeriod === 'morning' ? '早间' : this.data.currentPeriod === 'evening' ? '晚间' : '情绪';
    wx.setNavigationBarTitle({
      title: `${periodText}测评`
    });
    
    // 检查今日状态
    this.getTodayStatus();
  },

  // 处理单选变化
  handleRadioChange(e) {
    const { key } = e.currentTarget.dataset;
    const value = Number(e.detail.value);
    this.setData({ [key]: value });
  },

  // 处理滑块变化
  handleSliderChange(e) {
    const { key } = e.currentTarget.dataset;
    const value = Number(e.detail.value);
    this.setData({ [key]: value });
  },

  // 下一步
  nextStep() {
    const currentQuestion = this.data.questions[this.data.currentStep];
    const currentValue = this.data[currentQuestion.key];
    
    if (currentValue === null) {
      wx.showToast({ 
        title: '请完成当前题目', 
        icon: 'none',
        duration: 2000
      });
      return;
    }
    
    if (this.data.currentStep < this.data.questions.length - 1) {
      this.setData({
        currentStep: this.data.currentStep + 1
      });
    }
  },

  // 上一步
  prevStep() {
    if (this.data.currentStep > 0) {
      this.setData({
        currentStep: this.data.currentStep - 1
      });
    }
  },

  // 跳转到指定步骤
  goToStep(e) {
    const step = e.currentTarget.dataset.step;
    this.setData({
      currentStep: step
    });
  },

  // 提交数据 - 带详细日志版本
  async handleSubmit() {
    console.log('=== 开始提交情绪测评数据 ===');
    console.log('当前测评数据:', {
      depression: this.data.depression,
      anxiety: this.data.anxiety,
      energy: this.data.energy,
      sleep: this.data.sleep,
      period: this.data.currentPeriod
    });
    
    // 校验所有题目是否完成
    const incompleteQuestions = this.data.questions.filter(q => this.data[q.key] === null);
    console.log('未完成题目数量:', incompleteQuestions.length);
    console.log('未完成题目:', incompleteQuestions.map(q => q.title));
    
    if (incompleteQuestions.length > 0) {
      console.log('数据校验失败: 有未完成的题目');
      wx.showToast({
        title: `还有${incompleteQuestions.length}道题未完成`,
        icon: 'none',
        duration: 2000
      });
      
      // 跳转到第一个未完成的题目
      const firstIncompleteIndex = this.data.questions.findIndex(q => q.key === incompleteQuestions[0].key);
      console.log('跳转到第', firstIncompleteIndex + 1, '题');
      this.setData({
        currentStep: firstIncompleteIndex
      });
      return;
    }
    
    console.log('数据校验通过，开始提交');
    this.setData({ submitting: true });
    console.log('提交状态已设置为true');
    
    try {
      // 构建提交数据
      const recordData = {
        depression: this.data.depression,
        anxiety: this.data.anxiety,
        energy: this.data.energy,
        sleep: this.data.sleep
      };
      
      console.log('基础数据构建完成:', recordData);
      
      // 如果有period参数，传递给后端
      if (this.data.currentPeriod) {
        recordData.period = this.data.currentPeriod;
        console.log('添加时间段参数:', this.data.currentPeriod);
      }
      
      // 添加时间戳和设备信息
      recordData.timestamp = new Date().toISOString();
      recordData.device_info = {
        platform: wx.getSystemInfoSync().platform,
        version: wx.getSystemInfoSync().version
      };
      
      console.log('完整提交数据:', recordData);
      console.log('调用API: upsertEmotionRecord');
      
      const response = await emotionApi.upsertEmotionRecord(recordData);
      
      console.log('API提交成功，返回数据:', response);
      console.log('返回数据类型:', typeof response);
      console.log('返回数据键值:', response ? Object.keys(response) : '无返回数据');
      
      // 检查是否有预警
      if (response && response.alert) {
        console.log('检测到预警:', response.alert);
        this.showSubmissionAlert(response.alert);
      }
      
      // 显示成功提示
      wx.showToast({
        title: '测评提交成功',
        icon: 'success',
        duration: 2000
      });
      
      console.log('成功提示已显示，准备返回上一页');
      
      setTimeout(() => {
        console.log('执行返回操作');
        wx.navigateBack();
      }, 1500);
      
    } catch (error) {
      console.error('错误信息:', error.message);
      console.error('错误堆栈:', error.stack);
      console.error('错误代码:', error.code);
      console.error('错误响应:', error.response);
      
      // 更详细的错误处理
      let errorMessage = '提交失败，请重试';
      if (error.code === 'VALIDATION_ERROR') {
        errorMessage = '数据格式错误，请检查输入';
      } else if (error.code === 'RATE_LIMIT') {
        errorMessage = '提交过于频繁，请稍后再试';
      } else if (error.message.includes('网络')) {
        errorMessage = '网络连接失败，请检查网络';
      }
      
      wx.showToast({
        title: errorMessage,
        icon: 'none',
        duration: 2000
      });
    } finally {
      this.setData({ submitting: false });
      console.log('提交状态已重置为false');
    }
  },

  // 显示提交预警
  showSubmissionAlert(alert) {
    if (!alert || !alert.message) return;
    
    wx.showModal({
      title: '健康提醒',
      content: alert.message,
      showCancel: false,
      confirmText: '我知道了',
      confirmColor: alert.level === 'high' ? '#ff7875' : '#ffa940'
    });
  },

  // 获取今日状态
  async getTodayStatus() {
    try {
      const todayStatus = await emotionApi.getTodayStatus();
      console.log('今日状态:', todayStatus);
      
    } catch (error) {
      console.warn('获取今日状态失败:', error);
    }
  },

  // 获取当前进度的百分比
  getProgressPercent() {
    return ((this.data.currentStep + 1) / this.data.questions.length) * 100;
  }
});