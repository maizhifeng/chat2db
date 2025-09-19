<script>
  import { onMount } from 'svelte';
  import { models, currentModel } from '../../stores.js';
  import { getModels, chatWithAI } from '../../services/nlp.service.js';
  
  let messages = [];
  let userInput = '';
  let loading = false;
  let error = '';
  let loadingModels = false;
  
  // Load models on component mount
  onMount(() => {
    loadModels();
  });
  
  async function loadModels() {
    loadingModels = true;
    error = '';
    
    try {
      const modelsData = await getModels();
      // Normalize models data
      let modelsList = [];
      if (Array.isArray(modelsData)) {
        modelsList = modelsData;
      } else if (modelsData && Array.isArray(modelsData.models)) {
        modelsList = modelsData.models;
      } else if (modelsData && modelsData.error) {
        console.warn('Models endpoint returned error', modelsData.error);
        modelsList = [];
      } else {
        // try to coerce keys into string list
        try {
          modelsList = Object.keys(modelsData || {});
        } catch(e) {
          modelsList = [];
        }
      }
      
      models.set(modelsList);
      if (modelsList.length > 0 && !$currentModel) {
        currentModel.set(modelsList[0]);
      }
    } catch (err) {
      error = err.message;
    } finally {
      loadingModels = false;
    }
  }
  
  async function sendMessage() {
    if (!userInput.trim()) return;
    if (!$currentModel) {
      error = '请选择一个AI模型';
      return;
    }
    
    // Add user message to chat
    messages = [...messages, {
      id: Date.now(),
      role: 'user',
      content: userInput,
      timestamp: new Date()
    }];
    
    // Clear input
    const userMessage = userInput;
    userInput = '';
    
    // Show loading state
    loading = true;
    error = '';
    
    try {
      // Prepare history (last 10 messages)
      const history = messages.slice(-10).map(msg => ({
        role: msg.role,
        text: msg.content
      }));
      
      // Send message to AI
      const response = await chatWithAI(userMessage, history, $currentModel);
      
      // Add AI response to chat
      messages = [...messages, {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message || response.text || JSON.stringify(response),
        timestamp: new Date()
      }];
    } catch (err) {
      error = err.message;
      // Add error message to chat
      messages = [...messages, {
        id: Date.now() + 1,
        role: 'error',
        content: `错误: ${err.message}`,
        timestamp: new Date()
      }];
    } finally {
      loading = false;
    }
  }
  
  function clearChat() {
    messages = [];
  }
  
  function formatMessage(content) {
    // Simple formatting for code blocks
    return content.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  }
</script>

<div class="ai-assistant">
  <h2>AI 助手</h2>
  
  <div class="assistant-container">
    <div class="controls-section">
      <div class="model-selector">
        <label for="model">AI 模型:</label>
        <select id="model" bind:value={$currentModel}>
          {#each $models as model}
            <option value={model}>{model}</option>
          {/each}
        </select>
        <button class="btn-secondary" on:click={loadModels} disabled={loadingModels}>
          {#if loadingModels}
            刷新中...
          {:else}
            刷新模型
          {/if}
        </button>
      </div>
      
      <button class="btn-secondary" on:click={clearChat}>清空对话</button>
    </div>
    
    {#if error}
      <div class="error-message">{error}</div>
    {/if}
    
    <div class="chat-container">
      {#if messages.length === 0}
        <div class="welcome-message">
          <h3>欢迎使用 AI 助手</h3>
          <p>请输入您的问题，AI 助手将帮助您进行数据库查询和数据分析。</p>
        </div>
      {:else}
        <div class="messages-container">
          {#each messages as message}
            <div class="message {message.role}">
              <div class="message-header">
                <span class="role">{message.role === 'user' ? '您' : message.role === 'assistant' ? 'AI 助手' : '错误'}</span>
                <span class="timestamp">{message.timestamp.toLocaleTimeString()}</span>
              </div>
              <div class="message-content">
                {@html formatMessage(message.content)}
              </div>
            </div>
          {/each}
          
          {#if loading}
            <div class="message assistant">
              <div class="message-header">
                <span class="role">AI 助手</span>
              </div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>
    
    <div class="input-section">
      <textarea 
        bind:value={userInput} 
        placeholder="请输入您的问题..."
        rows="3"
        disabled={loading}
        on:keydown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
          }
        }}
      ></textarea>
      <button class="btn-primary" on:click={sendMessage} disabled={loading || !userInput.trim()}>
        {#if loading}
          发送中...
        {:else}
          发送
        {/if}
      </button>
    </div>
  </div>
</div>

<style>
  .ai-assistant {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .assistant-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }
  
  .controls-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
  }
  
  .model-selector {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .model-selector label {
    font-weight: 500;
    color: #333;
  }
  
  .model-selector select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
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
  
  .btn-secondary:hover:not(:disabled) {
    background-color: #545b62;
  }
  
  .btn-secondary:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .error-message {
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    padding: 10px;
  }
  
  .chat-container {
    flex: 1;
    overflow-y: auto;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    background-color: #f8f9fa;
  }
  
  .welcome-message {
    text-align: center;
    padding: 40px 20px;
    color: #666;
  }
  
  .welcome-message h3 {
    margin-top: 0;
    color: #333;
  }
  
  .messages-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .message {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 18px;
    position: relative;
  }
  
  .message.user {
    align-self: flex-end;
    background-color: #007bff;
    color: white;
    border-bottom-right-radius: 4px;
  }
  
  .message.assistant {
    align-self: flex-start;
    background-color: white;
    border: 1px solid #ddd;
    border-bottom-left-radius: 4px;
  }
  
  .message.error {
    align-self: flex-start;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-bottom-left-radius: 4px;
    color: #721c24;
  }
  
  .message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 12px;
  }
  
  .message.user .message-header {
    color: rgba(255, 255, 255, 0.8);
  }
  
  .message.assistant .message-header,
  .message.error .message-header {
    color: #666;
  }
  
  .role {
    font-weight: 600;
  }
  
  .timestamp {
    font-size: 11px;
  }
  
  .message-content {
    line-height: 1.5;
  }
  
  .message-content pre {
    background-color: #f1f1f1;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    overflow-x: auto;
    margin: 10px 0;
  }
  
  .message.user .message-content pre {
    background-color: rgba(0, 0, 0, 0.1);
  }
  
  .typing-indicator {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .typing-indicator span {
    width: 8px;
    height: 8px;
    background-color: #666;
    border-radius: 50%;
    display: inline-block;
    animation: typing 1.4s infinite ease-in-out;
  }
  
  .typing-indicator span:nth-child(1) {
    animation-delay: 0s;
  }
  
  .typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
  }
  
  .typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
  }
  
  @keyframes typing {
    0%, 60%, 100% {
      transform: translateY(0);
    }
    30% {
      transform: translateY(-5px);
    }
  }
  
  .input-section {
    display: flex;
    gap: 10px;
  }
  
  .input-section textarea {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: inherit;
    font-size: 14px;
    resize: none;
  }
  
  .input-section textarea:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
</style>