import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { AppComponent } from './app.component';
import { QueryComponent } from './query.component';
import { QueryService } from './query.service';
import { ConnectionManagerComponent } from './components/connection-manager/connection-manager.component';
import { ConnectionService } from './services/connection.service';
import { TableManagerComponent } from './components/table-manager/table-manager.component';
import { TableService } from './services/table.service';
import { NlpService } from './services/nlp.service';
import { AuthService } from './services/auth.service';
import { LoginComponent } from './components/auth/login/login.component';
import { RegisterComponent } from './components/auth/register/register.component';
import { AppRoutingModule } from './app-routing.module';

@NgModule({
  declarations: [
    AppComponent,
    QueryComponent,
    ConnectionManagerComponent,
    TableManagerComponent,
    LoginComponent,
    RegisterComponent
  ],
  imports: [
    BrowserModule, 
    FormsModule, 
    HttpClientModule,
    AppRoutingModule
  ],
  providers: [
    QueryService,
    ConnectionService,
    TableService,
    NlpService,
    AuthService
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}