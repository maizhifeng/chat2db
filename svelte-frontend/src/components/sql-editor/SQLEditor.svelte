<script>
  import { onMount } from 'svelte';
  import { currentConnection } from '../../stores.js';
  import { queryDatabase } from '../../services/database.service.js';
  
  let sqlQuery = '';
  let queryResults = [];
  let executedSql = '';
  let loading = false;
  let error = '';
  let successMessage = '';
  
  // Initialize with a sample query
  onMount(() => {
    sqlQuery = 'SELECT * FROM employees LIMIT 10;';
  });
  
  async function executeQuery() {
    if (!sqlQuery.trim()) {
      error = '请输入 SQL 查询语句';
      return;
    }
    
    if (!$currentConnection) {
      error = '请先选择一个数据库连接';
      return;
    }
    
    loading = true;
    error = '';
    successMessage = '';
    queryResults = [];
    
    try {
      // For SQL editor, we need to send the raw SQL query
      // We'll create a custom endpoint for this or modify the existing one
      const response = await queryDatabase($currentConnection.id, sqlQuery);
      
      queryResults = response.rows || [];
      executedSql = response.sql || sqlQuery;
      successMessage = `查询成功执行，返回 ${queryResults.length} 条记录`;
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  function clearResults() {
    queryResults = [];
    executedSql = '';
    error = '';
    successMessage = '';
  }
  
  function formatValue(value) {
    if (value === null || value === undefined) return '';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }
</script>

<div class="sql-editor">
  <h2>SQL 编辑器</h2>
  
  {#if !$currentConnection}
    <div class="no-connection">
      <p>请先选择一个数据库连接。</p>
      <a href="/connections">前往连接管理</a>
    </div>
  {:else}
    <div class="editor-container">
      <div class="editor-section">
        <div class="editor-header">
          <h3>SQL 查询</h3>
          <div class="editor-actions">
            <button class="btn-secondary" on:click={clearResults}>清空结果</button>
            <button class="btn-primary" on:click={executeQuery} disabled={loading}>
              {#if loading}
                执行中...
              {:else}
                执行查询
              {/if}
            </button>
          </div>
        </div>
        
        <div class="sql-input">
          <textarea 
            bind:value={sqlQuery} 
            placeholder="请输入 SQL 查询语句..."
            rows="10"
          ></textarea>
        </div>
        
        {#if error}
          <div class="error-message">{error}</div>
        {/if}
        
        {#if successMessage}
          <div class="success-message">{successMessage}</div>
        {/if}
      </div>
      
      {#if executedSql}
        <div class="executed-sql">
          <h4>执行的 SQL</h4>
          <pre>{executedSql}</pre>
        </div>
      {/if}
      
      {#if queryResults.length > 0}
        <div class="results-section">
          <h4>查询结果</h4>
          <div class="table-wrapper">
            <table class="results-table">
              <thead>
                <tr>
                  {#if queryResults[0]}
                    {#each Object.keys(queryResults[0]) as key}
                      <th>{key}</th>
                    {/each}
                  {/if}
                </tr>
              </thead>
              <tbody>
                {#each queryResults as row}
                  <tr>
                    {#each Object.entries(row) as [key, value]}
                      <td>{formatValue(value)}</td>
                    {/each}
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .sql-editor {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .editor-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .editor-section {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .editor-header h3 {
    margin: 0;
    color: #333;
  }
  
  .editor-actions {
    display: flex;
    gap: 10px;
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
  
  .btn-primary:hover:not(:disabled) {
    background-color: #0056b3;
  }
  
  .btn-primary:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .btn-secondary {
    background-color: #6c757d;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    font-size: 14px;
  }
  
  .btn-secondary:hover {
    background-color: #545b62;
  }
  
  .sql-input textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    resize: vertical;
    box-sizing: border-box;
  }
  
  .sql-input textarea:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
  
  .error-message {
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    padding: 10px;
    margin-top: 15px;
  }
  
  .success-message {
    color: #155724;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 4px;
    padding: 10px;
    margin-top: 15px;
  }
  
  .executed-sql {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .executed-sql h4 {
    margin-top: 0;
    margin-bottom: 10px;
    color: #333;
  }
  
  .executed-sql pre {
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    overflow-x: auto;
    font-family: 'Courier New', monospace;
    font-size: 14px;
    margin: 0;
  }
  
  .results-section {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .results-section h4 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #333;
  }
  
  .table-wrapper {
    overflow-x: auto;
    flex: 1;
  }
  
  .results-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .results-table th,
  .results-table td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }
  
  .results-table th {
    background-color: #f8f9fa;
    font-weight: 600;
    position: sticky;
    top: 0;
  }
  
  .results-table tr:hover {
    background-color: #f8f9fa;
  }
  
  .results-table td {
    max-width: 200px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .no-connection {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: #666;
  }
  
  .no-connection a {
    color: #007bff;
    text-decoration: none;
    margin-top: 10px;
  }
  
  .no-connection a:hover {
    text-decoration: underline;
  }
</style>