// pages/reports/list/list.js
const flowApi = require('../../../api/flow');
const scaleApi = require('../../../api/scale');
const authCenter = require('../../../utils/authCenter');

Page({
  data: {
    activeTab: 0, 
    reports: [],
    scales: [],
    loading: false,

    // UI 状态
    showEmpty: false,
    showList: false
  },

  onLoad() {
    this.loadData();
  },

  switchTab(e) {
    const tab = Number(e.currentTarget.dataset.tab);
    if (tab !== this.data.activeTab) {
      this.setData({ activeTab: tab });
      this.loadData();
    }
  },

  loadData() {
    this.setData({ loading: true, showEmpty: false, showList: false });

    const api = this.data.activeTab === 0
      ? flowApi.getAssessmentHistory()
      : scaleApi.getResultsHistory();

    api
      .then(res => {
        let list = Array.isArray(res) ? res : [];

        // 认知报告历史适配前端字段
        if (this.data.activeTab === 0) {
          list = list.map(item => {
            // 类型判断
            let type = '';
            if (item.score_mmse != null) type = 'MMSE';
            else if (item.score_moca != null) type = 'MoCA';
            else if (item.score_scd != null) type = 'SCD';
            else type = '认知测评';

            // 分数拼接
            let summary = '';
            if (type === 'MMSE') summary = `MMSE得分：${item.score_mmse}`;
            else if (type === 'MoCA') summary = `MoCA得分：${item.score_moca}`;
            else if (type === 'SCD') summary = `SCD得分：${item.score_scd}`;
            else summary = '无分数';

            return {
              ...item,
              report_type: type,
              summary,
              overall_risk: '', // 可根据分数映射风险等级，暂留空
            };
          });
        }

        const key = this.data.activeTab === 0 ? 'reports' : 'scales';

        this.setData({
          [key]: list,
          loading: false,
          showList: list.length > 0,
          showEmpty: list.length === 0
        });
      })
      .catch(() => {
        const key = this.data.activeTab === 0 ? 'reports' : 'scales';
        this.setData({
          [key]: [],
          loading: false,
          showList: false,
          showEmpty: true
        });
      });
  }
});
