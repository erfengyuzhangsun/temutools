import { test, expect } from '@playwright/test';

const apiBase = process.env.API_BASE_URL || 'https://www.jinpuhuang.com';

test.describe('API 合规冒烟', () => {
  test('未同意协议注册应返回 400', async ({ request }) => {
    const email = `uat_no_consent_${Date.now()}@example.com`;
    const res = await request.post(`${apiBase}/api/v1/auth/register`, {
      data: { email, password: 'securePass123' },
    });
    expect(res.status()).toBe(400);
    const body = await res.json();
    expect(body.success).toBe(false);
    expect(body.error?.message || '').toMatch(/协议|隐私/);
  });
});
