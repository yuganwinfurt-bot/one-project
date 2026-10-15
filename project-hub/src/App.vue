<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { projects } from './projects.js'

const localPreview = ['127.0.0.1', 'localhost', '::1', '[::1]'].includes(window.location.hostname)
const psbNumber = import.meta.env.VITE_PSB_RECORD_NUMBER || ''
const psbId = import.meta.env.VITE_PSB_RECORD_ID || ''
const cardTones = ['navy', 'mint', 'paper']
const role = ref('guest')
const authLoading = ref(true)
const authAvailable = ref(false)
const loginOpen = ref(false)
const loginBusy = ref(false)
const loginError = ref('')
const username = ref('')
const password = ref('')

async function refreshAuth() {
  authLoading.value = true
  try {
    const response = await fetch('/api/auth/status', { credentials: 'include' })
    if (!response.ok) throw new Error('无法读取当前身份')
    const result = await response.json()
    role.value = result.role === 'admin' ? 'admin' : 'guest'
    authAvailable.value = true
  } catch {
    authAvailable.value = false
  } finally {
    authLoading.value = false
  }
}

function openLogin() {
  loginError.value = ''
  username.value = ''
  password.value = ''
  loginOpen.value = true
}

function closeLogin() {
  if (loginBusy.value) return
  loginOpen.value = false
  password.value = ''
  loginError.value = ''
}

async function submitLogin() {
  if (loginBusy.value) return
  loginBusy.value = true
  loginError.value = ''
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value }),
    })
    const result = await response.json().catch(() => ({}))
    if (!response.ok) {
      const message = result.detail === 'Not Found'
        ? '登录服务暂不可用，请稍后重试'
        : result.detail || '登录失败，请检查账号或密码'
      throw new Error(message)
    }
    role.value = 'admin'
    authAvailable.value = true
    loginOpen.value = false
    password.value = ''
  } catch (error) {
    loginError.value = error.message || '登录服务暂不可用，请稍后重试'
  } finally {
    loginBusy.value = false
  }
}

async function logout() {
  if (authLoading.value) return
  authLoading.value = true
  try {
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
    })
    if (!response.ok) throw new Error('退出失败')
    role.value = 'guest'
  } catch {
    await refreshAuth()
  } finally {
    authLoading.value = false
  }
}

async function handleIdentityClick() {
  if (authLoading.value) return
  if (!authAvailable.value) {
    await refreshAuth()
    return
  }
  if (role.value === 'admin') await logout()
  else openLogin()
}

function refreshAuthOnFocus() {
  void refreshAuth()
}

onMounted(() => {
  void refreshAuth()
  window.addEventListener('focus', refreshAuthOnFocus)
})
onBeforeUnmount(() => window.removeEventListener('focus', refreshAuthOnFocus))

function projectHref(project) {
  const address = localPreview ? project.localUrl || project.publicUrl : project.publicUrl
  if (!address) return ''
  try {
    const url = new URL(address, window.location.href)
    if (!['http:', 'https:'].includes(url.protocol)) return ''
    if (!localPreview && /^(localhost|\[?::1\]?|0\.0\.0\.0|127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)/i.test(url.hostname)) return ''
    return url.href
  } catch {
    return ''
  }
}

function cardTone(project, index) {
  return `tone-${cardTones.includes(project.tone) ? project.tone : cardTones[index % cardTones.length]}`
}

</script>

