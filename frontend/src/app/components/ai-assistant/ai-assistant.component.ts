import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { QueryService } from '../../query.service';
import { NlpService } from '../../services/nlp.service';

@Component({
  selector: 'app-ai-assistant',
  templateUrl: './ai-assistant.component.html',
  styleUrls: ['./ai-assistant.component.css']
})
export class AiAssistantComponent implements OnInit {
  @ViewChild('messagesContainer', { static: false }) private messagesContainer!: ElementRef;
  
  messages: Array<{role: string, content?: string, timestamp: Date, isCollapsed?: boolean, isLongMessage?: boolean, messageType?: string, isProcessing?: boolean, thinkingContent?: string, responseContent?: string}> = [];
  userInput = '';
  selectedModel = 'llama2';
  models: string[] = [];
  loading = false;
  loadingModels = false;
  loadingMessage = ''; // 添加加载消息
  currentTime = new Date(); // 添加当前时间变量
  private timeInterval: any; // 添加定时器引用
  private readonly COLLAPSE_THRESHOLD = 500; // 设置消息长度阈值，增加到500字符

  constructor(
    private queryService: QueryService,
    private nlpService: NlpService
  ) {}

  ngOnInit(): void {
    this.loadModels();
    // 添加欢迎消息
    this.messages.push({
      role: 'assistant',
      content: '您好！我是您的AI数据库助手。您可以问我任何关于数据库的问题，我会尽力帮助您。',
      timestamp: new Date(),
      isCollapsed: false,
      messageType: 'system'
    });
    
    // 设置定时器更新当前时间
    this.timeInterval = setInterval(() => {
      this.currentTime = new Date();
    }, 1000);
  }

  ngOnDestroy(): void {
    // 清除定时器
    if (this.timeInterval) {
      clearInterval(this.timeInterval);
    }
  }

