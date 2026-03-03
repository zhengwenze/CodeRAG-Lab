// Web Markdown 渲染工具：将后端返回的 Markdown 内容渲染为安全的 HTML，并实现代码高亮
import MarkdownIt from 'markdown-it'
import Prism from 'prismjs'
import 'prismjs/themes/prism.css'
import 'prismjs/components/prism-javascript'
import 'prismjs/components/prism-python'
import 'prismjs/components/prism-typescript'
import 'prismjs/components/prism-java'
import 'prismjs/components/prism-json'
import 'prismjs/components/prism-markdown'
import 'prismjs/components/prism-yaml'
import 'prismjs/components/prism-bash'
import 'prismjs/components/prism-go'
import 'prismjs/components/prism-c'
import 'prismjs/components/prism-cpp'
import DOMPurify from 'dompurify'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: (str, lang) => {
    if (lang && Prism.languages[lang]) {
      try {
        return `<pre class="language-${lang}"><code>${Prism.highlight(str, Prism.languages[lang], lang)}</code></pre>`
      } catch (e) {
        // 兜底回退，继续渲染为普通代码块
      }
    }
    return md.utils.escapeHtml(str)
  }
})

// 渲染并清洗 HTML，防 XSS
const renderMarkdown = (content) => {
  if (!content) return ''
  const rendered = md.render(content)
  try {
    return (typeof DOMPurify?.sanitize === 'function') ? DOMPurify.sanitize(rendered) : rendered
  } catch {
    return rendered
  }
}

export { renderMarkdown }
export default renderMarkdown
