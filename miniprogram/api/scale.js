// 量表 API
const request = require('../utils/request');

// 获取量表配置列表
function listTypes(params = {}) {
  return request.get('/api/scales/list', params)
    .then((response) => response || [])
    .catch((error) => {
      console.error('量表类型请求失败:', error);
      return [];
    });
}

// 获取量表配置详情
function getScale(scaleCode) {
  return request.get(`/api/scales/${scaleCode}`)
    .catch((error) => {
      console.error('获取量表详情失败:', error);
      throw error;
    });
}

function getQuestions(scaleCode) {
  return request.get(`/api/scales/${scaleCode}/questions`)
    .catch((error) => {
      console.error('获取量表题目失败:', error);
      throw error;
    });
}

// 提交单量表结果
function createResult(data) {
  return request.post('/api/scales/results', data)
  .catch((error) => {
      console.error('获取量表题目失败:', error);
      throw error;
    });
}

// 获取单量表结果详情
function getResult(resultId) {
  return request.get(`/api/scales/results/${resultId}`);
}

// 获取量表历史结果
function getResultsHistory() {
  return request.get('/api/scales/results/history')
    .then(response => response || [])
    .catch(error => {
      console.error('量表历史结果请求失败:', error);
      return [];
    });
}


module.exports = {
  listTypes,
  getScale,
  getQuestions,
  createResult,
  getResultsHistory,
  getResult,
};
