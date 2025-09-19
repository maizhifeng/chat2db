import { render } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import Query from '../Query.svelte';

// Mock the API functions
vi.mock('../api.js', () => ({
  query: vi.fn(),
  chat: vi.fn(),
  getModels: vi.fn(),
  encodeText: vi.fn(),
  calculateSimilarity: vi.fn()
}));

describe('Query Component', () => {
  it('should render correctly', () => {
    const { getByText } = render(Query);
    
    // Check if the main title is rendered
    expect(getByText('Chat2DB 简易演示')).toBeInTheDocument();
    
    // Check if the textarea is rendered
    const textarea = document.querySelector('textarea');
    expect(textarea).toBeInTheDocument();
    
    // Check if buttons are rendered
    expect(getByText('刷新模型')).toBeInTheDocument();
    expect(getByText('加载并发送')).toBeInTheDocument();
    expect(getByText('发送（SQL）')).toBeInTheDocument();
  });
});