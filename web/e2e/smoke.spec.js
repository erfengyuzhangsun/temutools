import { test, expect } from '@playwright/test';

test.describe('鲸云策 UAT 冒烟', () => {
  test('首页可访问', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('鲸云策').first()).toBeVisible();
  });

  test('登录页含协议链接', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('link', { name: '《用户服务协议》' }).first()).toBeVisible();
    await expect(page.getByRole('link', { name: '《隐私政策》' }).first()).toBeVisible();
  });

  test('绑店指南页可访问', async ({ page }) => {
    await page.goto('/guide');
    await expect(page.getByText('店铺绑定操作指南')).toBeVisible();
    await expect(page.getByText('agentseller.temu.com')).toBeVisible();
  });

  test('OAuth 成功参数在首页展示', async ({ page }) => {
    await page.goto('/?success=' + encodeURIComponent('测试店铺绑定成功'));
    await expect(page.getByText('测试店铺绑定成功')).toBeVisible();
    await expect(page.getByRole('link', { name: '立即登录' })).toBeVisible();
  });

  test('用户服务协议页可访问', async ({ page }) => {
    await page.goto('/terms');
    await expect(page.getByText('用户服务协议')).toBeVisible();
  });
});
