// 文章 API
const request = require('../utils/request');

// 获取文章列表
function listArticles(params = {}) {
  return request.get('/api/articles/', params);
}

// 获取文章详情
function getArticle(articleId) {
  return request.get(`/api/articles/${articleId}`);
}

module.exports = {
  listArticles,
  getArticle
};
