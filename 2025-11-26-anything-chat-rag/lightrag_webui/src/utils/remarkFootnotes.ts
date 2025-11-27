/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// eslint-disable  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZEdkWVlnPT06YTFkMzhkYmY=

import { visit } from 'unist-util-visit'
import type { Plugin } from 'unified'
import type { Root, Text } from 'mdast'
// eslint-disable  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZEdkWVlnPT06YTFkMzhkYmY=

// Simple footnote plugin for remark - only renders inline citations
export const remarkFootnotes: Plugin<[], Root> = () => {
  return (tree: Root) => {
    // Find footnote references and replace them with inline citations
    visit(tree, 'text', (node: Text, index, parent) => {
      if (!parent || typeof index !== 'number') return

      const text = node.value
      const footnoteRegex = /\[\^([^\]]+)\]/g
      let match
      const replacements: any[] = []
      let lastIndex = 0

      while ((match = footnoteRegex.exec(text)) !== null) {
        const [fullMatch, id] = match
        const startIndex = match.index!

        // Add text before footnote
        if (startIndex > lastIndex) {
          replacements.push({
            type: 'text',
            value: text.slice(lastIndex, startIndex)
          })
        }

        // Check if there's another footnote immediately following this one
        const nextIndex = startIndex + fullMatch.length
        const remainingText = text.slice(nextIndex)
        const hasConsecutiveFootnote = /^\[\^[^\]]+\]/.test(remainingText)

        // Add footnote reference as HTML with placeholder link
        const footnoteHtml = `<sup><a href="#footnote-${id}" class="footnote-ref">${id}</a></sup>`

        // Add spacing if there's a consecutive footnote
        const htmlWithSpacing = hasConsecutiveFootnote
          ? footnoteHtml + '&nbsp;'
          : footnoteHtml

        replacements.push({
          type: 'html',
          value: htmlWithSpacing
        })

        lastIndex = startIndex + fullMatch.length
      }

      // Add remaining text
      if (lastIndex < text.length) {
        replacements.push({
          type: 'text',
          value: text.slice(lastIndex)
        })
      }

      // Replace the text node if we found footnotes
      if (replacements.length > 1) {
        parent.children.splice(index, 1, ...replacements)
      }
    })
  }
}
// TODO  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZEdkWVlnPT06YTFkMzhkYmY=
