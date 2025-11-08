// 情绪四维度 API - 与后端完全匹配的实现
const request = require('../utils/request');

// 创建或更新当日情绪记录 (POST /api/emotiontracker/)
// 后端实现: create_emotion_record(request, data: EmotionRecordCreateSchema)
// 需要字段: depression, anxiety, energy, sleep
// 返回: EmotionRecordResponseSchema(id, user_id, depression, anxiety, energy, sleep, created_at)
function upsertEmotionRecord(data) {
  return request.post('/api/emotiontracker/', data);
}

// 获取用户情绪趋势 (GET /api/emotiontracker/trend?days={days})
// 后端实现: get_emotion_trend(request, days: int = Query(90))
// 参数: days (默认90天)
// 返回: EmotionTrendSchema(dates[], depression[], anxiety[], energy[], sleep[])
function getEmotionTrend(days = 30) {
  return request.get('/api/emotiontracker/trend', { days });
}

// 获取今日早晚填写状态 (GET /api/emotiontracker/status)
// 后端实现: get_today_status(request) -> {"morning_filled": bool, "evening_filled": bool}
function getTodayStatus() {
  return request.get('/api/emotiontracker/status');
}

module.exports = {
  upsertEmotionRecord,
  getEmotionTrend,
  getTodayStatus
};