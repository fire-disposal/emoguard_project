// 情绪日记 API
const request = require('../utils/request');

// 获取情绪日记列表
function listJournals(params = {}) {
  return request.get('/api/journals/', params);
}

// 创建情绪日记
function createJournal(data) {
  // 提交新版字段
  const payload = {
    mainMood: data.mainMood,
    moodIntensity: data.moodIntensity,
    mainMoodOther: data.mainMoodOther || '',
    moodSupplementTags: typeof data.moodSupplementTags === 'object' && !Array.isArray(data.moodSupplementTags) ? data.moodSupplementTags : {},
    moodSupplementText: data.moodSupplementText || '',
    started_at: data.started_at || null // 新增：支持上传开始作答时间
  };
  return request.post('/api/journals/', payload);
}

// 获取单条日记详情
function getJournal(journalId) {
  return request.get(`/api/journals/${journalId}`);
}

// 更新情绪日记
function updateJournal(journalId, data) {
  // 提交新版字段
  const payload = {};
  if (typeof data.mainMood !== 'undefined') payload.mainMood = data.mainMood;
  if (typeof data.moodIntensity !== 'undefined') payload.moodIntensity = data.moodIntensity;
  if (typeof data.mainMoodOther !== 'undefined') payload.mainMoodOther = data.mainMoodOther;
  if (typeof data.moodSupplementTags !== 'undefined') payload.moodSupplementTags = data.moodSupplementTags;
  if (typeof data.moodSupplementText !== 'undefined') payload.moodSupplementText = data.moodSupplementText;
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
