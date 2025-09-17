import { Component, OnInit } from '@angular/core';
import { ConnectionService } from '../../services/connection.service';
import { DatabaseConnection } from '../../models/connection.model';

@Component({
  selector: 'app-connection-manager',
  templateUrl: './connection-manager.component.html',
  styleUrls: ['./connection-manager.component.css']
})
export class ConnectionManagerComponent implements OnInit {
  connections: DatabaseConnection[] = [];
  showForm = false;
  isEditing = false;
  currentConnection: DatabaseConnection = this.getEmptyConnection();
  testResult: { success: boolean; message: string } | null = null;

  constructor(private connectionService: ConnectionService) { }

  ngOnInit(): void {
    this.loadConnections();
  }

  loadConnections(): void {
    this.connectionService.getConnections().subscribe({
      next: (connections) => {
        // Filter out connections with empty IDs
        this.connections = connections.filter(conn => conn.id && conn.id.trim() !== '');
      },
      error: (error) => {
        console.error('Error loading connections', error);
        this.testResult = { success: false, message: '加载连接失败: ' + (error.error?.error || error.message) };
      }
    });
  }

  showCreateForm(): void {
    this.isEditing = false;
    this.currentConnection = this.getEmptyConnection();
    this.showForm = true;
    this.testResult = null;
  }

  editConnection(connection: DatabaseConnection): void {
    // Check if connection ID is valid
    if (!connection.id || connection.id.trim() === '') {
      this.testResult = { success: false, message: '连接ID无效，无法编辑' };
      return;
    }
    
    this.isEditing = true;
    this.currentConnection = { ...connection };
    this.showForm = true;
    this.testResult = null;
  }

  cancelForm(): void {
    this.showForm = false;
    this.testResult = null;
  }

  saveConnection(): void {
    // Validate required fields
    if (!this.currentConnection.name || !this.currentConnection.type || !this.currentConnection.database) {
      this.testResult = { success: false, message: '请填写所有必填字段' };
      return;
    }
    
    if (this.isEditing) {
      // Check if connection ID is valid
      if (!this.currentConnection.id || this.currentConnection.id.trim() === '') {
        this.testResult = { success: false, message: '连接ID无效，无法更新' };
        return;
      }
      
      // Update existing connection
      this.connectionService.updateConnection(this.currentConnection.id, this.currentConnection).subscribe({
        next: (updated) => {
          this.loadConnections();
          this.showForm = false;
          this.testResult = { success: true, message: '连接更新成功' };
        },
        error: (error) => {
          console.error('Error updating connection', error);
          this.testResult = { success: false, message: '连接更新失败: ' + (error.error?.error || error.message) };
        }
      });
    } else {
      // Create new connection
      // Generate a unique ID if not provided
      if (!this.currentConnection.id || this.currentConnection.id.trim() === '') {
        this.currentConnection.id = 'conn-' + Date.now();
      }
      
      this.connectionService.createConnection(this.currentConnection).subscribe({
        next: (created) => {
          this.loadConnections();
          this.showForm = false;
          this.testResult = { success: true, message: '连接创建成功' };
        },
        error: (error) => {
          console.error('Error creating connection', error);
          this.testResult = { success: false, message: '连接创建失败: ' + (error.error?.error || error.message) };
        }
      });
    }
  }

  deleteConnection(id: string): void {
    // Check if ID is valid
    if (!id || id.trim() === '') {
      this.testResult = { success: false, message: '连接ID无效，无法删除' };
      return;
    }
    
    if (confirm('确定要删除这个连接吗?')) {
      this.connectionService.deleteConnection(id).subscribe({
        next: () => {
          this.loadConnections();
          this.testResult = { success: true, message: '连接删除成功' };
        },
        error: (error) => {
          console.error('Error deleting connection', error);
          this.testResult = { success: false, message: '连接删除失败: ' + (error.error?.error || error.message) };
        }
      });
    }
  }

  testConnection(id: string): void {
    // Check if ID is valid
    if (!id || id.trim() === '') {
      this.testResult = { success: false, message: '连接ID无效，无法测试' };
      return;
    }
    
    this.connectionService.testConnection(id).subscribe({
      next: (result) => {
        this.testResult = { success: true, message: result.message || '连接测试成功' };
      },
      error: (error) => {
        console.error('Error testing connection', error);
        this.testResult = { success: false, message: '连接测试失败: ' + (error.error?.error || error.message) };
      }
    });
  }

  private getEmptyConnection(): DatabaseConnection {
    return {
      id: '',
      name: '',
      type: 'sqlite',
      host: '',
      port: 3306,
      username: '',
      password: '',
      database: '',
      environment: 'dev',
      file_path: ''
    };
  }
}