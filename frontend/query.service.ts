import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class QueryService {
  private base = 'http://localhost:5001/api';
  constructor(private http: HttpClient) {}

  query(nl: string): Observable<any> {
    return this.http.post(`${this.base}/query`, { query: nl });
  }
}
