import { mockDailyPlan } from './resources'

export const MOCK_CHAT_INTRO =
  '你好，我是你的雅思 AI 小助手。告诉我目标分数、考试倒计时和薄弱项，我会为你做痛点分析并动态调整今日任务。'

export const QUICK_PROMPTS = [
  '我目标 7 分，还有 20 天考试，帮我定个计划',
  '口语 Part 2 总是卡壳，给我针对性训练',
]

const SPEAKING_DEEP_REPLY = `【痛点分析】：Part 2 卡壳通常是因为缺乏串联线索（Storyline）或过度纠结高级词汇导致流利度（FC）受损。

【解决方案】：我为你准备了「六法串联关键词法」——用 When / Who / What / Why / Feeling / Future 六个锚点串起 2 分钟独白。

【动态微调提示】：系统检测到你当前的备考重心。是否需要我现在帮你重置「今日任务打卡」卡片，将今日的阅读和听力题量减半，并为你塞入 2 轮 Part 2 话题线索专项对练？`

export function resolveMockReply(userText) {
  const text = userText.trim()

  if (text.includes('Part 2') || text.includes('卡壳') || text.includes('口语')) {
    return {
      content: SPEAKING_DEEP_REPLY,
      actions: [
        { id: 'sync-plan', label: '将此计划一键同步至今日打卡清单' },
        { id: 'keep-plan', label: '保持原计划不变' },
      ],
      emitPlan: false,
      emitAdjust: null,
    }
  }

  if (text.includes('阅读') && text.includes('正确率')) {
    return {
      content:
        '【痛点分析】：阅读正确率波动多半来自定位慢与同义替换识别不足。\n\n【解决方案】：建议今日先做 1 篇 Passage 1 限时训练，再用 AI 长难句拆解错题定位段。\n\n【动态微调提示】：我已将阅读任务设为高优先级，可在下方打卡卡片查看。',
      actions: [],
      emitPlan: false,
      emitAdjust: null,
    }
  }

  return {
    content:
      '【计划生成】：已根据你的目标 7 分与 20 天倒计时，生成今日四科任务清单。\n\n【动态微调】：听力精听 + 阅读 Passage 1 + 口语 Part 2 盲考 + 写作 Task 2 已写入下方打卡区，完成后可勾选打卡。',
    actions: [],
    emitPlan: true,
    plan: mockDailyPlan,
    emitAdjust: null,
  }
}

export function resolveActionReply(actionId) {
  if (actionId === 'sync-plan' || actionId === 'confirm-adjust') {
    return {
      content:
        '好的，已为你微调今日任务：阅读、听力题量减半，并新增 2 轮 Part 2 话题线索专项对练。请在下方打卡卡片确认。',
      emitAdjust: 'speaking-focus',
    }
  }
  return {
    content: '已保持原计划不变。如需再次微调，随时告诉我。',
    emitAdjust: null,
  }
}
