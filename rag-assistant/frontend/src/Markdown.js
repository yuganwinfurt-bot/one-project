import { h } from 'vue'
import { micromark } from 'micromark'
import { gfm } from 'micromark-extension-gfm'

export default function Markdown(props) {
  // micromark escapes raw HTML and filters dangerous protocols by default.
  const content = String(props.content || '')
  return h('div', { innerHTML: micromark(content, { extensions: [gfm()] }) })
}
