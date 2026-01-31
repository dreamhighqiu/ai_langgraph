
import { test, expect } from '@playwright/test';

test('验证登录功能', async ({ page }) => {
  // 导航到登录页面
  await page.goto('http://appadmin.huice.com/fecadmin/login/index');
  
  // 验证登录页面加载成功
  await expect(page.getByRole('heading', { name: 'Fecmall Admin 后台系统' })).toBeVisible();
  
  // 使用admin/123456登录
  await page.getByRole('textbox', { name: '账号' }).fill('admin');
  await page.getByRole('textbox', { name: '密码' }).fill('123456');
  
  // 点击登录按钮 - 使用更通用的定位器
  await page.locator('button:has-text("登录")').click();
  
  // 验证成功登录到管理后台
  await expect(page.getByText('您好: admin')).toBeVisible({ timeout: 10000 });
  await expect(page.getByRole('heading', { name: '产品管理' })).toBeVisible();
  
  console.log('登录成功！');
});