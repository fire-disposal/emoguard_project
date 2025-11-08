// 量表 API
const request = require('../utils/request');

// 获取量表配置列表
function listConfigs(params = {}) {
  return request.get('/api/scales/configs', params)
    .then((response) => response || [])
    .catch((error) => {
      console.error('量表配置请求失败:', error);
      return [];
    });
}

// 获取量表配置详情
function getConfig(configId) {
  return request.get(`/api/scales/configs/${configId}`)
    .catch((error) => {
      console.error('获取量表详情失败:', error);
      throw error;
    });
}

// 提交单量表结果
function createResult(data) {
  return request.post('/api/scales/results', data);
}

// 获取单量表结果详情
function getResult(resultId) {
  return request.get(`/api/scales/results/${resultId}`);
}

// 开始智能测评
function startSmartAssessment() {
  return request.post('/api/scales/smart-assessment/start', {});
}

// 获取智能测评结果
function getSmartAssessmentResult(assessmentId) {
  return request.get(`/api/scales/smart-assessment/${assessmentId}`);
}

// 提交智能测评答案
function submitSmartAnswer(assessmentId, scaleConfigId, data) {
  return request.post(`/api/scales/smart-assessment/${assessmentId}/answer/${scaleConfigId}`, data);
}

module.exports = {
  listConfigs,
  getConfig,
  createResult,
  getResult,
  startSmartAssessment,
  getSmartAssessmentResult,
  submitSmartAnswer
};
