<script>
  import { onMount } from 'svelte';
  import { connections, currentConnection } from '../../stores.js';
  import { getConnections, addConnection, updateConnection, deleteConnection, testConnection } from '../../services/connection.service.js';
  
  let connectionForm = {
    id: '',
    name: '',
    type: 'sqlite',
    host: '',
    port: '',
    username: '',
    password: '',
    database: ''
  };
  
  let showForm = false;
  let editing = false;
  let loading = false;
  let testing = false;
  let testResults = {};
  let error = '';
  
  // Load connections on component mount
  onMount(() => {
    loadConnections();
  });
  
  async function loadConnections() {
    loading = true;
    error = '';
    
    try {
      await getConnections();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  function openForm(connection = null) {
    if (connection) {
      connectionForm = { ...connection };
      editing = true;
    } else {
      connectionForm = {
        id: '',
        name: '',
        type: 'sqlite',
        host: '',
        port: '',
        username: '',
        password: '',
        database: ''
      };
      editing = false;
    }
    showForm = true;
  }
  
  function closeForm() {
    showForm = false;
    editing = false;
    error = '';
  }
  
  async function saveConnection() {
    loading = true;
    error = '';
    
    try {
      if (editing) {
        await updateConnection(connectionForm.id, connectionForm);
      } else {
        await addConnection(connectionForm);
      }
      closeForm();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  async function removeConnection(id) {
    if (!confirm('确定要删除这个连接吗？')) return;
    
    loading = true;
    error = '';
    
    try {
      await deleteConnection(id);
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  async function testConnectionHandler(id) {
    testing = true;
    testResults[id] = '测试中...';
    
    try {
      const result = await testConnection(id);
      testResults[id] = result.message || '连接成功';
    } catch (err) {
      testResults[id] = `测试失败: ${err.message}`;
    } finally {
      testing = false;
    }
  }
  
  function setAsCurrent(connection) {
    currentConnection.set(connection);
  }
</script>

<div class="connection-manager">
  <div class="header">
    <h2>数据库连接管理</h2>
    <button class="btn-primary" on:click={() => openForm()}>添加连接</button>
  </div>
  
  {#if error}
    <div class="error-message">{error}</div>
  {/if}
  
  {#if $loading}
    <div class="loading">加载中...</div>
  {:else}
    <div class="connections-list">
      {#each $connections as connection}
        <div class="connection-card">
          <div class="connection-header">
            <h3>{connection.name}</h3>
            <span class="connection-type {connection.type}">{connection.type}</span>
          </div>
          
          <div class="connection-details">
            <p><strong>数据库:</strong> {connection.database}</p>
            {#if connection.type !== 'sqlite'}
              <p><strong>主机:</strong> {connection.host}:{connection.port}</p>
            {/if}
          </div>
          
          <div class="connection-actions">
            <button class="btn-secondary" on:click={() => testConnectionHandler(connection.id)} disabled={testing}>
              测试
            </button>
            <button class="btn-secondary" on:click={() => openForm(connection)}>编辑</button>
            <button class="btn-danger" on:click={() => removeConnection(connection.id)}>删除</button>
            <button class="btn-primary" on:click={() => setAsCurrent(connection)}>
              {#if $currentConnection && $currentConnection.id === connection.id}
                当前使用
              {:else}
                设为当前
              {/if}
            </button>
          </div>
          
          {#if testResults[connection.id]}
            <div class="test-result">{testResults[connection.id]}</div>
          {/if}
        </div>
      {:else}
        <p class="no-connections">暂无数据库连接，请添加一个连接。</p>
      {/each}
    </div>
  {/if}
  
  {#if showForm}
    <div class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{editing ? '编辑连接' : '添加连接'}</h3>
          <button class="close-btn" on:click={closeForm}>&times;</button>
        </div>
        
        <form on:submit|preventDefault={saveConnection}>
          <div class="form-group">
            <label for="name">连接名称</label>
            <input 
              type="text" 
              id="name" 
              bind:value={connectionForm.name} 
              required
            />
          </div>
          
          <div class="form-group">
            <label for="type">数据库类型</label>
            <select id="type" bind:value={connectionForm.type}>
              <option value="sqlite">SQLite</option>
              <option value="mysql">MySQL</option>
              <option value="postgresql">PostgreSQL</option>
            </select>
          </div>
          
          {#if connectionForm.type !== 'sqlite'}
            <div class="form-row">
              <div class="form-group">
                <label for="host">主机</label>
                <input 
                  type="text" 
                  id="host" 
                  bind:value={connectionForm.host} 
                  required
                />
              </div>
              
              <div class="form-group">
                <label for="port">端口</label>
                <input 
                  type="number" 
                  id="port" 
                  bind:value={connectionForm.port} 
                  required
                />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="username">用户名</label>
                <input 
                  type="text" 
                  id="username" 
                  bind:value={connectionForm.username} 
                  required
                />
              </div>
              
              <div class="form-group">
                <label for="password">密码</label>
                <input 
                  type="password" 
                  id="password" 
                  bind:value={connectionForm.password} 
                  required
                />
              </div>
            </div>
          {/if}
          
          <div class="form-group">
            <label for="database">数据库名称/路径</label>
            <input 
              type="text" 
              id="database" 
              bind:value={connectionForm.database} 
              required
            />
          </div>
          
          {#if error}
            <div class="error-message">{error}</div>
          {/if}
          
          <div class="form-actions">
            <button type="button" class="btn-secondary" on:click={closeForm}>取消</button>
            <button type="submit" class="btn-primary" disabled={loading}>
              {#if loading}
                保存中...
              {:else}
                保存
              {/if}
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}
</div>

<style>
  .connection-manager {
    padding: 20px;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .header h2 {
    margin: 0;
  }
  
  .btn-primary {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    font-size: 14px;
  }
  
  .btn-primary:hover {
    background-color: #0056b3;
  }
  
  .btn-secondary {
    background-color: #6c757d;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    font-size: 14px;
    margin-right: 8px;
  }
  
  .btn-secondary:hover {
    background-color: #545b62;
  }
  
  .btn-danger {
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    font-size: 14px;
    margin-right: 8px;
  }
  
  .btn-danger:hover {
    background-color: #bd2130;
  }
  
  .btn-primary:disabled,
  .btn-secondary:disabled,
  .btn-danger:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .error-message {
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    padding: 10px;
    margin-bottom: 20px;
  }
  
  .loading {
    text-align: center;
    padding: 20px;
  }
  
  .connections-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
  
  .connection-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .connection-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .connection-header h3 {
    margin: 0;
    color: #333;
  }
  
  .connection-type {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
  }
  
  .connection-type.sqlite {
    background-color: #28a745;
    color: white;
  }
  
  .connection-type.mysql {
    background-color: #007bff;
    color: white;
  }
  
  .connection-type.postgresql {
    background-color: #6f42c1;
    color: white;
  }
  
  .connection-details p {
    margin: 5px 0;
    color: #666;
  }
  
  .connection-actions {
    margin-top: 15px;
    display: flex;
    flex-wrap: wrap;
  }
  
  .test-result {
    margin-top: 10px;
    padding: 8px;
    border-radius: 4px;
    font-size: 14px;
  }
  
  .no-connections {
    grid-column: 1 / -1;
    text-align: center;
    padding: 40px;
    color: #666;
  }
  
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    border-radius: 8px;
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #eee;
  }
  
  .modal-header h3 {
    margin: 0;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #999;
  }
  
  .close-btn:hover {
    color: #333;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-row {
    display: flex;
    gap: 15px;
  }
  
  .form-row .form-group {
    flex: 1;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
    color: #333;
  }
  
  .form-group input,
  .form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    box-sizing: border-box;
  }
  
  .form-group input:focus,
  .form-group select:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    padding-top: 20px;
    border-top: 1px solid #eee;
  }
</style>