import { scales } from '../../../utils/scales';
const flowApi = require('../../../api/flow');

// 简化版流程判定逻辑（复刻 flow_step_calculator.py）
function getNextStep(completedScales, scaleResults) {
  // 只支持 SCD_Q9 -> MMSE 流程
  if (!completedScales.includes('SCD_Q9')) {
    return { completed: false, next: 'SCD_Q9', step: 1 };
  }
  const scd = scaleResults['SCD_Q9'];
  if (!scd || typeof scd.is_abnormal === 'undefined') {
    return { completed: false, next: 'SCD_Q9', step: 1 };
  }
  if (!scd.is_abnormal) {
    // SCD 正常，流程结束
    return { completed: true, next: null, step: 'done' };
  }
  if (!completedScales.includes('MMSE')) {
    return { completed: false, next: 'MMSE', step: 2 };
  }
  // SCD 异常且 MMSE 已完成，流程结束
  return { completed: true, next: null, step: 'done' };
}

Page({
  data: {
    scaleOrder: ['SCD_Q9', 'MMSE'],
    scaleList: [
      { key: 'SCD_Q9', name: scales.SCD_Q9.name },
      { key: 'MMSE', name: scales.MMSE.name }
    ],
    currentScaleKey: 'SCD_Q9',
    questions: [],
    selectedOptions: [],
    currentQuestionIndex: 0,
    results: {},
    finished: false,
    loading: true,
    flowStartedAt: null, // 流程开始时间
    flowCompletedAt: null, // 流程完成时间
    submitting: false, // 提交中状态
    submitSuccess: false, // 提交成功状态
    localResult: null, // 本地结果展示
    submitResult: null // 提交结果数据
  },

  onLoad() {
    // 记录流程开始时间
    this.setData({
      flowStartedAt: new Date().toISOString()
    }, () => {
      this.startFlow();
    });
  },

  startFlow() {
    // 初始化流程，加载第一个量表
    this.setData({
      currentScaleKey: 'SCD_Q9',
      results: {},
      finished: false
    }, () => {
      this.loadCurrentScale();
    });
  },

  loadCurrentScale() {
    const { currentScaleKey } = this.data;
    const scale = scales[currentScaleKey];
    const questions = scale.questions || [];
    this.setData({
      questions,
      selectedOptions: new Array(questions.length).fill(-1),
      currentQuestionIndex: 0,
      loading: false
    });
  },

  selectOption(e) {
    const { index } = e.currentTarget.dataset;
    const { currentQuestionIndex, selectedOptions } = this.data;
    if (
      Array.isArray(selectedOptions) &&
      currentQuestionIndex >= 0 &&
      currentQuestionIndex < selectedOptions.length
    ) {
      const updatedOptions = [...selectedOptions];
      updatedOptions[currentQuestionIndex] = index;
      this.setData({ selectedOptions: updatedOptions });
    }
  },

  prevQuestion() {
    if (this.data.currentQuestionIndex > 0) {
      this.setData({
        currentQuestionIndex: this.data.currentQuestionIndex - 1
      });
    }
  },

  nextQuestion() {
    if (this.data.questions.length === 0) {
      wx.showToast({ title: '没有题目', icon: 'none' });
      return;
    }
    if (this.data.selectedOptions[this.data.currentQuestionIndex] === -1) {
      wx.showToast({ title: '请选择答案', icon: 'none' });
      return;
    }
    if (this.data.currentQuestionIndex < this.data.questions.length - 1) {
      this.setData({
        currentQuestionIndex: this.data.currentQuestionIndex + 1
      });
    }
  },

  submitScale() {
    const { selectedOptions, questions, currentScaleKey, results } = this.data;
    if (!Array.isArray(selectedOptions) || selectedOptions.includes(-1)) {
      wx.showToast({ title: '请完成所有题目', icon: 'none' });
      return;
    }
    const scale = scales[currentScaleKey];
    const answers = selectedOptions.map((idx, i) =>
      idx >= 0 ? questions[i].options[idx].value : 0
    );
    const analysis = scale.calc(answers);

    // 调试输出每阶段得分结构体
    console.log(`[${currentScaleKey}] 阶段得分:`, analysis);

    // 保存当前量表结果
    const updatedResults = {
      ...results,
      [currentScaleKey]: { answers, analysis, is_abnormal: analysis.is_abnormal }
    };

    // 判定下一步
    const completedScales = Object.keys(updatedResults);
    const stepInfo = getNextStep(completedScales, updatedResults);

    if (stepInfo.completed) {
      // 流程完成，显示本地结果，延迟后自动提交
      const completedAt = new Date().toISOString();
      this.setData({
        results: updatedResults,
        finished: true,
        flowCompletedAt: completedAt,
        localResult: this.generateLocalResult(updatedResults),
        submitting: true
      }, () => {
        // 3秒后自动提交，给用户时间查看结果
        setTimeout(() => {
          this.submitFlowResult(updatedResults);
        }, 3000);
      });
    } else {
      // 进入下一个量表
      this.setData({
        currentScaleKey: stepInfo.next,
        results: updatedResults,
        loading: true
      }, () => {
        this.loadCurrentScale();
      });
    }
  },

  // 生成本地结果展示
  generateLocalResult(results) {
    let resultText = '';
    let scoreText = '';
    let statusText = '';
    let statusColor = '';

    if (results.SCD_Q9) {
      const scdScore = results.SCD_Q9.analysis.score;
      const scdLevel = results.SCD_Q9.analysis.level;
      const isAbnormal = results.SCD_Q9.analysis.is_abnormal;
      
      scoreText = `SCD-Q9 得分：${scdScore} 分`;
      statusText = `认知状态：${scdLevel}`;
      statusColor = isAbnormal ? '#ff4d4f' : '#52c41a';
      
      if (results.MMSE) {
        const mmseScore = results.MMSE.analysis.score;
        const mmseLevel = results.MMSE.analysis.level;
        scoreText += ` | MMSE 得分：${mmseScore} 分`;
        statusText += ` | MMSE：${mmseLevel}`;
      }
      
      resultText = isAbnormal
        ? '建议进一步认知功能评估，请关注认知健康。'
        : '认知功能正常，请继续保持健康生活方式。';
    }

    return {
      scoreText,
      statusText,
      statusColor,
      resultText,
      timestamp: new Date().toLocaleString('zh-CN')
    };
  },

  async submitFlowResult(results) {
    try {
      // 组装提交数据，字段结构需参考后端模型与 serializer
      const payload = {
        analysis: {},
        started_at: this.data.flowStartedAt || new Date().toISOString(),
        completed_at: this.data.flowCompletedAt || new Date().toISOString()
      };
      
      // 只上传 SCD_Q9 分数和分析
      if (results.SCD_Q9 && results.SCD_Q9.analysis) {
        payload.score_scd = results.SCD_Q9.analysis.score ?? null;
        payload.analysis.scd = results.SCD_Q9.analysis;
      }
      
      // 仅当 MMSE 存在且有分析时上传
      if (results.MMSE && results.MMSE.analysis && Object.keys(results.MMSE.analysis).length > 0) {
        payload.score_mmse = results.MMSE.analysis.score ?? null;
        payload.analysis.mmse = results.MMSE.analysis;
      }
      
      console.log('[FLOW] 最终上传内容:', payload);
      const res = await flowApi.submitCognitiveFlow(payload);
      
      // 更新提交状态 - 保持在结果页面，只显示toast
      this.setData({
        submitting: false,
        submitSuccess: true,
        submitResult: res // 保存提交结果供后续查看
      });
      
    } catch (e) {
      this.setData({
        submitting: false,
        submitSuccess: false
      });
      wx.showToast({ title: '提交失败', icon: 'none' });
    }
  },

  // 手动提交按钮点击事件
  manualSubmit() {
    if (this.data.submitting) return;
    
    const { results } = this.data;
    if (!results || Object.keys(results).length === 0) {
      wx.showToast({ title: '没有可提交的数据', icon: 'none' });
      return;
    }
    
    this.setData({ submitting: true });
    this.submitFlowResult(results);
  }
});