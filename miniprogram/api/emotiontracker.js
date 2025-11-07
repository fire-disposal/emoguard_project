/**
 * 情绪四维度 API
 */
const request = require('../utils/request');

/**
 * 创建或更新当日情绪记录
 * POST /api/emotiontracker/
 * @param {object} data - { user_id, depression, anxiety, energy, sleep }
 * @returns {Promise<object>} 记录结果
 */
function upsertEmotionRecord(data) {
  return request.post('/api/emotiontracker/', data);
}

/**
 * 获取用户情绪趋势
 * GET /api/emotiontracker/trend/{user_id}
 * @param {string} userId
 * @param {number} days
 * @returns {Promise<object>} 趋势数据
 */
function getEmotionTrend(userId, days = 90) {
  return request.get(`/api/emotiontracker/trend/${userId}`, { days });
}

/**
 * 获取今日早晚填写状态（无需传 userId，自动识别当前用户）
 * GET /api/emotiontracker/status
 * @returns {Promise<object>} { morning_filled, evening_filled }
 */
function getTodayStatus() {
  return request.get('/api/emotiontracker/status');
}

module.exports = {
  upsertEmotionRecord,
  getEmotionTrend,
  getTodayStatus
};