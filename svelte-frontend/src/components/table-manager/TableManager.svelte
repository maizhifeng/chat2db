<script>
  import { onMount } from 'svelte';
  import { currentConnection, tables, currentTable } from '../../stores.js';
  import { getTables, getTableSchema } from '../../services/database.service.js';
  
  let loading = false;
  let error = '';
  let tableSchema = [];
  let loadingSchema = false;
  let schemaError = '';
  
  // Load tables when component mounts or when current connection changes
  $: if ($currentConnection) {
    loadTables();
  }
  
  async function loadTables() {
    if (!$currentConnection) return;
    
    loading = true;
    error = '';
    
    try {
      const tablesData = await getTables($currentConnection.id);
      tables.set(tablesData);
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  async function loadTableSchema(tableName) {
    if (!tableName || !$currentConnection) return;
    
    // Set current table
    currentTable.set(tableName);
    
    // Load schema
    loadingSchema = true;
    schemaError = '';
    tableSchema = [];
    
    try {
      tableSchema = await getTableSchema($currentConnection.id, tableName);
    } catch (err) {
      schemaError = err.message;
    } finally {
      loadingSchema = false;
    }
  }
  
  function formatValue(value) {
    if (value === null || value === undefined) return '';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }
</script>

<div class="table-manager">
  <h2>表管理</h2>
  
  {#if !$currentConnection}
    <div class="no-connection">
      <p>请先选择一个数据库连接。</p>
      <a href="/connections">前往连接管理</a>
    </div>
  {:else}
    <div class="manager-container">
      <div class="tables-panel">
        <div class="panel-header">
          <h3>表列表</h3>
          <button class="btn-secondary" on:click={loadTables} disabled={loading}>
            {#if loading}
              刷新中...
            {:else}
              刷新
            {/if}
          </button>
        </div>
        
        {#if error}
          <div class="error-message">{error}</div>
        {:else}
          <ul class="tables-list">
            {#each $tables as table}
              <li 
                class:active={$currentTable === table}
                on:click={() => loadTableSchema(table)}
              >
                {table}
              </li>
            {/each}
          </ul>
        {/if}
      </div>
      
      <div class="schema-content">
        {#if $currentTable}
          <div class="schema-header">
            <h3>表结构: {$currentTable}</h3>
          </div>
          
          {#if loadingSchema}
            <div class="loading">加载表结构中...</div>
          {:else if schemaError}
            <div class="error-message">{schemaError}</div>
          {:else if tableSchema.length > 0}
            <div class="schema-table-container">
              <table class="schema-table">
                <thead>
                  <tr>
                    <th>字段名</th>
                    <th>数据类型</th>
                    <th>其他信息</th>
                  </tr>
                </thead>
                <tbody>
                  {#each tableSchema as column}
                    <tr>
                      <td>{column.name || column.column_name}</td>
                      <td>{column.type || column.data_type}</td>
                      <td>
                        {#if column.nullable !== undefined}
                          {column.nullable ? '允许为空' : '不允许为空'}
                        {/if}
                        {#if column.default !== undefined}
                          , 默认值: {formatValue(column.default)}
                        {/if}
                        {#if column.primary_key}
                          , 主键
                        {/if}
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {:else}
            <div class="no-schema">
              <p>该表没有可用的结构信息。</p>
            </div>
          {/if}
        {:else}
          <div class="no-table-selected">
            <p>请选择一个表来查看其结构。</p>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .table-manager {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .manager-container {
    display: flex;
    flex: 1;
    gap: 20px;
    height: calc(100% - 40px);
  }
  
  .tables-panel {
    width: 250px;
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }
  
  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .panel-header h3 {
    margin: 0;
    color: #333;
  }
  
  .btn-secondary {
    background-color: #6c757d;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    cursor: pointer;
    font-size: 14px;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background-color: #545b62;
  }
  
  .btn-secondary:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .tables-list {
    list-style: none;
    padding: 0;
    margin: 0;
    flex: 1;
  }
  
  .tables-list li {
    padding: 10px;
    border-radius: 4px;
    cursor: pointer;
    margin-bottom: 5px;
    transition: background-color 0.2s;
  }
  
  .tables-list li:hover {
    background-color: #f8f9fa;
  }
  
  .tables-list li.active {
    background-color: #007bff;
    color: white;
  }
  
  .schema-content {
    flex: 1;
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }
  
  .schema-header {
    margin-bottom: 20px;
  }
  
  .schema-header h3 {
    margin: 0;
    color: #333;
  }
  
  .loading {
    text-align: center;
    padding: 20px;
    color: #666;
  }
  
  .error-message {
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    padding: 10px;
    margin-bottom: 20px;
  }
  
  .no-connection,
  .no-table-selected,
  .no-schema {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: #666;
  }
  
  .no-connection a,
  .no-table-selected a,
  .no-schema a {
    color: #007bff;
    text-decoration: none;
    margin-top: 10px;
  }
  
  .no-connection a:hover,
  .no-table-selected a:hover,
  .no-schema a:hover {
    text-decoration: underline;
  }
  
  .schema-table-container {
    flex: 1;
    overflow-y: auto;
  }
  
  .schema-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .schema-table th,
  .schema-table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }
  
  .schema-table th {
    background-color: #f8f9fa;
    font-weight: 600;
    position: sticky;
    top: 0;
  }
  
  .schema-table tr:hover {
    background-color: #f8f9fa;
  }
</style>