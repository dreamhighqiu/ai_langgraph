
import{test,expect}from'@playwright/test';

test('seed',async({page})=>{
// 访问应用首页
// TODO: 修改为你要测试的实际应用 URL
// await page.goto('http://localhost:5173');

// 等待页面加载完成
await expect(page.locator('body')).toBeVisible();

// 可选：执行登录等初始化操作
// await page.getByRole('button', { name: '登录' }).click();
// await page.fill('#username', 'testuser');
// await page.fill('#password', 'password123');
// await page.getByRole('button', { name: '提交' }).click();
});