  ngAfterViewChecked(): void {
    // 每次视图更新后滚动到底部
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        const element = this.messagesContainer.nativeElement;
        element.scrollIntoView({behavior: "smooth", block: "end", inline: "nearest"});
        
        // 也滚动到消息容器的底部
        const messagesContainer = element.querySelector('.messages');
        if (messagesContainer) {
          messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
      }
    } catch(err) { 
      console.log('Scroll to bottom failed', err);
    }
  }

  loadModels(): void {
    this.loadingModels = true;
    this.loadingMessage = '正在加载AI模型...';
    this.queryService.getModels().subscribe({
      next: (res) => {
        if (Array.isArray(res)) {
          this.models = res;
        } else if (res && Array.isArray(res.models)) {
          this.models = res.models;
        }
        if (this.models.length > 0) {
          this.selectedModel = this.models[0];
        }
        this.loadingModels = false;
        this.loadingMessage = '';
      },
      error: (err) => {
        console.error('Failed to fetch models', err);
        this.loadingModels = false;
        this.loadingMessage = '';
        // 添加默认模型
        this.models = ['llama2', 'mistral', 'codellama'];
        this.selectedModel = 'llama2';
      }
    });
  }

  sendMessage(): void {
    if (!this.userInput.trim() || this.loading) return;

    // 添加用户消息
    this.messages.push({
      role: 'user',
      content: this.userInput,
      timestamp: new Date()
    });

    const userMessage = this.userInput;
    this.userInput = '';
    this.loading = true;
    this.loadingMessage = '正在处理您的请求...';

    // 首先尝试使用NLP服务转换为SQL
    this.nlpService.nl2sql(userMessage).subscribe({
      next: (res) => {
        if (res && res.sql) {
          // 如果成功转换为SQL，执行查询
          this.loadingMessage = '正在执行数据库查询...';
          this.queryService.query(res.sql).subscribe({
            next: (queryRes) => {
              this.loading = false;
              this.loadingMessage = '';
              const responseContent = `我理解您想要查询数据库。已生成并执行以下SQL:

\`\`\`sql
${res.sql}
\`\`\`

查询结果:
${JSON.stringify(queryRes.rows, null, 2)}`;
              
              // 检查消息是否需要折叠
              const isLongMessage = responseContent.length > this.COLLAPSE_THRESHOLD;
              
              this.messages.push({
                role: 'assistant',
                content: responseContent,
                timestamp: new Date(),
                isCollapsed: isLongMessage,
                isLongMessage: isLongMessage,
                messageType: 'database'
              });
            },
            error: (err) => {
              this.loading = false;
              this.loadingMessage = '';
              const errorMessage = `我理解您想要查询数据库并生成了SQL:

\`\`\`sql
${res.sql}
\`\`\`

但在执行时遇到了错误: ${err.message}`;
              
              this.messages.push({
                role: 'assistant',
                content: errorMessage,
                timestamp: new Date(),
                isCollapsed: errorMessage.length > this.COLLAPSE_THRESHOLD,
                isLongMessage: errorMessage.length > this.COLLAPSE_THRESHOLD,
                messageType: 'error'
              });
            }
          });
        } else {
          // 如果无法转换为SQL，使用AI模型
          this.sendToAI(userMessage);
        }
      },
      error: () => {
        // 如果NLP转换失败，使用AI模型
        this.sendToAI(userMessage);
      }
    });
  }

  sendToAI(message: string): void {
    this.loadingMessage = '正在与AI模型对话...';
    // 在发送历史记录时，排除刚刚添加的用户消息，避免重复
    const history = this.messages.slice(0, -1).map(m => ({
      role: m.role,
      text: m.content
    }));

    // 使用流式响应
    let assistantMessageIndex = -1;
    let thinkingMessageIndex = -1;
    
    this.queryService.streamChat(message, history, this.selectedModel).subscribe({
      next: (res) => {
        console.log('Stream response:', res);
        
        // Handle different response types
        switch (res.type) {
          case 'thinking':
            // Show thinking status with special display
            this.loadingMessage = res.message;
            
            // Create or update thinking message
            if (thinkingMessageIndex === -1) {
              // Create new thinking message
              this.messages.push({
                role: 'assistant',
                content: res.message,
                timestamp: new Date(),
                isCollapsed: false,
                isLongMessage: false,
                messageType: 'thinking',
                isProcessing: true
              });
              thinkingMessageIndex = this.messages.length - 1;
            } else {
              // Update existing thinking message
              this.messages[thinkingMessageIndex].content = res.message;
              this.messages[thinkingMessageIndex].isProcessing = true;
            }
            break;
            
          case 'responding':
            // Show responding status and create assistant message if needed
            this.loadingMessage = res.message;
            
            // Remove thinking message when we start responding
            if (thinkingMessageIndex !== -1) {
              this.messages.splice(thinkingMessageIndex, 1);
              thinkingMessageIndex = -1;
            }
            
            if (assistantMessageIndex === -1) {
              this.messages.push({
                role: 'assistant',
                content: '',
                timestamp: new Date(),
                isCollapsed: false,
                isLongMessage: false,
                messageType: 'response'
              });
              assistantMessageIndex = this.messages.length - 1;
              this.loading = false;
            }
            break;
            
          case 'chunk':
            // Add chunk to assistant message
            if (thinkingMessageIndex !== -1) {
              // Remove thinking message when we start responding
              this.messages.splice(thinkingMessageIndex, 1);
              thinkingMessageIndex = -1;
            }
            
            if (assistantMessageIndex === -1) {
              this.messages.push({
                role: 'assistant',
                content: '',
                timestamp: new Date(),
                isCollapsed: false,
                isLongMessage: false,
                messageType: 'response'
              });
              assistantMessageIndex = this.messages.length - 1;
              this.loading = false;
            }
            
            if (res.response) {
              this.messages[assistantMessageIndex].content += res.response;
            }
            
            // Check if we need to collapse long messages
            if (this.messages[assistantMessageIndex].content.length > this.COLLAPSE_THRESHOLD && 
                !this.messages[assistantMessageIndex].isLongMessage) {
              this.messages[assistantMessageIndex].isLongMessage = true;
              this.messages[assistantMessageIndex].isCollapsed = true;
            }
            break;
            
          case 'result':
            // Final result - update content if different
            if (thinkingMessageIndex !== -1) {
              // Remove thinking message when we have final result
              this.messages.splice(thinkingMessageIndex, 1);
              thinkingMessageIndex = -1;
            }
            
            if (assistantMessageIndex !== -1 && res.response) {
              // Only update if the response is different from what we already have
              if (!this.messages[assistantMessageIndex].content.endsWith(res.response)) {
                this.messages[assistantMessageIndex].content = res.response;
                
                // Check if we need to collapse long messages
                if (this.messages[assistantMessageIndex].content.length > this.COLLAPSE_THRESHOLD && 
                    !this.messages[assistantMessageIndex].isLongMessage) {
                  this.messages[assistantMessageIndex].isLongMessage = true;
                  this.messages[assistantMessageIndex].isCollapsed = true;
                }
              }
            }
            break;
            
          case 'error':
            // Handle error
            this.loading = false;
            this.loadingMessage = '';
            
            // Remove thinking message on error
            if (thinkingMessageIndex !== -1) {
              this.messages.splice(thinkingMessageIndex, 1);
              thinkingMessageIndex = -1;
            }
            
            if (assistantMessageIndex === -1) {
              const errorMessage = `抱歉，在处理您的请求时遇到了错误: ${res.message}`;
              this.messages.push({
                role: 'assistant',
                content: errorMessage,
                timestamp: new Date(),
                isCollapsed: errorMessage.length > this.COLLAPSE_THRESHOLD,
                isLongMessage: errorMessage.length > this.COLLAPSE_THRESHOLD,
                messageType: 'error'
              });
            } else {
              const errorMessage = `

抱歉，在处理您的请求时遇到了错误: ${res.message}`;
              this.messages[assistantMessageIndex].content += errorMessage;
              
              // Check if we need to collapse long messages
              if (this.messages[assistantMessageIndex].content.length > this.COLLAPSE_THRESHOLD && 
                  !this.messages[assistantMessageIndex].isLongMessage) {
                this.messages[assistantMessageIndex].isLongMessage = true;
                this.messages[assistantMessageIndex].isCollapsed = true;
              }
            }
            break;
            
          default:
            // Handle legacy or unknown response formats
            if (thinkingMessageIndex !== -1) {
              // Remove thinking message when we start responding
              this.messages.splice(thinkingMessageIndex, 1);
              thinkingMessageIndex = -1;
            }
            
            if (assistantMessageIndex === -1) {
              this.messages.push({
                role: 'assistant',
                content: '',
                timestamp: new Date(),
                isCollapsed: false,
                isLongMessage: false,
                messageType: 'response'
              });
              assistantMessageIndex = this.messages.length - 1;
              this.loading = false;
              this.loadingMessage = '';
            }
            
            if (res.response) {
              this.messages[assistantMessageIndex].content += res.response;
            } else if (res.message) {
              this.messages[assistantMessageIndex].content = res.message;
            }
            
            // Check if we need to collapse long messages
            if (this.messages[assistantMessageIndex].content.length > this.COLLAPSE_THRESHOLD && 
                !this.messages[assistantMessageIndex].isLongMessage) {
              this.messages[assistantMessageIndex].isLongMessage = true;
              this.messages[assistantMessageIndex].isCollapsed = true;
            }
            break;
        }
      },
      error: (err) => {
        this.loading = false;
        this.loadingMessage = '';
        
        // Remove thinking message on error
        if (thinkingMessageIndex !== -1) {
          this.messages.splice(thinkingMessageIndex, 1);
          thinkingMessageIndex = -1;
        }
        
        if (assistantMessageIndex === -1) {
          const errorMessage = `抱歉，在处理您的请求时遇到了错误: ${err.message}`;
          this.messages.push({
            role: 'assistant',
            content: errorMessage,
            timestamp: new Date(),
            isCollapsed: errorMessage.length > this.COLLAPSE_THRESHOLD,
            isLongMessage: errorMessage.length > this.COLLAPSE_THRESHOLD,
            messageType: 'error'
          });
        } else {
          const errorMessage = `

抱歉，在处理您的请求时遇到了错误: ${err.message}`;
          this.messages[assistantMessageIndex].content += errorMessage;
          
          // Check if we need to collapse long messages
          if (this.messages[assistantMessageIndex].content.length > this.COLLAPSE_THRESHOLD && 
              !this.messages[assistantMessageIndex].isLongMessage) {
            this.messages[assistantMessageIndex].isLongMessage = true;
            this.messages[assistantMessageIndex].isCollapsed = true;
          }
        }
      },
      complete: () => {
        this.loading = false;
        this.loadingMessage = '';
        
        // Remove thinking message when complete
        if (thinkingMessageIndex !== -1) {
          this.messages.splice(thinkingMessageIndex, 1);
          thinkingMessageIndex = -1;
        }
        
        // 检查最后一条消息是否包含思考过程和回复内容的分离格式
        if (this.messages.length > 0) {
          const lastMessage = this.messages[this.messages.length - 1];
          if (lastMessage.content && typeof lastMessage.content === 'string') {
            // 检查是否包含思考过程和回复内容的标记（支持多种格式）
            const hasThinking = lastMessage.content.includes('[THINKING_PROCESS]') || 
                               lastMessage.content.includes('**思考过程：**') || 
                               lastMessage.content.includes('思考过程：');
            const hasResponse = lastMessage.content.includes('[RESPONSE_CONTENT]') || 
                               lastMessage.content.includes('**回复内容：**') || 
                               lastMessage.content.includes('回复内容：');
            
            if (hasThinking && hasResponse) {
              // 分离思考过程和回复内容
              const content = lastMessage.content;
              let thinkingStart, responseStart;
              
              // 查找思考过程开始位置
              if (content.includes('[THINKING_PROCESS]')) {
                thinkingStart = content.indexOf('[THINKING_PROCESS]');
              } else if (content.includes('**思考过程：**')) {
                thinkingStart = content.indexOf('**思考过程：**');
              } else {
                thinkingStart = content.indexOf('思考过程：');
              }
              
              // 查找回复内容开始位置
              if (content.includes('[RESPONSE_CONTENT]')) {
                responseStart = content.indexOf('[RESPONSE_CONTENT]');
              } else if (content.includes('**回复内容：**')) {
                responseStart = content.indexOf('**回复内容：**');
              } else {
                responseStart = content.indexOf('回复内容：');
              }
              
              if (thinkingStart !== -1 && responseStart !== -1 && responseStart > thinkingStart) {
                const thinkingContent = content.substring(thinkingStart, responseStart).trim();
                const responseContent = content.substring(responseStart).trim();
                
                // 更新消息为分离显示类型
                lastMessage.messageType = 'separated';
                lastMessage.thinkingContent = thinkingContent;
                lastMessage.responseContent = responseContent;
                delete lastMessage.content;
              }
            } else if (hasThinking && !hasResponse) {
              // 只有思考过程，没有明确的回复内容标记
              const content = lastMessage.content;
              let thinkingStart;
              if (content.includes('[THINKING_PROCESS]')) {
                thinkingStart = content.indexOf('[THINKING_PROCESS]');
              } else if (content.includes('**思考过程：**')) {
                thinkingStart = content.indexOf('**思考过程：**');
              } else {
                thinkingStart = content.indexOf('思考过程：');
              }
              
              if (thinkingStart !== -1) {
                const thinkingContent = content.substring(thinkingStart).trim();
                const responseContent = "回复内容未明确标识";
                
                // 更新消息为分离显示类型
                lastMessage.messageType = 'separated';
                lastMessage.thinkingContent = thinkingContent;
                lastMessage.responseContent = responseContent;
                delete lastMessage.content;
              }
            }
          }
        }
      }
    });
  }

  clearChat(): void {
    this.messages = [{
      role: 'assistant',
      content: '您好！我是您的AI数据库助手。您可以问我任何关于数据库的问题，我会尽力帮助您。',
      timestamp: new Date(),
      isCollapsed: false,
      messageType: 'system'
    }];
  }

  // 切换消息的折叠状态
  toggleMessageCollapse(index: number): void {
    if (this.messages[index]) {
      this.messages[index].isCollapsed = !this.messages[index].isCollapsed;
    }
  }
  
  // 获取折叠后的预览内容
  getPreviewContent(content: string, maxLength: number = 300): string {
    if (content.length <= maxLength) {
      return content;
    }
    
    // 如果是代码块，尝试保持代码块的完整性
    if (content.startsWith('```')) {
      const lines = content.split('\n');
      let preview = lines[0] + '\n'; // 保留代码块开始标记
      let charCount = preview.length;
      
      for (let i = 1; i < lines.length && charCount < maxLength - 100; i++) {
        if (charCount + lines[i].length + 1 <= maxLength - 100) {
          preview += lines[i] + '\n';
          charCount += lines[i].length + 1;
        } else {
          break;
        }
      }
      
      return preview + '\n...';
    }
    
    // 普通文本截取
    return content.substring(0, maxLength) + '...';
  }
  
  // 测试分离显示功能
  testSeparation(): void {
    const testContent = `[THINKING_PROCESS]
This is the AI assistant's thinking process. Here, the AI analyzes the user's question, considers different solutions, and decides how best to answer the user.

The AI might consider the following factors:
1. The specific content of the user's question
2. Available database information
3. Relevant SQL queries
4. How to present the answer most clearly

[RESPONSE_CONTENT]
This is the AI assistant's final response content. Here, the AI provides specific answers and suggestions.

For your question, I recommend:
- First check the database connection
- Then run the appropriate SQL query
- Finally analyze the returned results`;
    
    this.messages.push({
      role: 'assistant',
      content: testContent,
      timestamp: new Date(),
      isCollapsed: false,
      messageType: 'response'
    });
    
    // 触发分离逻辑
    setTimeout(() => {
      const lastMessage = this.messages[this.messages.length - 1];
      if (lastMessage.content && typeof lastMessage.content === 'string') {
        const hasThinking = lastMessage.content.includes('[THINKING_PROCESS]') || 
                           lastMessage.content.includes('**思考过程：**') || 
                           lastMessage.content.includes('思考过程：');
        const hasResponse = lastMessage.content.includes('[RESPONSE_CONTENT]') || 
                           lastMessage.content.includes('**回复内容：**') || 
                           lastMessage.content.includes('回复内容：');
        
        if (hasThinking && hasResponse) {
          const content = lastMessage.content;
          let thinkingStart, responseStart;
          
          // 查找思考过程开始位置
          if (content.includes('[THINKING_PROCESS]')) {
            thinkingStart = content.indexOf('[THINKING_PROCESS]');
          } else if (content.includes('**思考过程：**')) {
            thinkingStart = content.indexOf('**思考过程：**');
          } else {
            thinkingStart = content.indexOf('思考过程：');
          }
          
          // 查找回复内容开始位置
          if (content.includes('[RESPONSE_CONTENT]')) {
            responseStart = content.indexOf('[RESPONSE_CONTENT]');
          } else if (content.includes('**回复内容：**')) {
            responseStart = content.indexOf('**回复内容：**');
          } else {
            responseStart = content.indexOf('回复内容：');
          }
          
          if (thinkingStart !== -1 && responseStart !== -1 && responseStart > thinkingStart) {
            const thinkingContent = content.substring(thinkingStart, responseStart).trim();
            const responseContent = content.substring(responseStart).trim();
            
            // 更新消息为分离显示类型
            lastMessage.messageType = 'separated';
            lastMessage.thinkingContent = thinkingContent;
            lastMessage.responseContent = responseContent;
            delete lastMessage.content;
          }
        }
      }
    }, 100);
  }
}