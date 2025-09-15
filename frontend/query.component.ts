import { Component, OnInit } from '@angular/core';
import { QueryService } from './query.service';

@Component({
  selector: 'app-query',
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
    this.svc.chat(this.queryText, [], this.selectedModel).subscribe({
      next: (res) => {
        // if backend returns sql-like response, keep old behavior; else show as message
        if (res && res.sql) {
          this.sql = res.sql;
          this.results = res.rows || [];
        } else if (res && res.message) {
          this.sql = '';
          this.results = [{ reply: res.message }];
        }
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.loading = false;
      }
    });
  }
}
