import { Component, OnInit } from '@angular/core';
import { QueryService } from '../../query.service';
import { NlpService } from '../../services/nlp.service';

@Component({
  selector: 'app-sql-editor',
  templateUrl: './sql-editor.component.html',
  styleUrls: ['./sql-editor.component.css']
})
export class SqlEditorComponent implements OnInit {
  sqlQuery = '';
  results: any[] = [];
  loading = false;
  useNlp = false;
  generatedSql = '';
  executionTime = 0;
  error: string | null = null;

  // 代码补全相关
  tables: string[] = [];
  columns: Map<string, string[]> = new Map();
  suggestions: string[] = [];
  showSuggestions = false;

  constructor(
    private queryService: QueryService,
    private nlpService: NlpService
  ) {}

  ngOnInit(): void {
    // 初始化一些示例数据
    this.tables = ['employees', 'departments', 'projects'];
    this.columns.set('employees', ['id', 'name', 'email', 'department_id', 'salary']);
    this.columns.set('departments', ['id', 'name', 'manager_id']);
    this.columns.set('projects', ['id', 'name', 'department_id', 'start_date', 'end_date']);
    
    // 设置默认查询
    this.sqlQuery = 'SELECT * FROM employees LIMIT 10;';
  }

  executeQuery(): void {
    if (!this.sqlQuery.trim()) return;

    this.loading = true;
    this.error = null;
    const startTime = performance.now();

    if (this.useNlp) {
      // 使用NLP转换自然语言为SQL
      this.nlpService.nl2sql(this.sqlQuery).subscribe({
        next: (res) => {
          this.generatedSql = res.sql;
          this.executeSql(res.sql);
        },
        error: (err) => {
          this.loading = false;
          this.error = `NLP转换失败: ${err.message}`;
        }
      });
    } else {
      // 直接执行SQL
      this.executeSql(this.sqlQuery);
    }
  }

  executeSql(sql: string): void {
    const startTime = performance.now();
    
    this.queryService.query(sql).subscribe({
      next: (res) => {
        const endTime = performance.now();
        this.executionTime = endTime - startTime;
        this.results = res.rows || [];
        this.loading = false;
      },
      error: (err) => {
        const endTime = performance.now();
        this.executionTime = endTime - startTime;
        this.loading = false;
        this.error = err.error || err.message || '查询执行失败';
      }
    });
  }

  formatSql(): void {
    // 简单的SQL格式化
    this.sqlQuery = this.sqlQuery
      .replace(/;/g, ';\n')
      .replace(/SELECT/g, '\nSELECT')
      .replace(/FROM/g, '\nFROM')
      .replace(/WHERE/g, '\nWHERE')
      .replace(/ORDER BY/g, '\nORDER BY')
      .replace(/GROUP BY/g, '\nGROUP BY')
      .replace(/JOIN/g, '\nJOIN')
      .replace(/ON/g, '\nON')
      .trim();
  }

  clearResults(): void {
    this.results = [];
    this.error = null;
    this.executionTime = 0;
  }

  // 代码补全相关方法
  onInput(event: any): void {
    const value = event.target.value;
    const cursorPosition = event.target.selectionStart;
    
    // 简单的关键词补全
    const keywords = [
      'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE',
      'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'VIEW',
      'DATABASE', 'SCHEMA', 'TRIGGER', 'PROCEDURE', 'FUNCTION',
      'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER', 'ON',
      'GROUP', 'ORDER', 'BY', 'HAVING', 'LIMIT', 'OFFSET',
      'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN',
      'IS', 'NULL', 'AS', 'DISTINCT'
    ];
    
    // 获取光标前的单词
    const textBeforeCursor = value.substring(0, cursorPosition);
    const words = textBeforeCursor.split(/\s+/);
    const lastWord = words[words.length - 1].toUpperCase();
    
    if (lastWord.length > 1) {
      this.suggestions = keywords.filter(kw => kw.startsWith(lastWord));
      this.showSuggestions = this.suggestions.length > 0;
    } else {
      this.showSuggestions = false;
    }
  }

  selectSuggestion(suggestion: string): void {
    // 这里应该实现实际的文本插入逻辑
    this.showSuggestions = false;
  }

  exportResults(): void {
    if (this.results.length === 0) return;
    
    // 将结果导出为CSV
    const csvContent = [
      Object.keys(this.results[0]).join(','),
      ...this.results.map(row => Object.values(row).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'query_results.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}