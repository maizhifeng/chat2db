import { Component, OnInit } from '@angular/core';
import { ConnectionService } from '../../services/connection.service';
import { TableService } from '../../services/table.service';
import { DatabaseConnection } from '../../models/connection.model';

@Component({
  selector: 'app-table-manager',
  templateUrl: './table-manager.component.html',
  styleUrls: ['./table-manager.component.css']
})
export class TableManagerComponent implements OnInit {
  connections: DatabaseConnection[] = [];
  selectedConnection: DatabaseConnection | null = null;
  tables: string[] = [];
  selectedTable: string | null = null;
  schema: any[] = [];
  queryText: string = '';
  queryResult: any = null;
  
  loadingTables = false;
  loadingSchema = false;

  constructor(
    private connectionService: ConnectionService,
    private tableService: TableService
  ) { }

  ngOnInit(): void {
    this.loadConnections();
  }

  loadConnections(): void {
    this.connectionService.getConnections().subscribe({
      next: (connections) => {
        this.connections = connections;
      },
      error: (error) => {
        console.error('Error loading connections', error);
      }
    });
  }

  selectConnection(connection: DatabaseConnection): void {
    this.selectedConnection = connection;
    this.loadTables();
  }

  clearConnection(): void {
    this.selectedConnection = null;
    this.tables = [];
    this.selectedTable = null;
    this.schema = [];
  }

  loadTables(): void {
    if (!this.selectedConnection) return;
    
    this.loadingTables = true;
    this.tableService.getTables(this.selectedConnection.id).subscribe({
      next: (tables) => {
        this.tables = tables;
        this.loadingTables = false;
      },
      error: (error) => {
        console.error('Error loading tables', error);
        this.loadingTables = false;
      }
    });
  }

  viewTable(tableName: string): void {
    if (!this.selectedConnection) return;
    
    this.selectedTable = tableName;
    this.loadTableSchema();
  }

  clearTable(): void {
    this.selectedTable = null;
    this.schema = [];
    this.queryText = '';
    this.queryResult = null;
  }

  loadTableSchema(): void {
    if (!this.selectedConnection || !this.selectedTable) return;
    
    this.loadingSchema = true;
    this.schema = [];
    this.tableService.getTableSchema(this.selectedConnection.id, this.selectedTable).subscribe({
      next: (schema) => {
        this.schema = schema;
        this.loadingSchema = false;
      },
      error: (error) => {
        console.error('Error loading table schema', error);
        this.loadingSchema = false;
      }
    });
  }

  executeQuery(): void {
    if (!this.selectedConnection || !this.queryText) return;
    
    this.queryResult = null;
    this.tableService.query(this.selectedConnection.id, this.queryText).subscribe({
      next: (result) => {
        this.queryResult = result;
      },
      error: (error) => {
        console.error('Error executing query', error);
        this.queryResult = { error: error.error?.error || '查询执行失败' };
      }
    });
  }
}