// miniprogram/utils/subscribeUtil.js
const noticeApi = require('../api/notice');

/**
 * 发起订阅消息授权，并同步状态到后端
 * @param {string} templateId - 订阅模板ID
 * @param {function} callback - 授权结果回调 (action: 'accept'|'reject'|'ban')
 */
function subscribeMessage(templateId, callback) {
  wx.requestSubscribeMessage({
    tmplIds: [templateId],
    success: (res) => {
      const action = res[templateId];
      syncSubscribeStatus(templateId, action);
      if (typeof callback === 'function') callback(action);
    },
    fail: (err) => {
      console.error('订阅消息失败:', err);
      if (typeof callback === 'function') callback('fail');
    }
  });
}

/**
 * 同步订阅状态到后端
 * @param {string} templateId
 * @param {string} action - 'accept'|'reject'|'ban'
 */
async function syncSubscribeStatus(templateId, action, retry = 0) {
  const maxRetry = 5;
  const baseDelay = 500; // ms
  try {
    const response = await noticeApi.syncSubscribeStatus({
      template_id: templateId,
      action: action
    });
    console.log('同步订阅状态成功:', response);
    if (response.status === 'success' && action === 'accept') {
      wx.showToast({
        title: '订阅成功',
        icon: 'success'
      });
    }
  } catch (error) {
    if (retry < maxRetry) {
      const delay = baseDelay * Math.pow(2, retry);
      console.warn(`订阅状态重试，第${retry + 1}次，延迟${delay}ms`);
      setTimeout(() => {
        syncSubscribeStatus(templateId, action, retry + 1);
      }, delay);
    } else {
      console.error('同步订阅状态失败，已达最大重试次数:', error);
      // 不显示错误，避免影响用户体验
    }
  }
}

module.exports = {
  subscribeMessage,
  syncSubscribeStatus
};
