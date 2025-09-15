import { Component } from '@angular/core';
import { QueryService } from './query.service';

@Component({
  selector: 'app-query',
  templateUrl: './query.component.html'
})
export class QueryComponent {
  queryText = '';
  results: any[] = [];
  sql = '';
  loading = false;

  constructor(private svc: QueryService) {}

  send() {
    this.loading = true;
    this.svc.query(this.queryText).subscribe({
      next: (res) => {
        this.sql = res.sql;
        this.results = res.rows || [];
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.loading = false;
      }
    });
  }
}
