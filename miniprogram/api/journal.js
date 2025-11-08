// 情绪日记 API
const request = require('../utils/request');

// 获取情绪日记列表
function listJournals(params = {}) {
  return request.get('/api/journals/', params);
}

// 创建情绪日记
function createJournal(data) {
  // 只提交 mood_score, mood_name, text
  const payload = {
    mood_score: data.mood_score,
    mood_name: data.mood_name,
    text: data.text || ''
  };
  return request.post('/api/journals/', payload);
}

// 获取单条日记详情
function getJournal(journalId) {
  return request.get(`/api/journals/${journalId}`);
}

// 更新情绪日记
function updateJournal(journalId, data) {
  // 只提交 mood_score, mood_name, text
  const payload = {};
  if (typeof data.mood_score !== 'undefined') payload.mood_score = data.mood_score;
  if (typeof data.mood_name !== 'undefined') payload.mood_name = data.mood_name;
  if (typeof data.text !== 'undefined') payload.text = data.text;
  return request.put(`/api/journals/${journalId}`, payload);
}

// 删除情绪日记
function deleteJournal(journalId) {
  return request.delete(`/api/journals/${journalId}`);
}

module.exports = {
  listJournals,
  createJournal,
  getJournal,
  updateJournal,
  deleteJournal
};
