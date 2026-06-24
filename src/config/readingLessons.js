/** 阅读二级选题：Passage → Lesson（映射 zyz 阅读题库 examId） */
export const READING_PASSAGES = [
  {
    id: 'P1',
    label: 'Passage 1',
    lessons: [
      {
        id: 'p1-lesson-1',
        examId: 'p1-high-01',
        label: 'Lesson 1',
        title: 'A Brief History of Tea 茶叶简史',
      },
      {
        id: 'p1-lesson-2',
        examId: 'p1-high-05',
        label: 'Lesson 2',
        title: 'Katherine Mansfield 新西兰作家',
      },
    ],
  },
  {
    id: 'P2',
    label: 'Passage 2',
    lessons: [
      {
        id: 'p2-lesson-1',
        examId: 'p2-low-06',
        label: 'Lesson 1',
        title: 'Biomimicry 仿生学',
      },
      {
        id: 'p2-lesson-2',
        examId: 'p2-high-09',
        label: 'Lesson 2',
        title: 'Early Approaches to Organisational Design',
      },
    ],
  },
  {
    id: 'P3',
    label: 'Passage 3',
    lessons: [
      {
        id: 'p3-lesson-1',
        examId: 'p3-high-03',
        label: 'Lesson 1',
        title: 'What makes a musical expert 音乐天赋',
      },
      {
        id: 'p3-lesson-2',
        examId: 'p3-high-04',
        label: 'Lesson 2',
        title: 'Yawning 打呵欠',
      },
    ],
  },
]

export function getPassageById(id) {
  return READING_PASSAGES.find((p) => p.id === id) || READING_PASSAGES[0]
}

export function findLesson(passageId, lessonId) {
  const passage = getPassageById(passageId)
  return passage.lessons.find((l) => l.id === lessonId) || null
}
