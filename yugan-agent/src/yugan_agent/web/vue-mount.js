(() => {
  const root = document.querySelector('.app');
  if (!root || !window.Vue) return;

  // Vue compiles and mounts the page shell. The established controller then binds its
  // existing computer-operation, chat, approval, and workspace actions to those elements.
  const app = window.Vue.createApp({ name: 'YuganAgentApp' });
  app.mount(root);
  window.__yuganAgentVueApp = app;
})();
