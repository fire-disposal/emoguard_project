/**
 * 量表 API
 */

const request = require('../utils/request');

/**
 * 获取量表配置列表
 * GET /api/scales/configs
 * @param {object} params - { status, type }
 * @returns {Promise<array>} 量表配置列表
 */
function listConfigs(params = {}) {
  return request.get('/api/scales/configs', params);
}

/**
 * 获取量表详情
 * GET /api/scales/configs/{config_id}
 * @param {number} configId
 * @returns {Promise<object>} 量表配置详情
 */
function getConfig(configId) {
  return request.get(`/api/scales/configs/${configId}`);
}

/**
 * 提交量表结果
 * POST /api/scales/results
 * @param {object} data - { user_id, scale_config_id, selected_options, conclusion, duration_ms, started_at, completed_at }
 * @returns {Promise<object>} 测评结果
 */
function createResult(data) {
  return request.post('/api/scales/results', data);
}

/**
 * 获取测评结果列表
 * GET /api/scales/results
 * @param {object} params - { user_id, scale_config_id, start_date, end_date, page, page_size }
 * @returns {Promise<array>} 测评结果列表
 */
function listResults(params = {}) {
  return request.get('/api/scales/results', params);
}

/**
 * 获取测评结果详情
 * GET /api/scales/results/{result_id}
 * @param {number} resultId
 * @returns {Promise<object>} 测评结果详情
 */
function getResult(resultId) {
  return request.get(`/api/scales/results/${resultId}`);
}

module.exports = {
  listConfigs,
  getConfig,
  createResult,
  listResults,
  getResult
};
