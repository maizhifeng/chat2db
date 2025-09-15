import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from './src/environments/environment';

@Injectable({ providedIn: 'root' })
export class QueryService {
  private base = environment.apiBase;
  constructor(private http: HttpClient) {}

  query(nl: string): Observable<any> {
    return this.http.post(`${this.base}/query`, { query: nl });
  }

  // call chat with optional model override
  chat(message: string, history: any[] = [], model?: string): Observable<any> {
    const payload: any = { message, history };
    if (model) payload.model = model;
    return this.http.post(`${this.base}/chat`, payload);
  }

  // list available models (proxied by backend)
  getModels(): Observable<any> {
    return this.http.get(`${this.base}/models`);
  }
}
