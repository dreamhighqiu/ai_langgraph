import { test, expect } from '@playwright/test';

test.describe('SauceDemo 登录功能测试', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('https://www.saucedemo.com/');
  });

  test('应该成功登录标准用户', async ({ page }) => {
    // 使用标准用户凭据登录
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 验证登录成功
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
    await expect(page.locator('.title')).toContainText('Products');
    await expect(page.locator('.shopping_cart_link')).toBeVisible();
  });

  test('应该成功登录问题用户', async ({ page }) => {
    // 使用问题用户凭据登录
    await page.fill('#user-name', 'problem_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 验证登录成功
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
    await expect(page.locator('.title')).toContainText('Products');
  });

  test('应该成功登录性能测试用户', async ({ page }) => {
    // 使用性能测试用户凭据登录
    await page.fill('#user-name', 'performance_glitch_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 验证登录成功
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
    await expect(page.locator('.title')).toContainText('Products');
  });

  test('应该显示锁定用户的错误信息', async ({ page }) => {
    // 使用锁定用户凭据登录
    await page.fill('#user-name', 'locked_out_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 验证错误信息
    await expect(page.locator('[data-test="error"]')).toBeVisible();
    await expect(page.locator('[data-test="error"]')).toContainText('Epic sadface: Sorry, this user has been locked out.');
  });

  test('应该显示无效凭据的错误信息', async ({ page }) => {
    // 使用无效凭据登录
    await page.fill('#user-name', 'invalid_user');
    await page.fill('#password', 'wrong_password');
    await page.click('#login-button');
    
    // 验证错误信息
    await expect(page.locator('[data-test="error"]')).toBeVisible();
    await expect(page.locator('[data-test="error"]')).toContainText('Epic sadface: Username and password do not match any user in this service');
  });

  test('应该显示空用户名的错误信息', async ({ page }) => {
    // 不填写用户名
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 验证错误信息
    await expect(page.locator('[data-test="error"]')).toBeVisible();
    await expect(page.locator('[data-test="error"]')).toContainText('Epic sadface: Username is required');
  });

  test('应该显示空密码的错误信息', async ({ page }) => {
    // 不填写密码
    await page.fill('#user-name', 'standard_user');
    await page.click('#login-button');
    
    // 验证错误信息
    await expect(page.locator('[data-test="error"]')).toBeVisible();
    await expect(page.locator('[data-test="error"]')).toContainText('Epic sadface: Password is required');
  });

  test('应该能够登出', async ({ page }) => {
    // 先登录
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 点击菜单按钮
    await page.click('#react-burger-menu-btn');
    await page.waitForSelector('.bm-menu-wrap');
    
    // 点击登出链接
    await page.click('#logout_sidebar_link');
    
    // 验证返回登录页面
    await expect(page).toHaveURL('https://www.saucedemo.com/');
    await expect(page.locator('#login-button')).toBeVisible();
  });
});