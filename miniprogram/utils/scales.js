// 量表 util，包含 ADL、SCD-Q9、MMSE 全部题目，便于前端统一渲染与评分
export const scales = {
  ADL: {
    name: "日常生活能力量表 (ADL)",
    code: "ADL",
    description: "日常生活能力评估量表",
    questions: [
      {
        id: 1, question: "自己搭公共汽车", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 2, question: "到家附近的地方去（步行范围）", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 3, question: "自己做饭（包括生火）", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 4, question: "做家务", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 5, question: "吃药", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 6, question: "吃饭", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 7, question: "穿脱衣服", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 8, question: "梳头、刷牙等", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 9, question: "洗自己的衣服", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 10, question: "在平坦的室内走动", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 11, question: "上下楼梯", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 12, question: "上下床、坐下或站起", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 13, question: "提水煮饭或洗澡", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 14, question: "洗澡（水已放好）", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 15, question: "剪脚趾甲", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 16, question: "逛街，购物", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 17, question: "定时去厕所", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 18, question: "打电话", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 19, question: "处理自己的钱财", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      },
      {
        id: 20, question: "独自在家", options: [
          { text: "自己可以做", value: 1 }, { text: "有些困难", value: 2 }, { text: "需要帮助", value: 3 }, { text: "根本没法做", value: 4 }
        ]
      }
    ],
    calc: (answers) => {
      const score = answers.reduce((sum, v) => sum + v, 0);
      let level, interpretation;
      if (score < 20) {
        level = "完全独立";
        interpretation = "继续保持良好生活习惯";
      } else if (score < 40) {
        level = "轻度依赖";
        interpretation = "建议适当锻炼，保持独立性";
      } else if (score < 60) {
        level = "中度依赖";
        interpretation = "建议家属协助日常活动，关注健康状况";
      } else {
        level = "重度依赖";
        interpretation = "建议专业护理，密切关注健康变化";
      }
      return { score, level, interpretation };
    }
  },
  SCD_Q9: {
    name: "SCD-Q9 问卷",
    code: "SCD-Q9",
    description: "主观认知障碍筛查问卷",
    questions: [
      {
        id: 1, question: "你认为自己有记忆问题吗？", options: [
          { text: "是", value: 1 }, { text: "否", value: 0 }
        ]
      },
      {
        id: 2, question: "你回忆3-5天前的对话有困难吗？", options: [
          { text: "是", value: 1 }, { text: "否", value: 0 }
        ]
      },
      {
        id: 3, question: "你觉得自己近两年有记忆问题吗？", options: [
          { text: "是", value: 1 }, { text: "否", value: 0 }
        ]
      },
      {
        id: 4, question: "下列问题经常发生吗：忘记对个人来说重要的日期（如生日等）", options: [
          { text: "经常", value: 1 }, { text: "偶尔", value: 0.5 }, { text: "从未", value: 0 }
        ]
      },
      {
        id: 5, question: "下列问题经常发生吗：忘记常用号码（手机号、身份证号等）", options: [
          { text: "经常", value: 1 }, { text: "偶尔", value: 0.5 }, { text: "从未", value: 0 }
        ]
      },
      {
        id: 6, question: "总的来说，你是否认为自己对要做的事或要说的话容易忘记？", options: [
          { text: "是", value: 1 }, { text: "否", value: 0 }
        ]
      },
      {
        id: 7, question: "下列问题经常发生吗：到了商店忘记要买什么？", options: [
          { text: "经常", value: 1 }, { text: "偶尔", value: 0.5 }, { text: "从未", value: 0 }
        ]
      },
      {
        id: 8, question: "你认为自己的记忆力比5年前要差吗？", options: [
          { text: "是", value: 1 }, { text: "否", value: 0 }
        ]
      },
      {
        id: 9, question: "你认为自己越来越记不住东西放哪儿了吗？", options: [
          { text: "是", value: 1 }, { text: "否", value: 0 }
        ]
      }
    ],
    calc: (answers) => {
      const score = answers.reduce((sum, v) => sum + v, 0);
      const threshold = 5;
      const is_abnormal = score > threshold;
      const level = is_abnormal ? "需进一步评估" : "正常";
      const interpretation = is_abnormal
        ? `您的SCD-Q9评分为${score}分（>${threshold}分），提示可能存在主观认知下降，建议进行进一步的认知功能评估。`
        : `您的SCD-Q9评分为${score}分（≤${threshold}分），未发现明显的主观认知下降，建议保持健康生活方式。`;
      return { score, level, is_abnormal, interpretation };
    }
  },
  MMSE: {
    name: "简易智能状态检查量表 (MMSE)",
    code: "MMSE",
    description: "全面认知功能评估量表",
    questions: [
      {
        id: 1, question: "现在是哪一年？", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 2, question: "现在是哪一季？", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 3, question: "现在是几月份？", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 4, question: "今天是几号？", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 5, question: "今天是星期几？", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 6, question: "我们在哪个省（市）？", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 7, question: "我们在哪个县（区）？", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 8, question: "我们在哪个乡（镇、街道）？", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 9, question: "我们在几楼？", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 10, question: "这里是什么地方？", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 11, question: "复述：皮球", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 12, question: "复述：国旗", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 13, question: "复述：树木", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 14, question: "100减7等于多少？", options: [
          { text: "正确（93）", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 15, question: "93减7等于多少？", options: [
          { text: "正确（86）", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 16, question: "86减7等于多少？", options: [
          { text: "正确（79）", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 17, question: "79减7等于多少？", options: [
          { text: "正确（72）", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 18, question: "72减7等于多少？", options: [
          { text: "正确（65）", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 19, question: "回忆：皮球", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 20, question: "回忆：国旗", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 21, question: "回忆：树木", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 22, question: "命名：手表", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 23, question: "命名：铅笔", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 24, question: "复述：四十四只石狮子", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 25, question: "执行指令：用右手拿纸", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 26, question: "执行指令：将纸对折", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 27, question: "执行指令：放在大腿上", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 28, question: "阅读并执行：闭上您的眼睛", options: [
          { text: "正确", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 29, question: "写一句完整的句子", options: [
          { text: "正确（有主语、谓语，有意义）", value: 1 }, { text: "错误", value: 0 }
        ]
      },
      {
        id: 30, question: "复制图案", options: [
          { text: "正确（画出完整图形）", value: 1 }, { text: "错误", value: 0 }
        ]
      }
    ],
    calc: (answers, education = "初中") => {
      const score = answers.reduce((sum, v) => sum + v, 0);
      let threshold = 24;
      if (education.includes("文盲")) threshold = 17;
      else if (education.includes("小学")) threshold = 20;
      let level = "重度认知障碍";
      if (score >= 27) level = "正常";
      else if (score >= 21) level = "轻度认知障碍";
      else if (score >= 10) level = "中度认知障碍";
      const is_abnormal = score <= threshold;
      const interpretation = is_abnormal
        ? `根据您的教育程度（${education}），MMSE评分${score}分低于校正阈值${threshold}分，提示${level}，建议进一步评估。`
        : `您的MMSE评分为${score}分，认知功能评估结果为${level}。`;
      return { score, level, is_abnormal, threshold, interpretation };
    }
  }
};


// 每日情绪测试题目
export const moodtestQ = [
  {
    key: 'depression',
    title: '抑郁水平',
    question: '在过去的几个小时里，您是否觉得心情低落，或者对平常喜欢做的事情提不起兴趣？',
    type: 'radio',
    options: [
      { text: '没有', value: 0, desc: '完全没有这种感觉' },
      { text: '轻微', value: 1, desc: '偶尔有轻微的感觉' },
      { text: '中等', value: 2, desc: '有明显的感觉，影响日常生活' },
      { text: '很严重', value: 3, desc: '感觉非常强烈，严重影响生活' }
    ]
  },
  {
    key: 'anxiety',
    title: '焦虑水平',
    question: '在过去的几个小时里，您是否感到紧张、焦虑，或者坐立不安？',
    type: 'scale',
    min: 0,
    max: 10,
    minText: '完全没有',
    maxText: '非常严重',
    desc: '请根据您的实际感受选择0-10之间的数值'
  },
  {
    key: 'energy',
    title: '精力状态',
    question: '在过去的几个小时里，您是否觉得没有精力，容易感到疲劳？',
    type: 'radio',
    options: [
      { text: '没有', value: 0, desc: '精力充沛，没有疲劳感' },
      { text: '有一点', value: 1, desc: '偶尔感到轻微疲劳' },
      { text: '明显', value: 2, desc: '经常感到疲劳，影响活动' },
      { text: '非常严重', value: 3, desc: '极度疲劳，无法正常生活' }
    ]
  },
  {
    key: 'sleep',
    title: '睡眠质量',
    question: '请回顾今天（或昨晚），您的睡眠情况如何？',
    type: 'radio',
    options: [
      { text: '非常好', value: 0, desc: '睡眠质量极佳，醒来精神饱满' },
      { text: '比较好', value: 1, desc: '睡眠质量良好，基本恢复精力' },
      { text: '一般', value: 2, desc: '睡眠质量一般，略有不足' },
      { text: '不太好', value: 3, desc: '睡眠质量较差，影响精神状态' },
      { text: '很差', value: 4, desc: '睡眠质量极差，严重缺乏休息' }
    ]
  },
  // 主观情绪问题 - 整合到标准问题流程中
  {
    key: 'mainMood',
    title: '主观情绪',
    question: '您现在主要是什么感觉？',
    type: 'mood',
    options: [
      { value: '快乐/愉快', text: '快乐/愉快', icon: 'smile' },
      { value: '平静/放松', text: '平静/放松', icon: 'calm' },
      { value: '难过/悲伤', text: '难过/悲伤', icon: 'cry' },
      { value: '焦虑/担心', text: '焦虑/担心', icon: 'nervous' },
      { value: '易怒/烦躁', text: '易怒/烦躁', icon: 'angry' },
      { value: '疲惫/无力', text: '疲惫/无力', icon: 'tired' },
      { value: '其他', text: '其他', icon: 'other' }
    ]
  },
  {
    key: 'moodIntensity',
    title: '情绪强度',
    question: '您当前感受的强度如何？',
    type: 'radio',
    options: [
      { value: 1, text: '轻微', desc: '情绪感受较弱' },
      { value: 2, text: '中等', desc: '情绪感受适中' },
      { value: 3, text: '明显', desc: '情绪感受较强' }
    ]
  },
  {
    key: 'moodSupplementTags',
    title: '情绪原因',
    question: '导致此情绪的原因（可多选）',
    type: 'checkbox',
    options: [
      { value: '身体不适', text: '身体不适', desc: '' },
      { value: '家庭事务', text: '家庭事务', desc: '' },
      { value: '记忆困扰', text: '记忆困扰', desc: '' },
      { value: '睡眠不好', text: '睡眠不好', desc: '' },
      { value: '工作/学习压力', text: '工作/学习压力', desc: '' },
      { value: '其他', text: '其他', desc: '' }
    ]
  },
  {
    key: 'moodSupplementText',
    title: '补充说明',
    question: '请简短写下导致此情绪的事情（可选）',
    type: 'text',
    placeholder: '可填写具体内容（可跳过）'
  }
];