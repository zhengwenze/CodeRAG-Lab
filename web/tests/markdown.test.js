import { describe, it, expect } from 'vitest'
import { renderMarkdown } from '../src/utils/markdown.js'

describe('Markdown 渲染', () => {
  it('应对代码块进行高亮显示', () => {
    const md = '```js\nconsole.log(\'hi\')\n```'
    const html = renderMarkdown(md)
    expect(html).toContain('<pre class="language-js"')
    expect(html).toContain('console.log')
  })

  it('应对 HTML 注入进行过滤', () => {
    const md = '`<script>alert("xss")</script>`'
    const html = renderMarkdown(md)
    expect(html).not.toContain('<script')
  })
})
