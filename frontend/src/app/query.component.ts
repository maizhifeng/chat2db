import { Component, OnInit } from '@angular/core';
import { QueryService } from './query.service';
import { NlpService } from './services/nlp.service';

@Component({
  selector: 'app-query',
  templateUrl: './query.component.html',
  styleUrls: ['./query.component.css']
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

  // NLP features
  useNlp = false;
  generatedSql = '';

  constructor(
    private svc: QueryService,
    private nlpService: NlpService
  ) {}

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
        } else if (res && Array.isArray(res.get('models') || res.models)) {
          this.models = res.models || [];
        } else if (res && res.models && Array.isArray(res.models)) {
          this.models = res.models;
        } else if (res && res.error) {
          console.warn('models endpoint returned error', res.error);
          this.models = [];
        } else {
          // try to coerce keys into string list
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
    
    if (this.useNlp) {
      // Use NLP to generate SQL first
      this.nlpService.nl2sql(this.queryText).subscribe({
        next: (res) => {
          this.generatedSql = res.sql;
          // Then execute the generated SQL
          this.executeSql(res.sql);
        },
        error: (err) => {
          console.error('NLP conversion error', err);
          this.loading = false;
        }
      });
    } else {
      // Direct SQL execution
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
  }

  executeSql(sql: string) {
    this.svc.query(sql).subscribe({
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
          if (res && res.raw && typeof res.raw === 'object' && res.raw.done_reason === 'load') {
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
          if (res && res.sql) {
            this.sql = res.sql;
            this.results = res.rows || [];
          } else if (res && res.message) {
            this.sql = '';
            this.results = [{ reply: res.message }];
          } else if (res && res.text) {
            this.sql = '';
            this.results = [{ reply: res.text }];
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