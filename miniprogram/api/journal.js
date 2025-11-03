/**
 * 情绪日记 API
 */

const request = require('../utils/request');

/**
 * 获取情绪日记列表
 * GET /api/journals/
 * @param {object} params - { user_id, start_date, end_date, mood_name, page, page_size }
 * @returns {Promise<array>} 日记列表
 */
function listJournals(params = {}) {
  return request.get('/api/journals/', params);
}

/**
 * 创建情绪日记
 * POST /api/journals/
 * @param {object} data - { mood_score, mood_name, mood_emoji, text, record_date }
 * @returns {Promise<object>} 创建的日记
 */
function createJournal(data) {
  return request.post('/api/journals/', data);
}

/**
 * 获取单条日记详情
 * GET /api/journals/{journal_id}
 * @param {number} journalId
 * @returns {Promise<object>} 日记详情
 */
function getJournal(journalId) {
  return request.get(`/api/journals/${journalId}`);
}

/**
 * 更新情绪日记
 * PUT /api/journals/{journal_id}
 * @param {number} journalId
 * @param {object} data - 更新的字段
 * @returns {Promise<object>} 更新后的日记
 */
function updateJournal(journalId, data) {
  return request.put(`/api/journals/${journalId}`, data);
}

/**
 * 删除情绪日记
 * DELETE /api/journals/{journal_id}
 * @param {number} journalId
 * @returns {Promise}
 */
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
