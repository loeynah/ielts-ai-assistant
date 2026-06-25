/** 本地听力题库（assets/listening） */
export const LISTENING_BASE = '/assets/listening'

export const listeningLessons = [
  {
    lessonId: '103',
    folder: '103. P1 International Club',
    title: 'P1 International Club',
    section: 'Part 1',
    htmlFile: '103. P1 International Club.html',
    audioFile: 'audio.mp3',
    pdfFile: '103. P1 International Club.pdf',
    description: '国际俱乐部信息填空 · 适合基础定位与同义替换训练',
  },
  {
    lessonId: '104',
    folder: '104. P2 Riding for the Disabled (RDA)',
    title: 'P2 Riding for the Disabled (RDA)',
    section: 'Part 2',
    htmlFile: '104. P2 Riding for the Disabled (RDA).html',
    audioFile: 'audio.mp3',
    pdfFile: '104. P2 Riding for the Disabled (RDA).pdf',
    description: '残疾人骑马协会介绍 · 地图与流程信息题',
  },
  {
    lessonId: 'p3-103',
    folder: '3. P3 Shampoo Marketing Project',
    title: 'Part 3 Lesson 103',
    section: 'Part 3',
    htmlFile: '3. P3 Shampoo Marketing Project.html',
    audioFile: 'audio.mp3',
    pdfFile: '3. P3 Shampoo Marketing Project.pdf',
    description: '洗发水营销项目 · 多人讨论与观点匹配',
  },
  {
    lessonId: '105',
    folder: '105. P4 Mass Strandings of Whales and Dolphins',
    title: 'P4 Mass Strandings of Whales and Dolphins',
    section: 'Part 4',
    htmlFile: '105. P4 Mass Strandings of Whales and Dolphins.html',
    audioFile: 'audio.mp3',
    pdfFile: '105. P4 Mass Strandings of Whales and Dolphins.pdf',
    description: '鲸豚集体搁浅学术讲座 · 适合精听与逻辑词追踪',
  },
]

export function getLessonById(lessonId) {
  return listeningLessons.find((l) => l.lessonId === lessonId) || listeningLessons[0]
}

/** 拼接本地静态资源 URL（路径含空格需编码） */
export function lessonAssetUrl(lesson, fileName) {
  const folder = encodeURIComponent(lesson.folder)
  const file = encodeURIComponent(fileName)
  return `${LISTENING_BASE}/${folder}/${file}`
}

export function lessonHtmlUrl(lesson) {
  return lessonAssetUrl(lesson, lesson.htmlFile)
}

export function lessonAudioUrl(lesson) {
  return lessonAssetUrl(lesson, lesson.audioFile)
}
