/** IELTS 写作字数统计：按空白分隔的英文单词 */
export function countWords(text) {
  const trimmed = (text || '').trim()
  if (!trimmed) return 0
  return trimmed.split(/\s+/).filter(Boolean).length
}
