import { test, expect } from '@playwright/test';

test.describe('SauceDemo 购物车功能测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 先登录
    await page.goto('https://www.saucedemo.com/');
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
  });

  test('应该能够添加商品到购物车', async ({ page }) => {
    // 添加第一个商品到购物车
    await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
    
    // 验证按钮文本变为"Remove"
    await expect(page.locator('[data-test="remove-sauce-labs-backpack"]')).toContainText('Remove');
    
    // 验证购物车图标显示数量
    await expect(page.locator('.shopping_cart_badge')).toHaveText('1');
    
    // 添加第二个商品
    await page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click();
    
    // 验证购物车图标更新数量
    await expect(page.locator('.shopping_cart_badge')).toHaveText('2');
  });

  test('应该能够从购物车移除商品', async ({ page }) => {
    // 先添加两个商品
    await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
    await page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click();
    
    // 验证购物车数量
    await expect(page.locator('.shopping_cart_badge')).toHaveText('2');
    
    // 移除第一个商品
    await page.locator('[data-test="remove-sauce-labs-backpack"]').click();
    
    // 验证按钮恢复为"Add to cart"
    await expect(page.locator('[data-test="add-to-cart-sauce-labs-backpack"]')).toContainText('Add to cart');
    
    // 验证购物车数量更新
    await expect(page.locator('.shopping_cart_badge')).toHaveText('1');
    
    // 移除第二个商品
    await page.locator('[data-test="remove-sauce-labs-bike-light"]').click();
    
    // 验证购物车图标消失
    await expect(page.locator('.shopping_cart_badge')).not.toBeVisible();
  });

  test('应该能够从商品详情页添加商品到购物车', async ({ page }) => {
    // 进入商品详情页
    await page.locator('.inventory_item_name').first().click();
    await expect(page).toHaveURL(/inventory-item\.html/);
    
    // 添加商品到购物车
    await page.locator('button').filter({ hasText: 'Add to cart' }).click();
    
    // 验证按钮文本变为"Remove"
    await expect(page.locator('button')).toContainText('Remove');
    
    // 返回商品列表
    await page.click('[data-test="back-to-products"]');
    
    // 验证购物车图标显示数量
    await expect(page.locator('.shopping_cart_badge')).toHaveText('1');
  });

  test('应该能够查看购物车内容', async ({ page }) => {
    // 添加商品到购物车
    await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
    await page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click();
    
    // 点击购物车图标
    await page.click('.shopping_cart_link');
    
    // 验证跳转到购物车页面
    await expect(page).toHaveURL('https://www.saucedemo.com/cart.html');
    await expect(page.locator('.title')).toContainText('Your Cart');
    
    // 验证购物车中有商品
    const cartItems = page.locator('.cart_item');
    await expect(cartItems).toHaveCount(2);
    
    // 验证商品信息显示正确
    await expect(cartItems.nth(0).locator('.inventory_item_name')).toContainText('Sauce Labs Backpack');
    await expect(cartItems.nth(1).locator('.inventory_item_name')).toContainText('Sauce Labs Bike Light');
    
    // 验证每个商品都有移除按钮
    await expect(cartItems.nth(0).locator('button')).toContainText('Remove');
    await expect(cartItems.nth(1).locator('button')).toContainText('Remove');
  });

  test('应该能够从购物车页面移除商品', async ({ page }) => {
    // 添加商品并进入购物车
    await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
    await page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click();
    await page.click('.shopping_cart_link');
    
    // 从购物车移除第一个商品
    await page.locator('[data-test="remove-sauce-labs-backpack"]').click();
    
    // 验证购物车中只剩一个商品
    const cartItems = page.locator('.cart_item');
    await expect(cartItems).toHaveCount(1);
    await expect(cartItems.locator('.inventory_item_name')).toContainText('Sauce Labs Bike Light');
  });

  test('应该能够继续购物', async ({ page }) => {
    // 进入购物车页面
    await page.click('.shopping_cart_link');
    
    // 点击继续购物按钮
    await page.click('[data-test="continue-shopping"]');
    
    // 验证返回商品列表页
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
    await expect(page.locator('.title')).toContainText('Products');
  });

  test('应该能够前往结账页面', async ({ page }) => {
    // 添加商品并进入购物车
    await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
    await page.click('.shopping_cart_link');
    
    // 点击结账按钮
    await page.click('[data-test="checkout"]');
    
    // 验证跳转到结账信息页面
    await expect(page).toHaveURL('https://www.saucedemo.com/checkout-step-one.html');
    await expect(page.locator('.title')).toContainText('Checkout: Your Information');
  });

  test('应该能够清空购物车', async ({ page }) => {
    // 添加多个商品
    await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
    await page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click();
    await page.locator('[data-test="add-to-cart-sauce-labs-bolt-t-shirt"]').click();
    
    // 验证购物车数量
    await expect(page.locator('.shopping_cart_badge')).toHaveText('3');
    
    // 打开菜单
    await page.click('#react-burger-menu-btn');
    await page.waitForSelector('.bm-menu-wrap');
    
    // 点击重置应用状态
    await page.click('#reset_sidebar_link');
    
    // 验证购物车被清空
    await expect(page.locator('.shopping_cart_badge')).not.toBeVisible();
    
    // 进入购物车页面验证
    await page.click('.shopping_cart_link');
    const cartItems = page.locator('.cart_item');
    await expect(cartItems).toHaveCount(0);
    
    // 验证空购物车消息
    await expect(page.locator('.cart_list')).toBeVisible();
  });
});