import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class NlpService {
  private base = environment.apiBase;

  constructor(private http: HttpClient) { }

  // Process natural language query
  processQuery(query: string): Observable<any> {
    return this.http.post(`${this.base}/nlp/process`, { query });
  }

  // Convert natural language to SQL
  nl2sql(query: string): Observable<any> {
    return this.http.post(`${this.base}/nlp/nl2sql`, { query });
  }
}