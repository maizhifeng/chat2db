import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from './src/environments/environment';

@Injectable({ providedIn: 'root' })
export class QueryService {
  private base = environment.apiBase;
  constructor(private http: HttpClient) {}

  query(nl: string): Observable<any> {
    return this.http.post(`${this.base}/query`, { query: nl });
  }

  // call chat with optional model override
  chat(message: string, history: any[] = [], model?: string): Observable<any> {
    const payload: any = { message, history };
    if (model) payload.model = model;
    return this.http.post(`${this.base}/chat`, payload);
  }

  // list available models (proxied by backend)
  getModels(): Observable<any> {
    return this.http.get(`${this.base}/models`);
  }
  
  // 新增 Embeddings 相关方法
  /**
   * 将文本编码为向量
   * @param text 要编码的文本
   * @returns 文本的向量表示
   */
  encodeText(text: string): Observable<any> {
    return this.http.post(`${this.base}/embeddings/encode`, { text });
  }
  
  /**
   * 计算两个文本的相似度
   * @param text1 第一个文本
   * @param text2 第二个文本
   * @returns 两个文本的相似度
   */
  calculateSimilarity(text1: string, text2: string): Observable<any> {
    return this.http.post(`${this.base}/embeddings/similarity`, { text1, text2 });
  }
}