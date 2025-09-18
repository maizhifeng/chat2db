import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  currentUser: any;
  stats = {
    connections: 0,
    queries: 0,
    tables: 0,
    models: 0
  };

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    // 初始化统计数据
    this.loadStats();
  }

  loadStats(): void {
    // 这里应该从后端获取统计数据
    this.stats = {
      connections: 3,
      queries: 42,
      tables: 15,
      models: 2
    };
  }

  navigateTo(path: string): void {
    this.router.navigate([`/${path}`]);
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}