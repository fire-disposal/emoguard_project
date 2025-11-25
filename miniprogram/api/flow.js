// 认知流程测评 API
const request = require('../utils/request');

/**
 * 提交认知流程测评结果
 * @param {object} data - 提交数据，包含各量表分数与分析
 * @returns {Promise}
 */
function submitCognitiveFlow(data) {
  if (typeof data !== 'object' || data === null) {
    return Promise.reject(new Error('提交数据格式错误'));
  }
  return request.post('/api/cognitive/submit', data)
    .catch(err => {
      console.warn('认知流程测评提交异常:', err);
      return { error: err && err.message ? err.message : '网络异常' };
    });

}
// 获取认知测评历史记录
function getAssessmentHistory() {
  return request.get('/api/cognitive/history')
    .then(response => response || [])
    .catch(error => {
      console.error('认知测评历史记录请求失败:', error);
      return [];
    });
}

// 获取单条认知测评结果
function getAssessmentResult(recordId) {
  return request.get(`/api/cognitive/result/${recordId}`)
    .catch(error => {
      console.error('认知测评结果详情请求失败:', error);
      return null;
    });
}

module.exports = {
  submitCognitiveFlow,
  getAssessmentHistory,
  getAssessmentResult
};