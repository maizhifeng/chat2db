import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DatabaseConnection } from '../models/connection.model';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ConnectionService {
  private base = environment.apiBase;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) { }

  // Create a new database connection
  createConnection(connection: DatabaseConnection): Observable<DatabaseConnection> {
    const headers = this.getAuthHeaders();
    return this.http.post<DatabaseConnection>(`${this.base}/connections`, connection, { headers });
  }

  // Get all database connections
  getConnections(): Observable<DatabaseConnection[]> {
    const headers = this.getAuthHeaders();
    return this.http.get<DatabaseConnection[]>(`${this.base}/connections`, { headers });
  }

  // Get a specific database connection by ID
  getConnection(id: string): Observable<DatabaseConnection> {
    const headers = this.getAuthHeaders();
    return this.http.get<DatabaseConnection>(`${this.base}/connections/${id}`, { headers });
  }

  // Update a database connection
  updateConnection(id: string, connection: DatabaseConnection): Observable<DatabaseConnection> {
    const headers = this.getAuthHeaders();
    return this.http.put<DatabaseConnection>(`${this.base}/connections/${id}`, connection, { headers });
  }

  // Delete a database connection
  deleteConnection(id: string): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.delete(`${this.base}/connections/${id}`, { headers });
  }

  // Test a database connection
  testConnection(id: string): Observable<any> {
    const headers = this.getAuthHeaders();
    return this.http.post(`${this.base}/connections/${id}/test`, {}, { headers });
  }

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
}