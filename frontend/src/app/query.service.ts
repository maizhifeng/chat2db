import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import { AuthService } from './services/auth.service';

@Injectable({ providedIn: 'root' })
export class QueryService {
  private base = environment.apiBase;
  
  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  query(nl: string): Observable<any> {
    // For public queries, no auth needed
    return this.http.post(`${this.base}/query`, { query: nl });
  }

  // call chat with optional model override
  chat(message: string, history: any[] = [], model?: string): Observable<any> {
    const payload: any = { message, history };
    if (model) payload.model = model;
    // For chat, no auth needed
    return this.http.post(`${this.base}/chat`, payload);
  }

  // list available models (proxied by backend)
  getModels(): Observable<any> {
    // For models, no auth needed
    return this.http.get(`${this.base}/models`);
  }
}