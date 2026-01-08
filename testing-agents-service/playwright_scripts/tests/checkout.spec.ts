import { test, expect } from '@playwright/test';

test.describe('SauceDemo 结账流程测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 先登录并添加商品到购物车
    await page.goto('https://www.saucedemo.com/');
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
    
    // 添加商品到购物车
    await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
    await page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click();
    
    // 进入购物车
    await page.click('.shopping_cart_link');
    await expect(page).toHaveURL('https://www.saucedemo.com/cart.html');
  });

  test('应该能够填写结账信息', async ({ page }) => {
    // 开始结账
    await page.click('[data-test="checkout"]');
    
    // 填写结账信息
    await page.fill('[data-test="firstName"]', 'John');
    await page.fill('[data-test="lastName"]', 'Doe');
    await page.fill('[data-test="postalCode"]', '12345');
    
    // 继续到下一步
    await page.click('[data-test="continue"]');
    
    // 验证跳转到订单概览页面
    await expect(page).toHaveURL('https://www.saucedemo.com/checkout-step-two.html');
    await expect(page.locator('.title')).toContainText('Checkout: Overview');
  });

  test('应该显示空名字的错误信息', async ({ page }) => {
    // 开始结账
    await page.click('[data-test="checkout"]');
    
    // 不填写名字，直接继续
    await page.fill('[data-test="lastName"]', 'Doe');
    await page.fill('[data-test="postalCode"]', '12345');
    await page.click('[data-test="continue"]');
    
    // 验证错误信息
    await expect(page.locator('[data-test="error"]')).toBeVisible();
    await expect(page.locator('[data-test="error"]')).toContainText('Error: First Name is required');
  });

  test('应该显示空姓氏的错误信息', async ({ page }) => {
    // 开始结账
    await page.click('[data-test="checkout"]');
    
    // 不填写姓氏，直接继续
    await page.fill('[data-test="firstName"]', 'John');
    await page.fill('[data-test="postalCode"]', '12345');
    await page.click('[data-test="continue"]');
    
    // 验证错误信息
    await expect(page.locator('[data-test="error"]')).toBeVisible();
    await expect(page.locator('[data-test="error"]')).toContainText('Error: Last Name is required');
  });

  test('应该显示空邮政编码的错误信息', async ({ page }) => {
    // 开始结账
    await page.click('[data-test="checkout"]');
    
    // 不填写邮政编码，直接继续
    await page.fill('[data-test="firstName"]', 'John');
    await page.fill('[data-test="lastName"]', 'Doe');
    await page.click('[data-test="continue"]');
    
    // 验证错误信息
    await expect(page.locator('[data-test="error"]')).toBeVisible();
    await expect(page.locator('[data-test="error"]')).toContainText('Error: Postal Code is required');
  });

  test('应该能够取消结账', async ({ page }) => {
    // 开始结账
    await page.click('[data-test="checkout"]');
    
    // 点击取消按钮
    await page.click('[data-test="cancel"]');
    
    // 验证返回购物车页面
    await expect(page).toHaveURL('https://www.saucedemo.com/cart.html');
    await expect(page.locator('.title')).toContainText('Your Cart');
  });

  test('应该显示订单概览信息', async ({ page }) => {
    // 完成结账信息填写
    await page.click('[data-test="checkout"]');
    await page.fill('[data-test="firstName"]', 'John');
    await page.fill('[data-test="lastName"]', 'Doe');
    await page.fill('[data-test="postalCode"]', '12345');
    await page.click('[data-test="continue"]');
    
    // 验证订单概览信息
    await expect(page.locator('.cart_item')).toHaveCount(2);
    
    // 验证商品信息
    await expect(page.locator('.inventory_item_name').first()).toContainText('Sauce Labs Backpack');
    await expect(page.locator('.inventory_item_name').nth(1)).toContainText('Sauce Labs Bike Light');
    
    // 验证支付信息
    await expect(page.locator('.summary_info_label').filter({ hasText: 'Payment Information' })).toBeVisible();
    await expect(page.locator('.summary_value_label').first()).toContainText('SauceCard');
    
    // 验证配送信息
    await expect(page.locator('.summary_info_label').filter({ hasText: 'Shipping Information' })).toBeVisible();
    await expect(page.locator('.summary_value_label').nth(1)).toContainText('Free Pony Express Delivery!');
    
    // 验证价格摘要
    await expect(page.locator('.summary_subtotal_label')).toBeVisible();
    await expect(page.locator('.summary_tax_label')).toBeVisible();
    await expect(page.locator('.summary_total_label')).toBeVisible();
  });

  test('应该能够完成订单', async ({ page }) => {
    // 完成结账信息填写
    await page.click('[data-test="checkout"]');
    await page.fill('[data-test="firstName"]', 'John');
    await page.fill('[data-test="lastName"]', 'Doe');
    await page.fill('[data-test="postalCode"]', '12345');
    await page.click('[data-test="continue"]');
    
    // 完成订单
    await page.click('[data-test="finish"]');
    
    // 验证订单完成页面
    await expect(page).toHaveURL('https://www.saucedemo.com/checkout-complete.html');
    await expect(page.locator('.title')).toContainText('Checkout: Complete!');
    
    // 验证成功消息
    await expect(page.locator('.complete-header')).toContainText('Thank you for your order!');
    await expect(page.locator('.complete-text')).toContainText('Your order has been dispatched, and will arrive just as fast as the pony can get there!');
  });

  test('应该能够从完成页面返回首页', async ({ page }) => {
    // 完成整个结账流程
    await page.click('[data-test="checkout"]');
    await page.fill('[data-test="firstName"]', 'John');
    await page.fill('[data-test="lastName"]', 'Doe');
    await page.fill('[data-test="postalCode"]', '12345');
    await page.click('[data-test="continue"]');
    await page.click('[data-test="finish"]');
    
    // 点击返回首页按钮
    await page.click('[data-test="back-to-products"]');
    
    // 验证返回商品列表页
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
    await expect(page.locator('.title')).toContainText('Products');
    
    // 验证购物车被清空
    await expect(page.locator('.shopping_cart_badge')).not.toBeVisible();
  });

  test('应该能够从订单概览取消结账', async ({ page }) => {
    // 完成结账信息填写
    await page.click('[data-test="checkout"]');
    await page.fill('[data-test="firstName"]', 'John');
    await page.fill('[data-test="lastName"]', 'Doe');
    await page.fill('[data-test="postalCode"]', '12345');
    await page.click('[data-test="continue"]');
    
    // 点击取消按钮
    await page.click('[data-test="cancel"]');
    
    // 验证返回商品列表页
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
    await expect(page.locator('.title')).toContainText('Products');
  });

  test('应该计算正确的订单总价', async ({ page }) => {
    // 获取商品价格
    await page.goto('https://www.saucedemo.com/inventory.html');
    const backpackPriceText = await page.locator('[data-test="inventory-item-price"]').first().textContent();
    const bikeLightPriceText = await page.locator('[data-test="inventory-item-price"]').nth(1).textContent();
    
    const backpackPrice = parseFloat(backpackPriceText!.replace('$', ''));
    const bikeLightPrice = parseFloat(bikeLightPriceText!.replace('$', ''));
    const subtotal = backpackPrice + bikeLightPrice;
    const tax = subtotal * 0.08; // 8% tax rate
    const total = subtotal + tax;
    
    // 完成结账流程
    await page.click('.shopping_cart_link');
    await page.click('[data-test="checkout"]');
    await page.fill('[data-test="firstName"]', 'John');
    await page.fill('[data-test="lastName"]', 'Doe');
    await page.fill('[data-test="postalCode"]', '12345');
    await page.click('[data-test="continue"]');
    
    // 验证价格计算正确
    const subtotalText = await page.locator('.summary_subtotal_label').textContent();
    const taxText = await page.locator('.summary_tax_label').textContent();
    const totalText = await page.locator('.summary_total_label').textContent();
    
    expect(subtotalText).toContain(`Item total: $${subtotal.toFixed(2)}`);
    expect(taxText).toContain(`Tax: $${tax.toFixed(2)}`);
    expect(totalText).toContain(`Total: $${total.toFixed(2)}`);
  });
});