<template>
  <div class="site-shell">
    <header class="site-header">
      <a class="brand" href="#top" aria-label="项目首页">
        <span class="brand-mark">P<span>·</span>L</span>
        <span class="brand-name">项目作品集 <small>PROJECT PORTFOLIO</small></span>
      </a>
      <nav aria-label="主导航">
        <a href="#projects">项目介绍</a>
        <a href="#open">项目入口</a>
      </nav>
      <div class="identity-control">
        <button class="identity-control-button" :class="{ 'identity-admin': role === 'admin', 'identity-unavailable': !authAvailable && !authLoading }" type="button" :disabled="authLoading" aria-live="polite" @click="handleIdentityClick">
          {{ authLoading ? '正在读取身份…' : !authAvailable ? '身份状态未知 · 重试' : `当前身份：${role === 'admin' ? '管理员' : '游客'} · ${role === 'admin' ? '退出' : '登录'}` }}
        </button>
      </div>
    </header>

    <main id="top">
      <section class="hero section-wrap" aria-labelledby="hero-title">
        <div class="hero-copy">
          <div class="eyebrow"><span class="live-dot"></span> {{ projects.length }} PROJECTS · ONE ENTRY</div>
          <h1 id="hero-title">智能应用实践，<br /><em>面向真实场景。</em></h1>
          <p class="hero-lead">围绕智能体任务执行与知识库问答，构建可本地运行的应用系统，涵盖模型接入、工具编排、文档检索与来源追踪。</p>
          <div class="hero-note"><span>PROJECT INDEX</span><span>{{ String(projects.length).padStart(2, '0') }} / PROJECTS</span><span>ONE / HOME</span></div>
        </div>
        <div id="open" class="hero-art" aria-label="项目入口">
          <div class="orbit orbit-one"></div><div class="orbit orbit-two"></div>
          <div class="art-heading"><span>PROJECT LAB / INDEX</span><b>{{ String(projects.length).padStart(2, '0') }}</b></div>
          <div class="art-project-list">
            <component :is="projectHref(project) ? 'a' : 'div'" v-for="(project, index) in projects.slice(0, 3)" :key="project.id" :href="projectHref(project) || undefined" :class="['art-project', { 'art-project-link': !!projectHref(project) }]">
              <span class="diagram-icon" :class="cardTone(project, index)">{{ project.mark || project.name.slice(0, 1).toUpperCase() }}</span>
              <div><b>{{ project.shortName || project.name }}</b><small>{{ project.caption || project.category }}</small></div>
              <span v-if="projectHref(project)" class="art-arrow" aria-hidden="true">↗</span>
              <small v-else class="art-unavailable">暂未开放</small>
            </component>
            <div v-if="projects.length > 3" class="art-more">还有 {{ projects.length - 3 }} 个项目，继续向下查看 ↓</div>
          </div>
          <div class="diagram-caption">YOUR PROJECTS, ONE PLACE</div>
        </div>
      </section>

      <section id="projects" class="projects section-wrap" aria-labelledby="projects-title">
        <div class="section-heading"><div><p class="kicker">01 / THE PROJECTS</p><h2 id="projects-title">项目概览与核心能力</h2></div><p>展示两个项目的建设目标、核心模块与技术实践，呈现从模型接入到应用落地的实现路径。</p></div>
        <div class="project-overviews">
          <article v-for="project in projects" :id="project.id" :key="project.id" class="project-overview" :class="`overview-${project.id}`">
            <div class="overview-hero">
              <div class="overview-copy">
                <p class="kicker">{{ project.introLabel || project.name }}</p>
                <h3>{{ project.introTitle || project.name }}<em>{{ project.introAccent }}</em></h3>
                <p class="overview-lead">{{ project.intro || project.description }}</p>
                <div class="overview-tags"><span v-for="tag in project.tags || []" :key="tag">{{ tag }}</span></div>
              </div>
              <div class="overview-art" aria-hidden="true"><div class="overview-orbit"></div><div class="overview-orbit orbit-second"></div><div class="overview-core"><span v-if="project.id === 'agent'" class="agent-eyes"><i></i><i></i></span><span v-else class="rag-pages">▤</span></div></div>
            </div>
            <div class="overview-heading"><div><p class="kicker">功能概览</p><h4>核心模块</h4></div><a v-if="projectHref(project)" class="overview-action" :href="projectHref(project)">{{ project.action || '打开项目页面' }} <span aria-hidden="true">→</span></a></div>
            <div class="overview-features"><section v-for="feature in project.features || []" :key="feature.name" class="overview-feature"><h5>{{ feature.name }}</h5><p>{{ feature.detail }}</p></section></div>
            <p v-if="project.note" class="overview-note">{{ project.note }}</p>
          </article>
        </div>
      </section>


    </main>

    <footer class="site-footer"><div class="section-wrap footer-inner"><div><a class="footer-brand" href="#top">项目作品集 <span>PROJECT PORTFOLIO</span></a><p>项目介绍与应用入口</p></div><div class="footer-links"><a href="#projects">项目介绍</a><a href="#open">项目入口</a></div><div class="filing"><a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">桂ICP备2026021890号-1</a><a v-if="psbNumber && psbId" :href="`https://beian.mps.gov.cn/#/query/webSearch?code=${encodeURIComponent(psbId)}`" target="_blank" rel="noopener noreferrer">{{ psbNumber }}</a><span>© 2026 项目作品集</span></div></div></footer>

    <div v-if="loginOpen" class="login-backdrop" @click.self="closeLogin">
      <section class="login-dialog" role="dialog" aria-modal="true" aria-labelledby="login-title">
        <button class="login-close" type="button" aria-label="关闭" :disabled="loginBusy" @click="closeLogin">×</button>
        <p class="kicker">ADMINISTRATOR ACCESS</p>
        <h2 id="login-title">管理员登录</h2>
        <p class="login-description">登录后将以管理员身份使用完整功能。</p>
        <form @submit.prevent="submitLogin">
          <label for="admin-username">账号</label>
          <input id="admin-username" v-model="username" autocomplete="username" required maxlength="80" />
          <label for="admin-password">密码</label>
          <input id="admin-password" v-model="password" type="password" autocomplete="current-password" required maxlength="512" />
          <p v-if="loginError" class="login-error" role="alert">{{ loginError }}</p>
          <button class="button button-dark login-submit" type="submit" :disabled="loginBusy">
            {{ loginBusy ? '正在登录…' : '登录' }}
          </button>
        </form>
      </section>
    </div>
  </div>
</template>
