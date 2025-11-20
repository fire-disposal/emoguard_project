/**
 * 错误处理工具
 * 统一管理错误处理逻辑
 */

const auth = require('./auth');

/**
 * 通用的错误处理函数
 * @param {object} error - 错误对象
 */
function handleError(error) {
  console.error('Error:', error);

  let errorMessage = '请求失败，请稍后重试';

  if (error && error.message) {
    errorMessage = error.message;
  }

  wx.showToast({
    title: errorMessage,
    icon: 'none',
    duration: 2000
  });

  // 如果是401错误（token失效），跳转登录页
  if (errorMessage.includes('401')) {
    auth.navigateToLogin();
  }
}

module.exports = {
  handleError
};