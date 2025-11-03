// pages/articles/list/list.js
const articleApi = require('../../../api/article');

Page({
  data: {
    articles: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false,
    refreshing: false
  },

  onLoad() {
    this.loadArticles();
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.setData({
      page: 1,
      refreshing: true
    });
    this.loadArticles(true);
  },

  /**
   * 上拉加载更多
   */
  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({
        page: this.data.page + 1
      });
      this.loadArticles(false);
    }
  },

  /**
   * 加载文章列表
   */
  loadArticles(refresh = false) {
    if (this.data.loading) return;

    this.setData({ loading: true });

    articleApi.listArticles({
      status: 'published',
      page: this.data.page,
      page_size: this.data.pageSize
    })
    .then((res) => {
      const articles = res || [];
      
      this.setData({
        articles: refresh ? articles : [...this.data.articles, ...articles],
        hasMore: articles.length >= this.data.pageSize
      });
    })
    .catch((error) => {
      console.error('加载文章列表失败:', error);
      wx.showToast({
        title: error.message || '加载失败',
        icon: 'none'
      });
    })
    .finally(() => {
      this.setData({ 
        loading: false,
        refreshing: false
      });
      
      if (this.data.refreshing) {
        wx.stopPullDownRefresh();
      }
    });
  },

  /**
   * 跳转到文章详情
   */
  goToDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/articles/detail/detail?id=${id}`
    });
  },

  /**
   * 格式化发布时间
   */
  formatTime(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
});
