// 文字转语音工具类
class TTSManager {
  constructor() {
    this.audioManager = null;
    this.isEnabled = true;
    this.isFirstClose = true;
    this.currentText = '';
    this.speaking = false;
  }

  // 初始化音频管理器
  init() {
    if (!this.audioManager) {
      this.audioManager = wx.getBackgroundAudioManager();
      this.audioManager.onEnded(() => {
        this.speaking = false;
      });
      this.audioManager.onStop(() => {
        this.speaking = false;
      });
      this.audioManager.onError((err) => {
        console.error('语音播放错误:', err);
        this.speaking = false;
      });
    }
  }

  // 检查是否开启语音辅助
  checkEnabled() {
    const setting = wx.getStorageSync('voiceAssist');
    this.isEnabled = setting !== false; // 默认开启
    return this.isEnabled;
  }

  // 设置语音辅助开关
  setEnabled(enabled) {
    this.isEnabled = enabled;
    wx.setStorageSync('voiceAssist', enabled);
    
    if (!enabled && this.isFirstClose) {
      this.isFirstClose = false;
      return true; // 需要显示提示
    }
    return false;
  }

  // 文字转语音
  speak(text, options = {}) {
    if (!this.checkEnabled() || !text) return;

    this.init();
    this.currentText = text;
    this.speaking = true;

    // 使用微信内置的语音合成
    if (wx.voice) {
      wx.voice.speak({
        text: text,
        lang: 'zh_CN',
        speed: options.speed || 0.8,
        pitch: options.pitch || 1.0,
        volume: options.volume || 1.0,
        success: () => {
          console.log('语音播放成功');
        },
        fail: (err) => {
          console.error('语音播放失败:', err);
          this.speaking = false;
          // 降级处理：使用系统TTS
          this.useSystemTTS(text);
        }
      });
    } else {
      // 使用系统TTS
      this.useSystemTTS(text);
    }
  }

  // 使用系统TTS（降级方案）
  useSystemTTS(text) {
    // 这里可以实现调用后端TTS服务的逻辑
    // 暂时使用console提示
    console.log('系统TTS:', text);
    this.speaking = false;
  }

  // 停止播放
  stop() {
    if (this.audioManager) {
      this.audioManager.stop();
    }
    if (wx.voice) {
      wx.voice.stop();
    }
    this.speaking = false;
  }

  // 暂停播放
  pause() {
    if (this.audioManager) {
      this.audioManager.pause();
    }
    if (wx.voice) {
      wx.voice.pause();
    }
  }

  // 恢复播放
  resume() {
    if (this.audioManager) {
      this.audioManager.play();
    }
    if (wx.voice) {
      wx.voice.resume();
    }
  }

  // 获取播放状态
  isSpeaking() {
    return this.speaking;
  }

  // 获取当前文本
  getCurrentText() {
    return this.currentText;
  }

  // 语音输入转文字
  voiceToText(options = {}) {
    return new Promise((resolve, reject) => {
      wx.getRecorderManager().start({
        duration: 60000, // 最长60秒
        sampleRate: 16000,
        numberOfChannels: 1,
        encodeBitRate: 96000,
        format: 'mp3'
      });

      const recorderManager = wx.getRecorderManager();
      
      recorderManager.onStop((res) => {
        const { tempFilePath } = res;
        
        // 调用语音识别API
        wx.cloud.callFunction({
          name: 'speechToText',
          data: {
            filePath: tempFilePath
          },
          success: (result) => {
            resolve(result.result.text);
          },
          fail: (err) => {
            reject(err);
          }
        });
      });

      recorderManager.onError((err) => {
        reject(err);
      });
    });
  }

  // 格式化文本（去除特殊字符，优化朗读效果）
  formatText(text) {
    if (!text) return '';
    
    return text
      .replace(/<[^>]*>/g, '') // 移除HTML标签
      .replace(/&[^;]*;/g, '') // 移除HTML实体
      .replace(/\s+/g, ' ') // 合并多余空格
      .trim();
  }
}

// 创建全局实例
const ttsManager = new TTSManager();

module.exports = ttsManager;