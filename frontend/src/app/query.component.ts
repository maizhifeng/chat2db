import { Component, OnInit } from '@angular/core';
import { QueryService } from './query.service';

@Component({
  selector: 'app-root',
  templateUrl: './query.component.html'
})
export class QueryComponent implements OnInit {
  queryText = '';
  results: any[] = [];
  sql = '';
  loading = false;

  // models
  models: string[] = [];
  selectedModel: string | null = null;
  loadingModels = false;
  loadingMessage = '';
  retryCount = 0;

  constructor(private svc: QueryService) {}

  ngOnInit(): void {
    this.fetchModels();
  }

  fetchModels() {
    this.loadingModels = true;
    this.svc.getModels().subscribe({
      next: (res) => {
        // response may be {models: [...] } or a plain array depending on Ollama
        if (Array.isArray(res)) {
          this.models = res;
        } else if (res && Array.isArray((res as any).models)) {
          this.models = (res as any).models;
        } else if (res && (res as any).error) {
          console.warn('models endpoint returned error', (res as any).error);
          this.models = [];
        } else {
          try {
            this.models = Object.keys(res || {});
          } catch(e) {
            this.models = [];
          }
        }
        if (this.models.length>0) this.selectedModel = this.models[0];
        this.loadingModels = false;
      },
      error: (err) => {
        console.error('failed to fetch models', err);
        this.loadingModels = false;
      }
    });
  }

  send() {
    this.loading = true;
    this.svc.query(this.queryText).subscribe({
      next: (res) => {
        this.sql = res.sql;
        this.results = res.rows || [];
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.loading = false;
      }
    });
  }

  // send chat request using selected model
  loadModelAndChat() {
    if (!this.selectedModel) return;
    this.loading = true;
    this.loadingMessage = '';
    this.retryCount = 0;
    const tryChat = () => {
      this.svc.chat(this.queryText, [], this.selectedModel).subscribe({
        next: (res) => {
          // check for server-side 'load' status
          if (res && res.raw && typeof res.raw === 'object' && (res.raw as any).done_reason === 'load') {
            this.retryCount++;
            this.loadingMessage = `模型正在加载，重试中 (${this.retryCount}/3)`;
            if (this.retryCount < 3) {
              setTimeout(tryChat, 3000);
              return;
            } else {
              this.loadingMessage = '模型加载超时，请稍后再试。';
            }
          }

          // if backend returns sql-like response, keep old behavior; else show as message
          if (res && (res as any).sql) {
            this.sql = (res as any).sql;
            this.results = (res as any).rows || [];
          } else if (res && (res as any).message) {
            this.sql = '';
            this.results = [{ reply: (res as any).message }];
          } else if (res && (res as any).text) {
            this.sql = '';
            this.results = [{ reply: (res as any).text }];
          }

          this.loading = false;
          this.loadingMessage = '';
        },
        error: (err) => {
          console.error(err);
          this.loading = false;
          this.loadingMessage = '请求出错，请查看控制台。';
        }
      });
    };

    tryChat();
  }
}
