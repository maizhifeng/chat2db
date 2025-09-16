import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  username = '';
  email = '';
  password = '';
  confirmPassword = '';
  loading = false;
  errorMessage = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  register(): void {
    // Check if passwords match
    if (this.password !== this.confirmPassword) {
      this.errorMessage = '密码不匹配';
      return;
    }
    
    this.loading = true;
    this.errorMessage = '';
    
    this.authService.register(this.username, this.email, this.password).subscribe({
      next: (user) => {
        this.loading = false;
        // After registration, redirect to login page
        this.router.navigate(['/login']);
      },
      error: (error) => {
        this.loading = false;
        this.errorMessage = error.error?.error || '注册失败';
      }
    });
  }
}