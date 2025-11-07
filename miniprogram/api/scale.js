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

/**
 * 创建评估分组（开始评估流程）
 * POST /api/scales/assessment-groups
 * @param {object} data - { user_id, flow_type }
 * @returns {Promise<object>} 评估分组信息
 */
function createAssessmentGroup(data) {
  return request.post('/api/scales/assessment-groups', data);
}

/**
 * 获取评估分组详情
 * GET /api/scales/assessment-groups/{group_id}
 * @param {number} groupId
 * @returns {Promise<object>} 评估分组详情
 */
function getAssessmentGroup(groupId) {
  return request.get(`/api/scales/assessment-groups/${groupId}`);
}

/**
 * 获取下一步需要完成的量表
 * GET /api/scales/assessment-groups/{group_id}/next-step
 * @param {number} groupId
 * @returns {Promise<object>} 下一步信息
 */
function getNextStep(groupId) {
  return request.get(`/api/scales/assessment-groups/${groupId}/next-step`);
}

/**
 * 提交分组量表结果（流程化提交）
 * POST /api/scales/assessment-groups/{group_id}/submit
 * @param {number} groupId
 * @param {object} data - { scale_config_id, selected_options, duration_ms, started_at, completed_at }
 * @returns {Promise<object>} 测评结果
 */
function submitGroupedResult(groupId, data) {
  return request.post(`/api/scales/assessment-groups/${groupId}/submit`, data);
}

module.exports = {
  listConfigs,
  getConfig,
  createResult,
  listResults,
  getResult,
  // 评估流程 API
  createAssessmentGroup,
  getAssessmentGroup,
  getNextStep,
  submitGroupedResult
};
