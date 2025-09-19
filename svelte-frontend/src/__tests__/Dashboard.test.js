import { render } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Dashboard from '../components/dashboard/Dashboard.svelte';

describe('Dashboard Component', () => {
  it('should render correctly', () => {
    const { getByText } = render(Dashboard);
    
    // Check if the main title is rendered
    expect(getByText('仪表板')).toBeInTheDocument();
    
    // Check if navigation cards are rendered
    expect(getByText('基础查询')).toBeInTheDocument();
    expect(getByText('AI助手')).toBeInTheDocument();
    expect(getByText('SQL编辑器')).toBeInTheDocument();
    expect(getByText('数据浏览器')).toBeInTheDocument();
    expect(getByText('连接管理')).toBeInTheDocument();
    expect(getByText('表管理')).toBeInTheDocument();
  });
});