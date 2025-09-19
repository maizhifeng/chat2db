<script>
  import { onMount } from 'svelte';
  import { query, chat, getModels, encodeText, calculateSimilarity } from './api.js';

  // State variables
  let queryText = '';
  let results = [];
  let sql = '';
  let loading = false;

  // Model related state
  let models = [];
  let selectedModel = null;
  let loadingModels = false;
  let loadingMessage = '';
  let retryCount = 0;

  // Load models on component mount
  onMount(() => {
    fetchModels();
  });

  // Fetch available models
  async function fetchModels() {
    loadingModels = true;
    try {
      const res = await getModels();
      // response may be {models: [...] } or a plain array depending on Ollama
      if (Array.isArray(res)) {
        models = res;
      } else if (res && Array.isArray(res.models)) {
        models = res.models;
      } else if (res && res.error) {
        console.warn('models endpoint returned error', res.error);
        models = [];
      } else {
        // try to coerce keys into string list
        try {
          models = Object.keys(res || {});
        } catch(e) {
          models = [];
        }
      }
      if (models.length > 0) selectedModel = models[0];
    } catch (err) {
      console.error('failed to fetch models', err);
    } finally {
      loadingModels = false;
    }
  }

  // Send natural language query
  async function send() {
    loading = true;
    try {
      const res = await query(queryText);
      sql = res.sql;
      results = res.rows || [];
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  }

  // Send chat request using selected model
  async function loadModelAndChat() {
    if (!selectedModel) return;
    loading = true;
    loadingMessage = '';
    retryCount = 0;
    
    const tryChat = async () => {
      try {
        const res = await chat(queryText, [], selectedModel);
        
        // check for server-side 'load' status
        if (res && res.raw && typeof res.raw === 'object' && res.raw.done_reason === 'load') {
          retryCount++;
          loadingMessage = `模型正在加载，重试中 (${retryCount}/3)`;
          if (retryCount < 3) {
            setTimeout(tryChat, 3000);
            return;
          } else {
            loadingMessage = '模型加载超时，请稍后再试。';
          }
        }

        // if backend returns sql-like response, keep old behavior; else show as message
        if (res && res.sql) {
          sql = res.sql;
          results = res.rows || [];
        } else if (res && res.message) {
          sql = '';
          results = [{ reply: res.message }];
        } else if (res && res.text) {
          sql = '';
          results = [{ reply: res.text }];
        }

        loading = false;
        loadingMessage = '';
      } catch (err) {
        console.error(err);
        loading = false;
        loadingMessage = '请求出错，请查看控制台。';
      }
    };

    await tryChat();
  }
</script>

<div class="chat2db">
  <h3>Chat2DB 简易演示</h3>
  
  <!-- Navigation -->
  <div style="margin-bottom: 20px;">
    <button class="btn btn-secondary">数据库连接管理</button>
  </div>
  
  <textarea rows="3" cols="60" bind:value={queryText}></textarea>
  <br>

  <div style="margin-top:8px">
    <label for="model">模型:</label>
    <select id="model" bind:value={selectedModel}>
      {#each models as model}
        <option value={model}>{model}</option>
      {/each}
    </select>
    <button on:click={fetchModels} disabled={loadingModels}>刷新模型</button>
    <button on:click={loadModelAndChat} disabled={loading || !selectedModel}>加载并发送</button>
    <button on:click={send} disabled={loading}>发送（SQL）</button>
  </div>
  {#if loadingMessage}
    <div class="loading-message">{loadingMessage}</div>
  {/if}

  {#if sql}
    <div>
      <h4>执行的 SQL</h4>
      <pre>{sql}</pre>
    </div>
  {/if}

  {#if results.length}
    <div>
      <h4>结果（最多 100 条）</h4>
      <table border="1">
        <thead>
          <tr>
            {#if results[0]}
              {#each Object.keys(results[0]) as key}
                <th>{key}</th>
              {/each}
            {/if}
          </tr>
        </thead>
        <tbody>
          {#each results as row}
            <tr>
              {#each Object.entries(row) as [key, value]}
                <td>{value}</td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>