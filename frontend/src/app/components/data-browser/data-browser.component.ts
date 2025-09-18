import { Component, OnInit } from '@angular/core';
import { DatabaseService } from '../../services/database.service';

@Component({
  selector: 'app-data-browser',
  templateUrl: './data-browser.component.html',
  styleUrls: ['./data-browser.component.css']
})
export class DataBrowserComponent implements OnInit {
  connections: any[] = [];
  selectedConnection: any = null;
  tables: string[] = [];
  selectedTable: string = '';
  tableSchema: any[] = [];
  tableData: any[] = [];
  loading = false;
  error: string | null = null;
  currentPage = 1;
  pageSize = 50;
  totalCount = 0;
  filterColumn = '';
  filterValue = '';
  sortBy = '';
  sortOrder: 'asc' | 'desc' = 'asc';

  constructor(private databaseService: DatabaseService) {}

  ngOnInit(): void {
    this.loadConnections();
  }

  loadConnections(): void {
    this.loading = true;
    this.databaseService.getConnections().subscribe({
      next: (res) => {
        this.connections = res.connections || res;
        this.loading = false;
      },
      error: (err) => {
        console.error('加载连接失败', err);
        // 使用模拟数据
        this.connections = [
          { id: '1', name: '本地SQLite', type: 'sqlite', database: 'chat2db.sqlite' },
          { id: '2', name: '生产MySQL', type: 'mysql', host: 'prod-db.example.com', database: 'production' },
          { id: '3', name: '测试PostgreSQL', type: 'postgresql', host: 'test-db.example.com', database: 'testing' }
        ];
        this.loading = false;
      }
    });
  }

  selectConnection(connection: any): void {
    this.selectedConnection = connection;
    this.loadTables();
  }

  loadTables(): void {
    if (!this.selectedConnection) return;
    
    this.loading = true;
    this.error = null;
    
    this.databaseService.getTables(this.selectedConnection.id).subscribe({
      next: (res) => {
        this.tables = res.tables || res;
        this.loading = false;
      },
      error: (err) => {
        console.error('加载表列表失败', err);
        // 使用模拟数据
        this.tables = ['employees', 'departments', 'projects', 'tasks', 'users'];
        this.loading = false;
      }
    });
  }

  selectTable(table: string): void {
    this.selectedTable = table;
    this.loadTableSchema();
    this.loadTableData();
  }

  loadTableSchema(): void {
    if (!this.selectedConnection || !this.selectedTable) return;
    
    this.loading = true;
    this.error = null;
    
    this.databaseService.getTableSchema(this.selectedConnection.id, this.selectedTable).subscribe({
      next: (res) => {
        this.tableSchema = res.schema || res;
        this.loading = false;
      },
      error: (err) => {
        console.error('加载表结构失败', err);
        // 使用模拟数据
        this.tableSchema = [
          { name: 'id', type: 'INTEGER', nullable: false, primary_key: true },
          { name: 'name', type: 'VARCHAR(255)', nullable: false, primary_key: false },
          { name: 'email', type: 'VARCHAR(255)', nullable: true, primary_key: false },
          { name: 'department_id', type: 'INTEGER', nullable: true, primary_key: false },
          { name: 'salary', type: 'DECIMAL(10,2)', nullable: true, primary_key: false }
        ];
        this.loading = false;
      }
    });
  }

  loadTableData(): void {
    if (!this.selectedConnection || !this.selectedTable) return;
    
    this.loading = true;
    this.error = null;
    
    // 构建查询选项
    const options = {
      filterColumn: this.filterColumn,
      filterValue: this.filterValue,
      sortBy: this.sortBy,
      sortOrder: this.sortOrder,
      page: this.currentPage,
      pageSize: this.pageSize
    };
    
    this.databaseService.queryTableData(this.selectedConnection.id, this.selectedTable, options).subscribe({
      next: (res) => {
        this.tableData = res.data || res.rows || [];
        this.totalCount = res.totalCount || res.count || 0;
        this.loading = false;
      },
      error: (err) => {
        console.error('加载表数据失败', err);
        // 使用模拟数据
        this.tableData = [];
        for (let i = 1; i <= Math.min(this.pageSize, 25); i++) {
          const id = (this.currentPage - 1) * this.pageSize + i;
          this.tableData.push({
            id: id,
            name: `员工${id}`,
            email: `employee${id}@example.com`,
            department_id: Math.floor(Math.random() * 5) + 1,
            salary: Math.floor(Math.random() * 100000) + 30000
          });
        }
        this.totalCount = 125; // 模拟总记录数
        this.loading = false;
      }
    });
  }

  applyFilter(): void {
    this.currentPage = 1;
    this.loadTableData();
  }

  clearFilter(): void {
    this.filterColumn = '';
    this.filterValue = '';
    this.currentPage = 1;
    this.loadTableData();
  }

  sort(column: string): void {
    if (this.sortBy === column) {
      // 切换排序顺序
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      // 设置新的排序列
      this.sortBy = column;
      this.sortOrder = 'asc';
    }
    this.loadTableData();
  }

  nextPage(): void {
    if (this.currentPage * this.pageSize < this.totalCount) {
      this.currentPage++;
      this.loadTableData();
    }
  }

  prevPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadTableData();
    }
  }

  getObjectKeys(obj: any): string[] {
    return Object.keys(obj);
  }

  exportTable(): void {
    if (!this.selectedConnection || !this.selectedTable || this.tableData.length === 0) return;
    
    this.databaseService.exportTableData(this.selectedConnection.id, this.selectedTable).subscribe({
      next: (res) => {
        // 创建下载链接
        const blob = new Blob([res], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `${this.selectedTable}_data.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      },
      error: (err) => {
        console.error('导出数据失败', err);
        alert('导出数据失败，请查看控制台了解详情');
      }
    });
  }
}