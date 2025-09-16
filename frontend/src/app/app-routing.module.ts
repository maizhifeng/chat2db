import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { QueryComponent } from './query.component';
import { ConnectionManagerComponent } from './components/connection-manager/connection-manager.component';
import { TableManagerComponent } from './components/table-manager/table-manager.component';
import { LoginComponent } from './components/auth/login/login.component';
import { RegisterComponent } from './components/auth/register/register.component';
import { AuthGuard } from './guards/auth.guard';

const routes: Routes = [
  { path: '', component: QueryComponent, canActivate: [AuthGuard] },
  { path: 'connections', component: ConnectionManagerComponent, canActivate: [AuthGuard] },
  { path: 'tables', component: TableManagerComponent, canActivate: [AuthGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: '**', redirectTo: '/login' } // Wildcard route for a 404 page (redirect to login)
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }