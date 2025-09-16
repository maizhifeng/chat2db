import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TableService {
  private base = environment.apiBase;

  constructor(private http: HttpClient) { }

  // Get tables for a connection
  getTables(connectionId: string): Observable<any> {
    return this.http.get(`${this.base}/connections/${connectionId}/tables`);
  }

  // Get table schema
  getTableSchema(connectionId: string, tableName: string): Observable<any> {
    return this.http.get(`${this.base}/connections/${connectionId}/tables/${tableName}/schema`);
  }

  // Get table data
  getTableData(connectionId: string, tableName: string, limit: number = 100): Observable<any> {
    return this.http.get(`${this.base}/connections/${connectionId}/tables/${tableName}/data?limit=${limit}`);
  }

  // Execute a query
  query(connectionId: string, query: string): Observable<any> {
    return this.http.post(`${this.base}/connections/${connectionId}/query`, { query });
  }
}