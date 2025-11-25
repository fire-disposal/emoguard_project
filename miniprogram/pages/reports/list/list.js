// pages/reports/list/list.js
const reportApi = require('../../../api/report');
const authCenter = require('../../../utils/authCenter');

Page({
  data: {
    reports: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false
  },

  onShow() {
    if (!authCenter.logined) {
      authCenter.logout();
      wx.reLaunch({ url: '/pages/login/login' });
      return;
    }
  },

  onLoad() {
    this.loadReports();
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({ page: this.data.page + 1 });
      this.loadReports();
    }
  },

  /**
   * 加载报告列表
   */
  loadReports() {
    const userInfo = authCenter.getUserInfo();
    if (!userInfo) return;

    if (this.data.loading) return;

    this.setData({ loading: true });

    reportApi.listReports({
      user_id: userInfo.id,
      page: this.data.page,
      page_size: this.data.pageSize
    })
    .then((res) => {
      const reports = res || [];
      
      this.setData({
        reports: this.data.page === 1 ? reports : [...this.data.reports, ...reports],
        hasMore: reports.length >= this.data.pageSize
      });
    })
    .catch((error) => {
      console.error('加载报告列表失败:', error);
    })
    .finally(() => {
      this.setData({ loading: false });
    });
  },

  /**
   * 查看报告详情
   */
  viewDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/reports/detail/detail?id=${id}`
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
