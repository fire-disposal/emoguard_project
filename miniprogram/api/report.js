/**
 * 健康报告 API
 */

const request = require('../utils/request');

/**
 * 获取报告列表
 * GET /api/reports/
 * @param {object} params - { user_id, report_type, overall_risk, start_date, end_date, page, page_size }
 * @returns {Promise<array>} 报告列表
 */
function listReports(params = {}) {
  return request.get('/api/reports/', params);
}

/**
 * 获取报告详情
 * GET /api/reports/{report_id}
 * @param {number} reportId
 * @returns {Promise<object>} 报告详情
 */
function getReport(reportId) {
  return request.get(`/api/reports/${reportId}`);
}

/**
 * 获取用户报告摘要
 * GET /api/reports/summary/{user_id}
 * @param {string} userId
 * @returns {Promise<object>} 报告摘要
 */
function getUserReportSummary(userId) {
  return request.get(`/api/reports/summary/${userId}`);
}

/**
 * 获取健康趋势
 * GET /api/reports/trends/{user_id}
 * @param {string} userId
 * @param {number} days - 天数（默认90）
 * @returns {Promise<array>} 健康趋势数据
 */
function getHealthTrends(userId, days = 90) {
  return request.get(`/api/reports/trends/${userId}`, { days });
}

module.exports = {
  listReports,
  getReport,
  getUserReportSummary,
  getHealthTrends
};
