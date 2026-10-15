import { defineCustomElement, h } from 'vue'

const icon = (name) => h('svg', {
  'aria-hidden': 'true', viewBox: '0 0 24 24', width: 14, height: 14,
  fill: 'none', stroke: 'currentColor', 'stroke-width': 2,
  'stroke-linecap': 'round', 'stroke-linejoin': 'round',
}, name === 'chevron'
  ? [h('path', { d: 'm6 9 6 6 6-6' })]
  : [h('path', { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' }),
    h('path', { d: 'M14 2v6h6M8 13h8M8 17h8' })])

const KnowledgeDisclosure = defineCustomElement({
  props: {
    label: { type: String, default: '查看详情' },
    expanded: { type: Boolean, default: false },
  },
  styles: [`
    :host { display: block; margin-top: 12px; color: #40566a; font-family: inherit; }
    details { overflow: hidden; border: 1px solid #dbe4e1; border-radius: 9px; background: #fbfcf9; }
    summary { height: 35px; display: flex; align-items: center; gap: 7px; padding: 0 10px;
      list-style: none; color: #147c69; font-size: 10px; font-weight: 500; cursor: pointer; }
    summary::-webkit-details-marker { display: none; }
    summary svg:first-child { color: #1a9c81; }
    summary svg:last-child { margin-left: auto; transition: transform .15s; }
    details[open] summary svg:last-child { transform: rotate(180deg); }
    summary:focus-visible { outline: 2px solid #1a9c81; outline-offset: -2px; }
  `],
  setup(props) {
    return () => h('details', { open: props.expanded }, [
      h('summary', [icon('document'), h('span', props.label), icon('chevron')]),
      h('slot'),
    ])
  },
})

if (!customElements.get('knowledge-disclosure')) {
  customElements.define('knowledge-disclosure', KnowledgeDisclosure)
}
