import { onUnmounted, ref } from 'vue'

let activeFrame = null

export function createStateFrame() {
  const frame = { slots: [], index: 0, disposed: false }
  frame.begin = () => { frame.index = 0; activeFrame = frame }
  frame.dispose = () => {
    frame.disposed = true
    for (const slot of frame.slots) if (slot?.kind === 'effect') slot.cleanup?.()
  }
  onUnmounted(frame.dispose)
  return frame
}

function nextSlot(kind, create) {
  if (!activeFrame) throw new Error('State hook called outside Vue render')
  const index = activeFrame.index++
  const slot = activeFrame.slots[index] ||= create()
  if (slot.kind !== kind) throw new Error(`State hook order changed at ${index}`)
  return slot
}

export function useState(initial) {
  const slot = nextSlot('state', () => ({ kind: 'state', value: ref(typeof initial === 'function' ? initial() : initial) }))
  const set = (next) => { slot.value.value = typeof next === 'function' ? next(slot.value.value) : next }
  return [slot.value.value, set]
}

export function useRef(initial) {
  const slot = nextSlot('ref', () => {
    const value = ref(initial)
    Object.defineProperty(value, 'current', { get: () => value.value, set: (next) => { value.value = next } })
    return { kind: 'ref', value }
  })
  return slot.value
}

export function useMemo(factory) { return factory() }

export function useEffect(callback, dependencies) {
  const frame = activeFrame
  const slot = nextSlot('effect', () => ({ kind: 'effect', dependencies: null, cleanup: null, revision: 0 }))
  const changed = !slot.dependencies || !dependencies || dependencies.some((value, index) => !Object.is(value, slot.dependencies[index]))
  if (!changed) return
  slot.dependencies = dependencies?.slice() || null
  const revision = ++slot.revision
  queueMicrotask(() => {
    if (frame.disposed || slot.revision !== revision) return
    slot.cleanup?.()
    slot.cleanup = callback() || null
  })
}
