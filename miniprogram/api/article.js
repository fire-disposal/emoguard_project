/**
 * 文章 API
 */

const request = require('../utils/request');

/**
 * 获取文章列表
 * GET /api/articles/
 * @param {object} params - { status, search, page, page_size }
 * @returns {Promise<array>} 文章列表
 */
function listArticles(params = {}) {
  return request.get('/api/articles/', params);
}

/**
 * 获取文章详情
 * GET /api/articles/{article_id}
 * @param {number} articleId
 * @returns {Promise<object>} 文章详情
 */
function getArticle(articleId) {
  return request.get(`/api/articles/${articleId}`);
}

module.exports = {
  listArticles,
  getArticle
};
