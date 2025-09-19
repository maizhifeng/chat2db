<script>
  import { user, isAuthenticated } from '../../stores.js';
  import { navigateTo, routes } from '../../router.js';
</script>

<div class="dashboard">
  <h2>仪表板</h2>
  
  <div class="dashboard-grid">
    <div class="dashboard-card" on:click={() => navigateTo(routes.QUERY)}>
      <h3>基础查询</h3>
      <p>使用自然语言查询数据库</p>
    </div>
    
    <div class="dashboard-card" on:click={() => navigateTo(routes.AI_ASSISTANT)}>
      <h3>AI助手</h3>
      <p>与AI模型对话进行复杂查询</p>
    </div>
    
    <div class="dashboard-card" on:click={() => navigateTo(routes.SQL_EDITOR)}>
      <h3>SQL编辑器</h3>
      <p>直接编写和执行SQL语句</p>
    </div>
    
    <div class="dashboard-card" on:click={() => navigateTo(routes.DATA_BROWSER)}>
      <h3>数据浏览器</h3>
      <p>浏览数据库表和数据</p>
    </div>
    
    <div class="dashboard-card" on:click={() => navigateTo(routes.CONNECTIONS)}>
      <h3>连接管理</h3>
      <p>管理数据库连接</p>
    </div>
    
    <div class="dashboard-card" on:click={() => navigateTo(routes.TABLES)}>
      <h3>表管理</h3>
      <p>管理数据库表结构</p>
    </div>
  </div>
</div>

<style>
  .dashboard {
    padding: 20px;
  }
  
  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 20px;
  }
  
  .dashboard-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .dashboard-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
  
  .dashboard-card h3 {
    margin-top: 0;
    color: #333;
  }
  
  .dashboard-card p {
    color: #666;
    margin-bottom: 0;
  }
</style>