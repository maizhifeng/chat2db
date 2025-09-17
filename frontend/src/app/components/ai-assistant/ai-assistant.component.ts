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
  
  messages: Array<{role: string, content: string, timestamp: Date}> = [];
  userInput = '';
  selectedModel = 'llama2';
  models: string[] = [];
  loading = false;
  loadingModels = false;
  loadingMessage = ''; // 添加加载消息

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
      timestamp: new Date()
    });
  }

  ngAfterViewChecked(): void {
    // 每次视图更新后滚动到底部
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        this.messagesContainer.nativeElement.scrollIntoView({behavior: "smooth", block: "end", inline: "nearest"});
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
              this.messages.push({
                role: 'assistant',
                content: `我理解您想要查询数据库。已生成并执行以下SQL:

\`\`\`sql
${res.sql}
\`\`\`

查询结果:
${JSON.stringify(queryRes.rows, null, 2)}`,
                timestamp: new Date()
              });
            },
            error: (err) => {
              this.loading = false;
              this.loadingMessage = '';
              this.messages.push({
                role: 'assistant',
                content: `我理解您想要查询数据库并生成了SQL:

\`\`\`sql
${res.sql}
\`\`\`

但在执行时遇到了错误: ${err.message}`,
                timestamp: new Date()
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
    const history = this.messages.map(m => ({
      role: m.role,
      text: m.content
    }));

    this.queryService.chat(message, history, this.selectedModel).subscribe({
      next: (res) => {
        this.loading = false;
        this.loadingMessage = '';
        this.messages.push({
          role: 'assistant',
          content: res.message || res.text || '抱歉，我没有理解您的问题。',
          timestamp: new Date()
        });
      },
      error: (err) => {
        this.loading = false;
        this.loadingMessage = '';
        this.messages.push({
          role: 'assistant',
          content: `抱歉，在处理您的请求时遇到了错误: ${err.message}`,
          timestamp: new Date()
        });
      }
    });
  }

  clearChat(): void {
    this.messages = [{
      role: 'assistant',
      content: '您好！我是您的AI数据库助手。您可以问我任何关于数据库的问题，我会尽力帮助您。',
      timestamp: new Date()
    }];
  }
}