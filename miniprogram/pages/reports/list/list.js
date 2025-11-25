// pages/reports/list/list.js
const flowApi = require('../../../api/flow');
const scaleApi = require('../../../api/scale');
const authCenter = require('../../../utils/authCenter');

Page({
  data: {
    reports: [],
    scales: [],
    page: 1,
    pageSize: 10,
    hasMore: true,
    loading: false,
    activeTab: 0 // 0:报告历史 1:量表历史
  },

  onShow() {
    if (!authCenter.logined) {
      authCenter.logout();
      wx.reLaunch({ url: '/pages/login/login' });
      return;
    }
  },

  onLoad() {
    this.loadTabData();
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.setData({ page: this.data.page + 1 });
      this.loadReports();
    }
  },

  /**
   * 加载tab对应数据
   */
  loadTabData() {
    if (this.data.activeTab === 0) {
      this.loadCognitiveRecords();
    } else {
      this.loadScales();
    }
  },

  /**
   * 加载报告列表
   */
  loadCognitiveRecords() {
    if (this.data.loading) {
      console.log('[loadCognitiveRecords] 正在加载中，跳过本次请求');
      return;
    }
    this.setData({ loading: true });
  
    flowApi.getAssessmentHistory()
      .then((res) => {
        console.log('[loadCognitiveRecords] 认知测评历史接口返回:', res);
        const records = (res || []).map(item => ({
          ...item,
          created_at: item.created_at || '',
          updated_at: item.updated_at || ''
        }));
        this.setData({
          reports: this.data.page === 1 ? records : [...this.data.reports, ...records],
          hasMore: records.length >= this.data.pageSize
        });
      })
      .catch((error) => {
        console.error('加载认知测评历史失败:', error);
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  /**
   * 加载量表历史
   */
  loadScales() {
    if (this.data.loading) {
      console.log('[loadScales] 正在加载中，跳过本次请求');
      return;
    }
    this.setData({ loading: true });
  
    scaleApi.getResultsHistory()
      .then((res) => {
        console.log('[loadScales] 量表历史接口返回:', res);
        const scales = res || [];
        this.setData({
          scales: scales,
          hasMore: false // 量表暂不分页
        });
      })
      .catch((error) => {
        console.error('加载量表历史失败:', error);
      })
      .finally(() => {
        this.setData({ loading: false });
      });
  },

  /**
   * 查看报告详情
   */
  viewDetail(e) {
    const { id, type } = e.currentTarget.dataset;
    let url = `/pages/reports/detail/detail?id=${id}`;
    if (type === 'scale') {
      url += '&type=scale';
    }
    wx.navigateTo({ url });
  },

  /**
   * tab切换
   */
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    if (tab === this.data.activeTab) return;
    this.setData({ activeTab: tab, page: 1, hasMore: true });
    this.loadTabData();
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
