import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class TableService {
  private base = environment.apiBase;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  // Get auth headers
  private getAuthHeaders(): HttpHeaders {
    const token = this.authService.getCurrentToken();
    if (token) {
      return new HttpHeaders({
        'Authorization': `Bearer ${token}`
      });
    }
    return new HttpHeaders();
  }

  // Get tables for a connection
  getTables(connectionId: string): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.get(`${this.base}/connections/${connectionId}/tables`, { headers });
  }

  // Get table schema
  getTableSchema(connectionId: string, tableName: string): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.get(`${this.base}/connections/${connectionId}/tables/${tableName}`, { headers });
  }

  // Get table data
  getTableData(connectionId: string, tableName: string, limit: number = 100): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.get(`${this.base}/connections/${connectionId}/tables/${tableName}/query?limit=${limit}`, { headers });
  }

  // Execute a query
  query(connectionId: string, query: string): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.post(`${this.base}/connections/${connectionId}/query`, { query }, { headers });
  }
}