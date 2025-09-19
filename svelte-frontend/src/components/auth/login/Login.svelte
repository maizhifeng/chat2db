<script>
  import { user } from '../../../stores.js';
  import { login } from '../../../services/auth.service.js';
  import { navigateTo, routes } from '../../../router.js';
  
  let username = '';
  let password = '';
  let loading = false;
  let error = '';
  
  async function handleLogin() {
    if (!username || !password) {
      error = '请填写所有字段';
      return;
    }
    
    loading = true;
    error = '';
    
    try {
      await login(username, password);
      navigateTo(routes.DASHBOARD);
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="auth-container">
  <div class="auth-card">
    <h2>登录</h2>
    
    {#if error}
      <div class="error-message">{error}</div>
    {/if}
    
    <form on:submit|preventDefault={handleLogin}>
      <div class="form-group">
        <label for="username">用户名</label>
        <input 
          type="text" 
          id="username" 
          bind:value={username} 
          placeholder="请输入用户名"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="password">密码</label>
        <input 
          type="password" 
          id="password" 
          bind:value={password} 
          placeholder="请输入密码"
          required
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {#if loading}
          登录中...
        {:else}
          登录
        {/if}
      </button>
    </form>
    
    <div class="auth-footer">
      <p>还没有账户？<a href="#" on:click|preventDefault={() => navigateTo(routes.REGISTER)}>立即注册</a></p>
    </div>
  </div>
</div>

<style>
  .auth-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 20px;
  }
  
  .auth-card {
    background: white;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
  }
  
  .auth-card h2 {
    text-align: center;
    margin-top: 0;
    margin-bottom: 30px;
    color: #333;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
    color: #333;
  }
  
  .form-group input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    box-sizing: border-box;
  }
  
  .form-group input:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }
  
  button {
    width: 100%;
    padding: 12px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  button:hover:not(:disabled) {
    background-color: #0056b3;
  }
  
  button:disabled {
    background-color: #ccc;
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
  
  .auth-footer {
    text-align: center;
    margin-top: 20px;
  }
  
  .auth-footer a {
    color: #007bff;
    text-decoration: none;
  }
  
  .auth-footer a:hover {
    text-decoration: underline;
  }
</style>