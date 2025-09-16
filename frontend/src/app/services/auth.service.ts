import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface User {
  id: string;
  username: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private base = environment.apiBase;
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  private tokenSubject = new BehaviorSubject<string | null>(null);
  
  public currentUser = this.currentUserSubject.asObservable();
  public token = this.tokenSubject.asObservable();

  constructor(private http: HttpClient) {
    // Check if there's a stored token on initialization
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      this.tokenSubject.next(token);
      this.currentUserSubject.next(JSON.parse(user));
    }
  }

  // Register a new user
  register(username: string, email: string, password: string): Observable<User> {
    return this.http.post<User>(`${this.base}/auth/register`, { username, email, password });
  }

  // Login user
  login(username: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.base}/auth/login`, { username, password })
      .pipe(
        tap(response => {
          // Store token and user in local storage
          localStorage.setItem('token', response.token);
          localStorage.setItem('user', JSON.stringify(response.user));
          
          // Update subjects
          this.tokenSubject.next(response.token);
          this.currentUserSubject.next(response.user);
        })
      );
  }

  // Logout user
  logout(): void {
    // Clear local storage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // Update subjects
    this.tokenSubject.next(null);
    this.currentUserSubject.next(null);
  }

  // Get current user
  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  // Get current token
  getCurrentToken(): string | null {
    return this.tokenSubject.value;
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!this.tokenSubject.value;
  }

  // Get auth headers for HTTP requests
  getAuthHeaders() {
    const token = this.getCurrentToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
}