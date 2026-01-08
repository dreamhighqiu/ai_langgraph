import { test, expect } from '@playwright/test';

test.describe('Sauce Demo 网站自动化测试', () => {
  test.beforeEach(async ({ page }) => {
    // 访问网站
    await page.goto('https://www.saucedemo.com/');
    await expect(page).toHaveTitle('Swag Labs');
  });

  test('测试1: 验证页面加载和标题', async ({ page }) => {
    // 验证页面标题
    await expect(page.locator('.login_logo')).toHaveText('Swag Labs');
    
    // 验证登录表单存在
    await expect(page.locator('#user-name')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('#login-button')).toBeVisible();
    
    // 截图记录
    await page.screenshot({ path: 'screenshot_homepage.png' });
  });

  test('测试2: 使用标准用户登录', async ({ page }) => {
    // 输入标准用户凭据
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    
    // 点击登录按钮
    await page.click('#login-button');
    
    // 验证登录成功
    await expect(page.locator('.title')).toHaveText('Products');
    await expect(page.locator('.inventory_item')).toHaveCount(6);
    
    // 截图记录
    await page.screenshot({ path: 'screenshot_login_success.png' });
  });

  test('测试3: 使用错误凭据登录', async ({ page }) => {
    // 输入错误凭据
    await page.fill('#user-name', 'wrong_user');
    await page.fill('#password', 'wrong_password');
    
    // 点击登录按钮
    await page.click('#login-button');
    
    // 验证错误消息
    await expect(page.locator('[data-test="error"]')).toContainText(
      'Epic sadface: Username and password do not match'
    );
    
    // 截图记录
    await page.screenshot({ path: 'screenshot_login_failure.png' });
  });

  test('测试4: 商品浏览和排序功能', async ({ page }) => {
    // 先登录
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 验证商品列表
    await expect(page.locator('.inventory_item_name')).toHaveCount(6);
    
    // 测试排序功能 - 按名称排序
    await page.selectOption('.product_sort_container', 'az');
    const firstItemAZ = await page.locator('.inventory_item_name').first().textContent();
    console.log('按名称排序第一个商品:', firstItemAZ);
    
    // 测试排序功能 - 按价格从低到高
    await page.selectOption('.product_sort_container', 'lohi');
    const firstItemPrice = await page.locator('.inventory_item_price').first().textContent();
    console.log('按价格排序第一个商品价格:', firstItemPrice);
    
    // 截图记录
    await page.screenshot({ path: 'screenshot_product_sorting.png' });
  });

  test('测试5: 添加商品到购物车', async ({ page }) => {
    // 先登录
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 添加第一个商品到购物车
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    
    // 验证购物车数量更新
    await expect(page.locator('.shopping_cart_badge')).toHaveText('1');
    
    // 添加第二个商品到购物车
    await page.click('[data-test="add-to-cart-sauce-labs-bike-light"]');
    
    // 验证购物车数量更新为2
    await expect(page.locator('.shopping_cart_badge')).toHaveText('2');
    
    // 截图记录
    await page.screenshot({ path: 'screenshot_add_to_cart.png' });
  });

  test('测试6: 查看购物车和移除商品', async ({ page }) => {
    // 先登录并添加商品
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 添加两个商品
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    await page.click('[data-test="add-to-cart-sauce-labs-bike-light"]');
    
    // 进入购物车
    await page.click('.shopping_cart_link');
    
    // 验证购物车页面
    await expect(page.locator('.title')).toHaveText('Your Cart');
    await expect(page.locator('.cart_item')).toHaveCount(2);
    
    // 移除一个商品
    await page.click('[data-test="remove-sauce-labs-backpack"]');
    
    // 验证商品数量减少
    await expect(page.locator('.cart_item')).toHaveCount(1);
    
    // 截图记录
    await page.screenshot({ path: 'screenshot_cart_remove.png' });
  });

  test('测试7: 完整的结账流程', async ({ page }) => {
    // 先登录并添加商品
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 添加商品到购物车
    await page.click('[data-test="add-to-cart-sauce-labs-backpack"]');
    
    // 进入购物车
    await page.click('.shopping_cart_link');
    
    // 开始结账
    await page.click('[data-test="checkout"]');
    
    // 填写个人信息
    await expect(page.locator('.title')).toHaveText('Checkout: Your Information');
    await page.fill('[data-test="firstName"]', 'John');
    await page.fill('[data-test="lastName"]', 'Doe');
    await page.fill('[data-test="postalCode"]', '12345');
    
    // 继续到下一步
    await page.click('[data-test="continue"]');
    
    // 验证订单概览
    await expect(page.locator('.title')).toHaveText('Checkout: Overview');
    await expect(page.locator('.cart_item')).toHaveCount(1);
    
    // 完成订单
    await page.click('[data-test="finish"]');
    
    // 验证订单完成
    await expect(page.locator('.complete-header')).toHaveText('Thank you for your order!');
    
    // 截图记录
    await page.screenshot({ path: 'screenshot_checkout_complete.png' });
  });

  test('测试8: 登出功能', async ({ page }) => {
    // 先登录
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    
    // 打开菜单
    await page.click('#react-burger-menu-btn');
    
    // 点击登出
    await page.click('[data-test="logout-sidebar-link"]');
    
    // 验证返回登录页面
    await expect(page.locator('.login_logo')).toHaveText('Swag Labs');
    await expect(page.locator('#login-button')).toBeVisible();
    
    // 截图记录
    await page.screenshot({ path: 'screenshot_logout.png' });
  });

  test('测试9: 性能测试 - 页面加载时间', async ({ page }) => {
    // 记录页面加载时间
    const startTime = Date.now();
    await page.goto('https://www.saucedemo.com/');
    const loadTime = Date.now() - startTime;
    
    console.log(`页面加载时间: ${loadTime}ms`);
    
    // 验证页面在合理时间内加载完成
    expect(loadTime).toBeLessThan(5000); // 5秒内加载完成
    
    // 截图记录
    await page.screenshot({ path: 'screenshot_performance.png' });
  });

  test('测试10: 响应式测试 - 不同视口大小', async ({ page }) => {
    // 测试桌面视图
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('https://www.saucedemo.com/');
    await page.screenshot({ path: 'screenshot_desktop.png' });
    
    // 测试平板视图
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('https://www.saucedemo.com/');
    await page.screenshot({ path: 'screenshot_tablet.png' });
    
    // 测试手机视图
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('https://www.saucedemo.com/');
    await page.screenshot({ path: 'screenshot_mobile.png' });
    
    // 验证登录表单在不同尺寸下都可见
    await expect(page.locator('#login-button')).toBeVisible();
  });
});