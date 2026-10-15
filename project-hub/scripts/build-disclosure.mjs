import { build } from 'vite'
import { copyFile, mkdir } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'

const root = resolve(import.meta.dirname, '..')
const output = resolve(root, 'dist', 'knowledge-disclosure.js')
await build({
  root,
  configFile: false,
  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
    __VUE_OPTIONS_API__: true,
    __VUE_PROD_DEVTOOLS__: false,
    __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
  },
  build: {
    emptyOutDir: false,
    outDir: resolve(root, 'dist'),
    lib: { entry: resolve(root, 'src', 'KnowledgeDisclosure.js'), formats: ['es'], fileName: () => 'knowledge-disclosure.js' },
  },
})

for (const target of [
  resolve(root, '..', 'rag-assistant', 'frontend', 'public', 'knowledge-disclosure.js'),
  resolve(root, '..', 'yugan-agent', 'src', 'yugan_agent', 'web', 'knowledge-disclosure.js'),
]) {
  await mkdir(dirname(target), { recursive: true })
  await copyFile(output, target)
}
