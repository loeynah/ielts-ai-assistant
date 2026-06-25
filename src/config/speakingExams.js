/**
 * 口语三套演示真题（源自 5-8月口语题目.md）
 * 每套含完整 Part 1 → Part 2 → Part 3 逻辑链
 */
export const SPEAKING_EXAMS = [
  {
    id: 'exam-01',
    title: 'Set 1 · Clothing & Communication',
    part1Topic: 'Clothing',
    part1: [
      'What kind of clothes do you like to wear?',
      'Do you prefer to wear comfortable and casual clothes or formal clothes?',
      'Do you like wearing T-shirts?',
    ],
    part2: {
      title: 'Describe a person who has not replied to your messages for a long time',
      cues: [
        'Who he/she is',
        'What message you sent him/her',
        'Did he/she finally reply to you',
        'And explain how you felt about him/her',
      ],
    },
    part3: [
      'In what situations do people spend a long time responding to others\' messages?',
      'Why do some people prefer sending a message instead of making a call?',
    ],
  },
  {
    id: 'exam-02',
    title: 'Set 2 · Science & Languages',
    part1Topic: 'Science',
    part1: [
      'Do you like science?',
      'Which science subject is interesting to you?',
      'What kinds of interesting things have you done with science?',
    ],
    part2: {
      title: 'Describe a person who is good at learning and speaking new languages',
      cues: [
        'How you got to know him/her',
        'How he/she learns a new language',
        'What languages he/she can speak',
        'And explain how you feel about him/her',
      ],
    },
    part3: [
      'Are there many people who can speak foreign languages in your country?',
      'Does speaking other languages help at work?',
    ],
  },
  {
    id: 'exam-03',
    title: 'Set 3 · Parks & Ambition',
    part1Topic: 'Parks',
    part1: [
      'Did you like going to parks as a child?',
      'Do you still like going to parks now?',
      'Would you like to see more parks in your city?',
    ],
    part2: {
      title: 'Describe an ambition you have had for a long time',
      cues: [
        'What it is',
        'What you did for it',
        'When you can achieve it',
        'And explain why you have this ambition',
      ],
    },
    part3: [
      'What kinds of ambitions do people have?',
      'Why are young people ambitious for higher positions?',
    ],
  },
]

export function getSpeakingExam(id) {
  return SPEAKING_EXAMS.find((e) => e.id === id) || SPEAKING_EXAMS[0]
}

/** 计时配置（秒） */
export const SPEAKING_TIMERS = {
  part1Answer: 30,
  part2Prep: 60,
  part2Record: 120,
  part3Answer: 45,
}
