// 健康报告 API
const request = require('../utils/request');

// 获取报告列表
function listReports(params = {}) {
  return request.get('/api/reports/', params);
}

// 获取报告详情
function getReport(reportId) {
  return request.get(`/api/reports/${reportId}`);
}

// 获取用户报告摘要
function getUserReportSummary() {
  return request.get('/api/reports/summary');
}

// 获取健康趋势
function getHealthTrends(days = 90) {
  return request.get('/api/reports/trends', { days });
}

module.exports = {
  listReports,
  getReport,
  getUserReportSummary,
  getHealthTrends
};
