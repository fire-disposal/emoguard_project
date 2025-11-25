// pages/articles/detail/detail.js
const articleApi = require('../../../api/article');

Page({
  data: {
    article: null,
    loading: true
  },

  onLoad(options) {
    const { id } = options;
    if (id) {
      this.loadArticle(id);
    }
  },

  /**
   * 加载文章详情
   */
  loadArticle(id) {
    this.setData({ loading: true });

    articleApi.getArticle(id)
      .then((res) => {
        // 替换富文本图片路径为完整静态资源 URL
        const BASE_URL = 'https://cg.aoxintech.com';
        if (res.content) {
          res.content = res.content.replace(/src="\/media\/summernote\/([^"]+)"/g, `src="${BASE_URL}/media/summernote/$1"`);
        }
        this.setData({
          article: res
        });
      })
      .catch((error) => {
        console.error('加载文章详情失败:', error);
        wx.showToast({
          title: error.message || '加载失败',
          icon: 'none'
        });
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  /**
   * 格式化时间
   */
  formatTime(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
});
