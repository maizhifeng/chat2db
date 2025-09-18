import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { environment } from '../environments/environment';
import { AuthService } from './services/auth.service';

@Injectable({ providedIn: 'root' })
export class QueryService {
  private base = environment.apiBase;
  
  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  query(nl: string): Observable<any> {
    // For public queries, no auth needed
    return this.http.post(`${this.base}/query`, { query: nl });
  }

  // call chat with optional model override
  chat(message: string, history: any[] = [], model?: string): Observable<any> {
    const payload: any = { message, history };
    if (model) payload.model = model;
    // For chat, no auth needed
    return this.http.post(`${this.base}/chat`, payload);
  }

  // Stream chat with optional model override
  streamChat(message: string, history: any[] = [], model?: string): Observable<any> {
    const payload: any = { message, history, stream: true };
    if (model) payload.model = model;
    
    // Create a Subject to emit the streaming responses
    const subject = new Subject<any>();
    
    // Make the request using fetch API to handle streaming
    const url = `${this.base}/chat`;
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    };
    
    // Use fetch API to handle streaming responses
    fetch(url, options)
      .then(response => {
        if (!response.body) {
          throw new Error('ReadableStream not supported');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        function read() {
          reader.read().then(({ done, value }) => {
            if (done) {
              subject.complete();
              return;
            }
            
            // Decode the chunk and process SSE format
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6); // Remove 'data: ' prefix
                if (data === '[DONE]') {
                  subject.complete();
                  return;
                }
                
                try {
                  const jsonData = JSON.parse(data);
                  
                  // Handle different status types
                  if (jsonData.status === 'thinking') {
                    subject.next({ type: 'thinking', message: jsonData.message });
                  } else if (jsonData.status === 'responding') {
                    subject.next({ type: 'responding', message: jsonData.message });
                  } else if (jsonData.status === 'chunk') {
                    subject.next({ type: 'chunk', response: jsonData.response });
                  } else if (jsonData.status === 'result') {
                    subject.next({ type: 'result', response: jsonData.response });
                  } else if (jsonData.status === 'error') {
                    subject.next({ type: 'error', message: jsonData.message || jsonData.error });
                  } else {
                    // Default handling for other responses
                    subject.next(jsonData);
                  }
                } catch (e) {
                  console.error('Error parsing JSON:', e);
                  subject.next({ type: 'raw', data: data });
                }
              }
            }
            
            read(); // Continue reading
          }).catch(error => {
            subject.error(error);
          });
        }
        
        read(); // Start reading
      })
      .catch(error => {
        subject.error(error);
      });
    
    return subject.asObservable();
  }

  // list available models (proxied by backend)
  getModels(): Observable<any> {
    // For models, no auth needed
    return this.http.get(`${this.base}/models`);
  }
}