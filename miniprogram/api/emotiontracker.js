// 情绪四维度 API
const request = require('../utils/request');

// 创建或更新当日情绪记录
function upsertEmotionRecord(data) {
  return request.post('/api/emotiontracker/', data);
}

// 获取用户情绪趋势
function getEmotionTrend(days = 90) {
  return request.get('/api/emotiontracker/trend', { days });
}

// 获取今日早晚填写状态
function getTodayStatus() {
  return request.get('/api/emotiontracker/status');
}

module.exports = {
  upsertEmotionRecord,
  getEmotionTrend,
  getTodayStatus
};