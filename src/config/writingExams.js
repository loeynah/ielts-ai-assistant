const ASSET = '/assets/writing'

function task1(id, title, prompt, imageFile, minutes = 20) {
  return {
    id,
    type: 'task1',
    title,
    minutes,
    minWords: 150,
    instruction: `You should spend about ${minutes} minutes on this task.`,
    prompt,
    imageUrl: `${ASSET}/${imageFile}`,
  }
}

function task2(id, title, topic, minutes = 40) {
  return {
    id,
    type: 'task2',
    title,
    minutes,
    minWords: 250,
    instruction: `You should spend about ${minutes} minutes on this task.`,
    prompt: [
      'Write about the following topic:',
      topic,
      'Give reasons for your answer and include any relevant examples from your own knowledge or experience.',
      `Write at least ${250} words.`,
    ].join('\n\n'),
    imageUrl: null,
  }
}

export const WRITING_EXAM_SETS = [
  {
    id: 'set-1',
    title: '套题 1',
    subtitle: 'Melbourne 社会中心 · 竞争与合作',
    task1: task1(
      'set-1-t1',
      'Melbourne 社会中心活动人数',
      'The graph below gives information on the numbers of participants for different activities at one social centre in Melbourne, Australia for the period 2000 to 2020.\n\nSummarise the information by selecting and reporting the main features, and make comparisons where relevant.\n\nWrite at least 150 words.',
      'TASK1-1.png',
    ),
    task2: task2(
      'set-1-t2',
      '竞争 vs 合作',
      'Some people think that competition at work, at school and in daily life is a good thing. Others believe that we should try to cooperate more, rather than competing against each other.\n\nDiscuss both these views and give your own opinion.',
    ),
  },
  {
    id: 'set-2',
    title: '套题 2',
    subtitle: '港口变迁图 · 缩短工作周',
    task1: task1(
      'set-2-t1',
      '港口 2000 与今日对比',
      'The plans below show a harbour in 2000 and how it looks today.\n\nSummarise the information by selecting and reporting the main features, and make comparisons where relevant.\n\nWrite at least 150 words.',
      'TASK2-1.png',
    ),
    task2: task2(
      'set-2-t2',
      '缩短工作周',
      'The working week should be shorter and workers should have a longer weekend.\n\nDo you agree or disagree?',
    ),
  },
  {
    id: 'set-3',
    title: '套题 3',
    subtitle: '生物燃料流程图 · 储蓄观念',
    task1: task1(
      'set-3-t1',
      '乙醇生物燃料生产流程',
      'The diagram below shows how a biofuel called ethanol is produced.\n\nSummarise the information by selecting and reporting the main features, and make comparisons where relevant.\n\nWrite at least 150 words.',
      'TASK3-1.png',
    ),
    task2: task2(
      'set-3-t2',
      '为未来储蓄',
      'It is important for everyone, including young people, to save money for their future.\n\nTo what extent do you agree or disagree with this statement?',
    ),
  },
]

export const WRITING_DEMO_TASK2 = [
  task2(
    'demo-driverless',
    '无人驾驶汽车',
    'It will be better to have wide use of driverless cars for individuals and society.\n\nTo what extent do you agree or disagree?',
  ),
  task2(
    'demo-community',
    '义务社区服务',
    'Some people believe that unpaid community service should be a compulsory part of high school programmes (e.g. working for a charity, improving the neighborhood, teaching sports to younger children).\n\nTo what extent do you agree or disagree?',
  ),
]

export function getWritingTask(setId, taskKey) {
  const examSet = WRITING_EXAM_SETS.find((s) => s.id === setId)
  if (!examSet) return null
  return examSet[taskKey] ?? null
}

export function getDemoTask(demoId) {
  return WRITING_DEMO_TASK2.find((t) => t.id === demoId) ?? null
}

export function isDemoId(id) {
  return WRITING_DEMO_TASK2.some((t) => t.id === id)
}

export const WRITING_MENU_ITEMS = [
  ...WRITING_EXAM_SETS.map((s) => ({
    id: s.id,
    kind: 'set',
    label: s.title,
    subtitle: s.subtitle,
  })),
  ...WRITING_DEMO_TASK2.map((d) => ({
    id: d.id,
    kind: 'demo',
    label: d.title,
    subtitle: '独立大作文',
  })),
]
