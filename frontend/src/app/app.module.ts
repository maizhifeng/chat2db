import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { QueryComponent } from './query.component';
import { QueryService } from './query.service';

@NgModule({
  declarations: [QueryComponent],
  imports: [BrowserModule, FormsModule, HttpClientModule],
  providers: [QueryService],
  bootstrap: [QueryComponent]
})
export class AppModule {}
