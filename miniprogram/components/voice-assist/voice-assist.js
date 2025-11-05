// 语音辅助组件
const ttsManager = require('../../utils/tts');

Component({
  properties: {
    // 是否显示语音控制按钮
    showControl: {
      type: Boolean,
      value: true
    },
    // 按钮位置
    position: {
      type: String,
      value: 'bottom-right' // bottom-right, bottom-left, top-right, top-left
    },
    // 自动播报内容
    autoSpeak: {
      type: Boolean,
      value: true
    },
    // 播报内容
    speakContent: {
      type: String,
      value: ''
    },
    // 播报延迟（毫秒）
    speakDelay: {
      type: Number,
      value: 500
    }
  },

  data: {
    isSpeaking: false,
    isEnabled: true,
    showVoiceIcon: true
  },

  lifetimes: {
    attached() {
      this.initVoiceAssist();
    },

    detached() {
      this.stopSpeaking();
    }
  },

  observers: {
    'speakContent': function(newContent) {
      if (newContent && this.data.autoSpeak && this.data.isEnabled) {
        this.delayedSpeak(newContent);
      }
    }
  },

  methods: {
    // 初始化语音辅助
    initVoiceAssist() {
      this.setData({
        isEnabled: ttsManager.checkEnabled()
      });

      // 监听语音播放状态
      this.startStatusCheck();
    },

    // 延迟播报
    delayedSpeak(content) {
      clearTimeout(this.speakTimer);
      this.speakTimer = setTimeout(() => {
        this.speakContent(content);
      }, this.data.speakDelay);
    },

    // 播报内容
    speakContent(content) {
      if (!content || !this.data.isEnabled) return;
      
      const formattedContent = ttsManager.formatText(content);
      this.setData({ isSpeaking: true });
      
      ttsManager.speak(formattedContent, {
        onComplete: () => {
          this.setData({ isSpeaking: false });
        }
      });
    },

    // 停止播报
    stopSpeaking() {
      ttsManager.stop();
      this.setData({ isSpeaking: false });
      clearTimeout(this.speakTimer);
    },

    // 切换语音开关
    toggleVoice() {
      const newEnabled = !this.data.isEnabled;
      const needShowTip = ttsManager.setEnabled(newEnabled);
      
      this.setData({ 
        isEnabled: newEnabled,
        showVoiceIcon: newEnabled
      });

      if (needShowTip) {
        this.showCloseTip();
      }

      if (!newEnabled) {
        this.stopSpeaking();
      }

      // 发送事件给父组件
      this.triggerEvent('voiceToggle', { enabled: newEnabled });
    },

    // 显示关闭提示
    showCloseTip() {
      wx.showModal({
        title: '提示',
        content: '是否关闭本界面语音阅读辅助？',
        confirmText: '是',
        cancelText: '否',
        success: (res) => {
          if (res.confirm) {
            // 用户确认关闭
            this.setData({ showVoiceIcon: false });
          } else {
            // 用户取消，重新开启
            ttsManager.setEnabled(true);
            this.setData({ 
              isEnabled: true,
              showVoiceIcon: true
            });
          }
        }
      });
    },

    // 开始状态检查
    startStatusCheck() {
      this.statusTimer = setInterval(() => {
        const isSpeaking = ttsManager.isSpeaking();
        if (isSpeaking !== this.data.isSpeaking) {
          this.setData({ isSpeaking: isSpeaking });
        }
      }, 500);
    },

    // 获取语音按钮样式类
    getVoiceButtonClass() {
      const baseClass = 'voice-button';
      const positionClass = `voice-button-${this.data.position}`;
      const statusClass = this.data.isSpeaking ? 'voice-button-speaking' : '';
      const enabledClass = this.data.isEnabled ? '' : 'voice-button-disabled';
      
      return `${baseClass} ${positionClass} ${statusClass} ${enabledClass}`.trim();
    },

    // 获取语音图标类
    getVoiceIconClass() {
      if (!this.data.isEnabled) return 'icon-volume-off';
      return this.data.isSpeaking ? 'icon-volume-speaking' : 'icon-volume-on';
    }
  }
});