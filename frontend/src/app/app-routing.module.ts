import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { QueryComponent } from './query.component';
import { ConnectionManagerComponent } from './components/connection-manager/connection-manager.component';
import { TableManagerComponent } from './components/table-manager/table-manager.component';
import { LoginComponent } from './components/auth/login/login.component';
import { RegisterComponent } from './components/auth/register/register.component';
import { AuthGuard } from './guards/auth.guard';
// 导入新组件
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { AiAssistantComponent } from './components/ai-assistant/ai-assistant.component';
import { SqlEditorComponent } from './components/sql-editor/sql-editor.component';
import { DataBrowserComponent } from './components/data-browser/data-browser.component';

const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'query', component: QueryComponent, canActivate: [AuthGuard] },
  { path: 'ai-assistant', component: AiAssistantComponent, canActivate: [AuthGuard] },
  { path: 'sql-editor', component: SqlEditorComponent, canActivate: [AuthGuard] },
  { path: 'data-browser', component: DataBrowserComponent, canActivate: [AuthGuard] },
  { path: 'connections', component: ConnectionManagerComponent, canActivate: [AuthGuard] },
  { path: 'tables', component: TableManagerComponent, canActivate: [AuthGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: '**', redirectTo: '/dashboard' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }