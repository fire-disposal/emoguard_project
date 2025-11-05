// TTS测试页面
const ttsManager = require('../../utils/tts');

Page({
  data: {
    testText: '欢迎使用情绪守护小程序，这是一个专为中老年朋友设计的健康管理工具。我们可以为您提供语音辅助阅读服务，让您更轻松地使用各项功能。',
    customText: '',
    isSpeaking: false,
    isEnabled: true,
    voiceSpeed: 0.8,
    voicePitch: 1.0,
    voiceVolume: 1.0,
    testResults: [],
    currentTest: ''
  },

  onLoad() {
    this.checkTTSupport();
    this.updateVoiceStatus();
  },

  onUnload() {
    ttsManager.stop();
  },

  // 检查TTS支持情况
  checkTTSupport() {
    const result = {
      name: 'TTS支持检测',
      time: new Date().toLocaleTimeString(),
      status: 'checking',
      message: ''
    };

    // 检查微信语音合成
    if (wx.voice && wx.voice.speak) {
      result.status = 'success';
      result.message = '微信内置TTS可用';
    } else {
      result.status = 'warning';
      result.message = '微信内置TTS不可用，将使用降级方案';
    }

    this.addTestResult(result);
  },

  // 更新语音状态
  updateVoiceStatus() {
    this.setData({
      isEnabled: ttsManager.checkEnabled(),
      isSpeaking: ttsManager.isSpeaking()
    });

    // 定时更新状态
    this.statusTimer = setInterval(() => {
      this.setData({
        isSpeaking: ttsManager.isSpeaking()
      });
    }, 500);
  },

  // 测试基础语音合成
  testBasicTTS() {
    const result = {
      name: '基础TTS测试',
      time: new Date().toLocaleTimeString(),
      status: 'testing',
      message: ''
    };

    this.addTestResult(result);
    this.setData({ currentTest: 'basic' });

    try {
      ttsManager.speak(this.data.testText, {
        speed: this.data.voiceSpeed,
        pitch: this.data.voicePitch,
        volume: this.data.voiceVolume,
        onComplete: () => {
          result.status = 'success';
          result.message = '语音播放完成';
          this.updateTestResult(result);
          this.setData({ currentTest: '' });
        }
      });

      result.message = '开始播放...';
      this.updateTestResult(result);
    } catch (error) {
      result.status = 'error';
      result.message = `播放失败: ${error.message}`;
      this.updateTestResult(result);
      this.setData({ currentTest: '' });
    }
  },

  // 测试自定义文本
  testCustomText() {
    if (!this.data.customText.trim()) {
      wx.showToast({
        title: '请输入测试文本',
        icon: 'none'
      });
      return;
    }

    const result = {
      name: '自定义文本测试',
      time: new Date().toLocaleTimeString(),
      status: 'testing',
      message: ''
    };

    this.addTestResult(result);
    this.setData({ currentTest: 'custom' });

    try {
      ttsManager.speak(this.data.customText, {
        onComplete: () => {
          result.status = 'success';
          result.message = '自定义文本播放完成';
          this.updateTestResult(result);
          this.setData({ currentTest: '' });
        }
      });

      result.message = '开始播放自定义文本...';
      this.updateTestResult(result);
    } catch (error) {
      result.status = 'error';
      result.message = `播放失败: ${error.message}`;
      this.updateTestResult(result);
      this.setData({ currentTest: '' });
    }
  },

  // 测试语音格式化
  testTextFormat() {
    const testCases = [
      {
        input: '<p>Hello <strong>World</strong>!</p>',
        expected: 'Hello World!'
      },
      {
        input: '  多   余   空  格  ',
        expected: '多 余 空 格'
      },
      {
        input: '&nbsp;HTML&nbsp;实体&nbsp;',
        expected: 'HTML实体'
      }
    ];

    testCases.forEach((testCase, index) => {
      const result = {
        name: `文本格式化测试${index + 1}`,
        time: new Date().toLocaleTimeString(),
        status: 'testing',
        message: ''
      };

      const formatted = ttsManager.formatText(testCase.input);
      if (formatted === testCase.expected) {
        result.status = 'success';
        result.message = `格式化成功: "${testCase.input}" -> "${formatted}"`;
      } else {
        result.status = 'error';
        result.message = `格式化失败: 期望"${testCase.expected}", 实际"${formatted}"`;
      }

      this.addTestResult(result);
    });
  },

  // 测试语音控制
  testVoiceControl() {
    const result = {
      name: '语音控制测试',
      time: new Date().toLocaleTimeString(),
      status: 'testing',
      message: ''
    };

    this.addTestResult(result);

    // 测试停止功能
    if (ttsManager.isSpeaking()) {
      ttsManager.stop();
      result.status = 'success';
      result.message = '语音停止成功';
    } else {
      // 先开始播放，然后停止
      ttsManager.speak('这是控制测试语音，将立即停止。');
      setTimeout(() => {
        ttsManager.stop();
        result.status = 'success';
        result.message = '播放并停止测试完成';
      }, 100);
    }

    this.updateTestResult(result);
  },

  // 测试语音参数
  testVoiceParams() {
    const speeds = [0.5, 0.8, 1.0, 1.2, 1.5];
    const speed = speeds[Math.floor(Math.random() * speeds.length)];

    const result = {
      name: `语音参数测试 (速度: ${speed})`,
      time: new Date().toLocaleTimeString(),
      status: 'testing',
      message: ''
    };

    this.addTestResult(result);
    this.setData({ currentTest: 'params' });

    const testText = `这是速度为${speed}的语音测试，您听清楚了吗？`;
    
    try {
      ttsManager.speak(testText, {
        speed: speed,
        onComplete: () => {
          result.status = 'success';
          result.message = `参数测试完成 (速度: ${speed})`;
          this.updateTestResult(result);
          this.setData({ currentTest: '' });
        }
      });
    } catch (error) {
      result.status = 'error';
      result.message = `参数测试失败: ${error.message}`;
      this.updateTestResult(result);
      this.setData({ currentTest: '' });
    }
  },

  // 输入框变化
  onTextInput(e) {
    this.setData({
      customText: e.detail.value
    });
  },

  // 速度滑块变化
  onSpeedChange(e) {
    this.setData({
      voiceSpeed: e.detail.value
    });
  },

  // 音调滑块变化
  onPitchChange(e) {
    this.setData({
      voicePitch: e.detail.value
    });
  },

  // 音量滑块变化
  onVolumeChange(e) {
    this.setData({
      voiceVolume: e.detail.value
    });
  },

  // 添加测试结果
  addTestResult(result) {
    const results = [...this.data.testResults, result];
    this.setData({
      testResults: results.slice(-20) // 保留最近20条
    });

    // 滚动到最新结果
    this.scrollToBottom();
  },

  // 更新测试结果
  updateTestResult(updatedResult) {
    const results = this.data.testResults.map(result => 
      result.time === updatedResult.time ? updatedResult : result
    );
    this.setData({ testResults: results });
  },

  // 滚动到底部
  scrollToBottom() {
    wx.createSelectorQuery().select('.test-results').boundingClientRect((rect) => {
      if (rect) {
        wx.pageScrollTo({
          scrollTop: rect.height,
          duration: 300
        });
      }
    }).exec();
  },

  // 清空测试结果
  clearResults() {
    this.setData({
      testResults: []
    });
  },

  // 停止所有语音
  stopAll() {
    ttsManager.stop();
    this.setData({
      isSpeaking: false,
      currentTest: ''
    });
    wx.showToast({
      title: '已停止所有语音',
      icon: 'success'
    });
  },

  // 复制测试结果
  copyResults() {
    const resultText = this.data.testResults.map(result => 
      `[${result.time}] ${result.name}: ${result.status} - ${result.message}`
    ).join('\n');

    wx.setClipboardData({
      data: resultText,
      success: () => {
        wx.showToast({
          title: '测试结果已复制',
          icon: 'success'
        });
      }
    });
  }
});