import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class DatabaseService {
  private base = environment.apiBase;
  
  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  // 获取数据库连接列表
  getConnections(): Observable<any> {
    const headers = new HttpHeaders(this.authService.getAuthHeaders());
    return this.http.get(`${this.base}/connections`, { headers });
  }

  // 获取指定连接的表列表
  getTables(connectionId: string): Observable<any> {
    const headers = new HttpHeaders(this.authService.getAuthHeaders());
    return this.http.get(`${this.base}/connections/${connectionId}/tables`, { headers });
  }

  // 获取表结构信息
  getTableSchema(connectionId: string, tableName: string): Observable<any> {
    const headers = new HttpHeaders(this.authService.getAuthHeaders());
    return this.http.get(`${this.base}/connections/${connectionId}/tables/${tableName}/schema`, { headers });
  }

  // 查询表数据
  queryTableData(connectionId: string, tableName: string, options: any = {}): Observable<any> {
    const headers = new HttpHeaders(this.authService.getAuthHeaders());
    return this.http.post(`${this.base}/connections/${connectionId}/tables/${tableName}/query`, 
      { ...options }, 
      { headers }
    );
  }

  // 导出表数据
  exportTableData(connectionId: string, tableName: string, format: string = 'csv'): Observable<any> {
    const headers = new HttpHeaders(this.authService.getAuthHeaders());
    return this.http.get(`${this.base}/connections/${connectionId}/tables/${tableName}/export?format=${format}`, 
      { headers, responseType: 'blob' as 'json' }
    );
  }
}