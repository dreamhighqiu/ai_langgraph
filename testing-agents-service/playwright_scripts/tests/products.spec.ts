import { test, expect } from '@playwright/test';

test.describe('SauceDemo 商品浏览和筛选功能测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 先登录
    await page.goto('https://www.saucedemo.com/');
    await page.fill('#user-name', 'standard_user');
    await page.fill('#password', 'secret_sauce');
    await page.click('#login-button');
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
  });

  test('应该显示商品列表', async ({ page }) => {
    // 验证商品列表显示
    const productItems = page.locator('.inventory_item');
    await expect(productItems).toHaveCount(6);
    
    // 验证每个商品都有名称、描述、价格和图片
    for (let i = 0; i < 6; i++) {
      const item = productItems.nth(i);
      await expect(item.locator('.inventory_item_name')).toBeVisible();
      await expect(item.locator('.inventory_item_desc')).toBeVisible();
      await expect(item.locator('.inventory_item_price')).toBeVisible();
      await expect(item.locator('.inventory_item_img img')).toBeVisible();
      await expect(item.locator('button')).toContainText('Add to cart');
    }
  });

  test('应该能够按名称A-Z排序', async ({ page }) => {
    // 选择A-Z排序
    await page.selectOption('.product_sort_container', 'az');
    
    // 获取第一个商品名称
    const firstItemName = await page.locator('.inventory_item_name').first().textContent();
    
    // 验证排序正确（第一个应该是"Sauce Labs Backpack"）
    expect(firstItemName).toBe('Sauce Labs Backpack');
  });

  test('应该能够按名称Z-A排序', async ({ page }) => {
    // 选择Z-A排序
    await page.selectOption('.product_sort_container', 'za');
    
    // 获取第一个商品名称
    const firstItemName = await page.locator('.inventory_item_name').first().textContent();
    
    // 验证排序正确（第一个应该是"Test.allTheThings() T-Shirt (Red)"）
    expect(firstItemName).toBe('Test.allTheThings() T-Shirt (Red)');
  });

  test('应该能够按价格从低到高排序', async ({ page }) => {
    // 选择价格从低到高排序
    await page.selectOption('.product_sort_container', 'lohi');
    
    // 获取所有商品价格
    const priceElements = page.locator('.inventory_item_price');
    const prices: number[] = [];
    
    for (let i = 0; i < 6; i++) {
      const priceText = await priceElements.nth(i).textContent();
      const price = parseFloat(priceText!.replace('$', ''));
      prices.push(price);
    }
    
    // 验证价格是升序排列
    for (let i = 0; i < prices.length - 1; i++) {
      expect(prices[i]).toBeLessThanOrEqual(prices[i + 1]);
    }
  });

  test('应该能够按价格从高到低排序', async ({ page }) => {
    // 选择价格从高到低排序
    await page.selectOption('.product_sort_container', 'hilo');
    
    // 获取所有商品价格
    const priceElements = page.locator('.inventory_item_price');
    const prices: number[] = [];
    
    for (let i = 0; i < 6; i++) {
      const priceText = await priceElements.nth(i).textContent();
      const price = parseFloat(priceText!.replace('$', ''));
      prices.push(price);
    }
    
    // 验证价格是降序排列
    for (let i = 0; i < prices.length - 1; i++) {
      expect(prices[i]).toBeGreaterThanOrEqual(prices[i + 1]);
    }
  });

  test('应该能够查看商品详情', async ({ page }) => {
    // 点击第一个商品
    await page.locator('.inventory_item_name').first().click();
    
    // 验证跳转到商品详情页
    await expect(page).toHaveURL(/inventory-item\.html/);
    
    // 验证商品详情信息显示
    await expect(page.locator('.inventory_details_name')).toBeVisible();
    await expect(page.locator('.inventory_details_desc')).toBeVisible();
    await expect(page.locator('.inventory_details_price')).toBeVisible();
    await expect(page.locator('.inventory_details_img')).toBeVisible();
    await expect(page.locator('button')).toContainText('Add to cart');
    
    // 验证返回按钮存在
    await expect(page.locator('[data-test="back-to-products"]')).toBeVisible();
  });

  test('应该能够从详情页返回商品列表', async ({ page }) => {
    // 进入商品详情页
    await page.locator('.inventory_item_name').first().click();
    await expect(page).toHaveURL(/inventory-item\.html/);
    
    // 点击返回按钮
    await page.click('[data-test="back-to-products"]');
    
    // 验证返回商品列表页
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');
    await expect(page.locator('.title')).toContainText('Products');
  });

  test('应该能够重置应用状态', async ({ page }) => {
    // 先添加一些商品到购物车
    await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
    await page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click();
    
    // 验证购物车图标显示数量
    await expect(page.locator('.shopping_cart_badge')).toHaveText('2');
    
    // 打开菜单
    await page.click('#react-burger-menu-btn');
    await page.waitForSelector('.bm-menu-wrap');
    
    // 点击重置应用状态
    await page.click('#reset_sidebar_link');
    
    // 验证购物车被清空
    await expect(page.locator('.shopping_cart_badge')).not.toBeVisible();
    
    // 验证添加按钮恢复
    await expect(page.locator('[data-test="add-to-cart-sauce-labs-backpack"]')).toBeVisible();
    await expect(page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]')).toBeVisible();
  });
});