// 情绪日记 API
const request = require('../utils/request');

// 获取情绪日记列表
function listJournals(params = {}) {
  return request.get('/api/journals/', params);
}

// 创建情绪日记
function createJournal(data) {
  return request.post('/api/journals/', data);
}

// 获取单条日记详情
function getJournal(journalId) {
  return request.get(`/api/journals/${journalId}`);
}

// 更新情绪日记
function updateJournal(journalId, data) {
  return request.put(`/api/journals/${journalId}`, data);
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
