<script>
  import { onMount } from 'svelte';
  import { currentRoute, navigateTo, routes } from './router.js';
  import { user, isAuthenticated } from './stores.js';
  import { getCurrentUser } from './services/auth.service.js';
  
  // Import components
  import Dashboard from './components/dashboard/Dashboard.svelte';
  import Query from './Query.svelte';
  import Login from './components/auth/login/Login.svelte';
  import Register from './components/auth/register/Register.svelte';
  import ConnectionManager from './components/connection-manager/ConnectionManager.svelte';
  import DataBrowser from './components/data-browser/DataBrowser.svelte';
  import SQLEditor from './components/sql-editor/SQLEditor.svelte';
  import TableManager from './components/table-manager/TableManager.svelte';
  import AIAssistant from './components/ai-assistant/AIAssistant.svelte';
  
  // Check authentication on mount
  onMount(() => {
    checkAuth();
    // Handle browser back/forward buttons
    window.addEventListener('popstate', handlePopState);
  });
  
  async function checkAuth() {
    try {
      await getCurrentUser();
    } catch (err) {
      // Not authenticated, that's okay
      console.log('Not authenticated');
    }
  }
  
  function handlePopState() {
    currentRoute.set(window.location.pathname);
  }
  
  function logout() {
    user.set(null);
    navigateTo(routes.LOGIN);
  }
  
  // Determine which component to show based on route
  let component = Dashboard;
  let componentProps = {};
  
  $: {
    switch ($currentRoute) {
      case routes.DASHBOARD:
        component = Dashboard;
        break;
      case routes.QUERY:
        component = Query;
        break;
      case routes.LOGIN:
        component = Login;
        break;
      case routes.REGISTER:
        component = Register;
        break;
      case routes.CONNECTIONS:
        component = ConnectionManager;
        break;
      case routes.DATA_BROWSER:
        component = DataBrowser;
        break;
      case routes.SQL_EDITOR:
        component = SQLEditor;
        break;
      case routes.TABLES:
        component = TableManager;
        break;
      case routes.AI_ASSISTANT:
        component = AIAssistant;
        break;
      default:
        component = Dashboard;
    }
  }
</script>

<div class="app">
  <!-- Navigation bar -->
  {#if $isAuthenticated && $currentRoute !== routes.LOGIN && $currentRoute !== routes.REGISTER}
    <nav class="navbar">
      <div class="nav-brand">
        <h1>Chat2DB</h1>
      </div>
      
      <ul class="nav-links">
        <li><a href="#" class:active={$currentRoute === routes.DASHBOARD} on:click|preventDefault={() => navigateTo(routes.DASHBOARD)}>仪表板</a></li>
        <li><a href="#" class:active={$currentRoute === routes.QUERY} on:click|preventDefault={() => navigateTo(routes.QUERY)}>基础查询</a></li>
        <li><a href="#" class:active={$currentRoute === routes.AI_ASSISTANT} on:click|preventDefault={() => navigateTo(routes.AI_ASSISTANT)}>AI助手</a></li>
        <li><a href="#" class:active={$currentRoute === routes.SQL_EDITOR} on:click|preventDefault={() => navigateTo(routes.SQL_EDITOR)}>SQL编辑器</a></li>
        <li><a href="#" class:active={$currentRoute === routes.DATA_BROWSER} on:click|preventDefault={() => navigateTo(routes.DATA_BROWSER)}>数据浏览器</a></li>
        <li><a href="#" class:active={$currentRoute === routes.CONNECTIONS} on:click|preventDefault={() => navigateTo(routes.CONNECTIONS)}>连接管理</a></li>
        <li><a href="#" class:active={$currentRoute === routes.TABLES} on:click|preventDefault={() => navigateTo(routes.TABLES)}>表管理</a></li>
      </ul>
      
      <div class="nav-user">
        {#if $user}
          <span>欢迎, {$user.username}</span>
          <button class="btn-logout" on:click={logout}>退出</button>
        {/if}
      </div>
    </nav>
  {/if}
  
  <!-- Main content -->
  <main class="main-content">
    <svelte:component this={component} {...componentProps} />
  </main>
</div>

<style>
  .app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  .navbar {
    background-color: #343a40;
    color: white;
    padding: 0 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .nav-brand h1 {
    margin: 0;
    font-size: 1.5rem;
  }
  
  .nav-links {
    display: flex;
    list-style: none;
    gap: 20px;
  }
  
  .nav-links a {
    color: rgba(255, 255, 255, 0.75);
    text-decoration: none;
    padding: 20px 0;
    transition: color 0.2s;
  }
  
  .nav-links a:hover,
  .nav-links a.active {
    color: white;
  }
  
  .nav-user {
    display: flex;
    align-items: center;
    gap: 15px;
  }
  
  .btn-logout {
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    cursor: pointer;
    font-size: 14px;
  }
  
  .btn-logout:hover {
    background-color: #bd2130;
  }
  
  .main-content {
    flex: 1;
    background-color: #f8f9fa;
  }
</style>