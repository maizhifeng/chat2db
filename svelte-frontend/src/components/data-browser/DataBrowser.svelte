<script>
  import { onMount } from 'svelte';
  import { currentConnection, tables, currentTable } from '../../stores.js';
  import { getTables, getTableSchema, queryTableData } from '../../services/database.service.js';
  
  let loading = false;
  let error = '';
  let tableSchema = [];
  let tableData = [];
  let loadingData = false;
  let dataError = '';
  let currentPage = 1;
  let pageSize = 50;
  let totalCount = 0;
  
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
  
  async function loadTableDetails(tableName) {
    if (!tableName || !$currentConnection) return;
    
    // Set current table
    currentTable.set(tableName);
    
    // Load schema
    loadingData = true;
    dataError = '';
    tableSchema = [];
    tableData = [];
    
    try {
      // Load schema
      tableSchema = await getTableSchema($currentConnection.id, tableName);
      
      // Load first page of data
      currentPage = 1;
      await loadTableData();
    } catch (err) {
      dataError = err.message;
    } finally {
      loadingData = false;
    }
  }
  
  async function loadTableData() {
    if (!$currentConnection || !$currentTable) return;
    
    loadingData = true;
    dataError = '';
    
    try {
      const data = await queryTableData($currentConnection.id, $currentTable, {
        page: currentPage,
        pageSize: pageSize
      });
      
      tableData = data.data || [];
      totalCount = data.totalCount || 0;
    } catch (err) {
      dataError = err.message;
    } finally {
      loadingData = false;
    }
  }
  
  function goToPage(page) {
    if (page < 1 || page > Math.ceil(totalCount / pageSize)) return;
    
    currentPage = page;
    loadTableData();
  }
  
  function formatValue(value) {
    if (value === null || value === undefined) return '';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }
</script>

<div class="data-browser">
  <h2>数据浏览器</h2>
  
  {#if !$currentConnection}
    <div class="no-connection">
      <p>请先选择一个数据库连接。</p>
      <a href="/connections">前往连接管理</a>
    </div>
  {:else}
    <div class="browser-container">
      <div class="tables-panel">
        <h3>表列表</h3>
        
        {#if loading}
          <div class="loading">加载中...</div>
        {:else if error}
          <div class="error-message">{error}</div>
        {:else}
          <ul class="tables-list">
            {#each $tables as table}
              <li 
                class:active={$currentTable === table}
                on:click={() => loadTableDetails(table)}
              >
                {table}
              </li>
            {/each}
          </ul>
        {/if}
      </div>
      
      <div class="table-content">
        {#if $currentTable}
          <div class="table-header">
            <h3>表: {$currentTable}</h3>
          </div>
          
          {#if loadingData}
            <div class="loading">加载数据中...</div>
          {:else if dataError}
            <div class="error-message">{dataError}</div>
          {:else}
            <div class="table-details">
              {#if tableSchema.length > 0}
                <div class="schema-section">
                  <h4>表结构</h4>
                  <table class="schema-table">
                    <thead>
                      <tr>
                        <th>字段名</th>
                        <th>数据类型</th>
                      </tr>
                    </thead>
                    <tbody>
                      {#each tableSchema as column}
                        <tr>
                          <td>{column.name || column.column_name}</td>
                          <td>{column.type || column.data_type}</td>
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>
              {/if}
              
              {#if tableData.length > 0}
                <div class="data-section">
                  <h4>数据</h4>
                  <div class="table-wrapper">
                    <table class="data-table">
                      <thead>
                        <tr>
                          {#if tableData[0]}
                            {#each Object.keys(tableData[0]) as key}
                              <th>{key}</th>
                            {/each}
                          {/if}
                        </tr>
                      </thead>
                      <tbody>
                        {#each tableData as row}
                          <tr>
                            {#each Object.entries(row) as [key, value]}
                              <td>{formatValue(value)}</td>
                            {/each}
                          </tr>
                        {/each}
                      </tbody>
                    </table>
                  </div>
                  
                  {#if totalCount > pageSize}
                    <div class="pagination">
                      <button 
                        class="pagination-btn" 
                        disabled={currentPage === 1}
                        on:click={() => goToPage(currentPage - 1)}
                      >
                        上一页
                      </button>
                      
                      <span class="pagination-info">
                        第 {currentPage} 页，共 {Math.ceil(totalCount / pageSize)} 页
                        (共 {totalCount} 条记录)
                      </span>
                      
                      <button 
                        class="pagination-btn" 
                        disabled={currentPage === Math.ceil(totalCount / pageSize)}
                        on:click={() => goToPage(currentPage + 1)}
                      >
                        下一页
                      </button>
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          {/if}
        {:else}
          <div class="no-table-selected">
            <p>请选择一个表来查看数据。</p>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .data-browser {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .browser-container {
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
  }
  
  .tables-panel h3 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #333;
  }
  
  .tables-list {
    list-style: none;
    padding: 0;
    margin: 0;
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
  
  .table-content {
    flex: 1;
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }
  
  .table-header {
    margin-bottom: 20px;
  }
  
  .table-header h3 {
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
  .no-table-selected {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: #666;
  }
  
  .no-connection a,
  .no-table-selected a {
    color: #007bff;
    text-decoration: none;
    margin-top: 10px;
  }
  
  .no-connection a:hover,
  .no-table-selected a:hover {
    text-decoration: underline;
  }
  
  .table-details {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .schema-section,
  .data-section {
    margin-bottom: 30px;
  }
  
  .schema-section h4,
  .data-section h4 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #333;
  }
  
  .schema-table,
  .data-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
  }
  
  .schema-table th,
  .schema-table td,
  .data-table th,
  .data-table td {
    padding: 10px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }
  
  .schema-table th,
  .data-table th {
    background-color: #f8f9fa;
    font-weight: 600;
  }
  
  .schema-table tr:hover,
  .data-table tr:hover {
    background-color: #f8f9fa;
  }
  
  .table-wrapper {
    overflow-x: auto;
  }
  
  .data-table td {
    max-width: 200px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .pagination {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
  }
  
  .pagination-btn {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
  }
  
  .pagination-btn:hover:not(:disabled) {
    background-color: #0056b3;
  }
  
  .pagination-btn:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .pagination-info {
    color: #666;
  }
</style>