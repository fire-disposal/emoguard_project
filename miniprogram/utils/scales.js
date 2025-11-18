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