// pages/reports/detail/detail.js
const reportApi = require('../../../api/report');
const { request } = require('../../../utils/request');

Page({
  data: {
    report: null,
    loading: true,
    historyType: 'flow',
    historyList: []
  },

  onLoad(options) {
    const { id } = options;
    if (id) {
      this.loadReport(id);
    }
  },

  /**
   * 加载报告详情
   */
  loadReport(id) {
    this.setData({ loading: true });

    reportApi.getReport(id)
      .then((res) => {
        this.setData({ report: res });
        // 加载历史记录
        this.loadHistory();
      })
      .catch((error) => {
        console.error('加载报告详情失败:', error);
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
   * 历史记录类型切换
   */
  onSwitchType(e) {
    const type = e.currentTarget.dataset.type;
    if (type === this.data.historyType) return;
    this.setData({ historyType: type });
    this.loadHistory();
  },

  /**
   * 加载历史记录
   */
  async loadHistory() {
    this.setData({ loading: true, historyList: [] });
    const { historyType, report } = this.data;
    const userId = report && report.user_id;
    if (!userId) {
      this.setData({ loading: false });
      return;
    }
    try {
      let list = [];
      if (historyType === 'flow') {
        list = await request({
          url: '/api/cognitive/history',
          method: 'GET',
          data: { user_id: userId }
        });
        list = (list || []).map(item => ({
          id: item.id,
          type: 'flow',
          name: item.name || item.flow_name,
          date: item.date || item.created_at,
          score: item.score
        }));
      } else {
        list = await request({
          url: '/api/scale/results/history',
          method: 'GET',
          data: { user_id: userId }
        });
        list = (list || []).map(item => ({
          id: item.id,
          type: 'scale',
          name: item.scale_name,
          date: item.date || item.created_at,
          score: item.score
        }));
      }
      this.setData({ historyList: list });
    } catch (e) {
      this.setData({ historyList: [] });
    } finally {
      this.setData({ loading: false });
    }
  }
});
