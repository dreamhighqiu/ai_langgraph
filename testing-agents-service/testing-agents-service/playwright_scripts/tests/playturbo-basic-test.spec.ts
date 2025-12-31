import { test, expect } from '@playwright/test';

test('PlayTurbo网站基本功能测试', async ({ page }) => {
  // 测试1: 访问主页
  console.log('测试1: 访问主页...');
  await page.goto('https://www.playturbo.com/');
  
  // 检查页面标题
  const title = await page.title();
  console.log(`页面标题: ${title}`);
  expect(title).toBeTruthy();
  
  // 检查页面基本元素
  console.log('检查页面基本元素...');
  await expect(page.locator('body')).toBeVisible();
  
  // 检查是否有header
  const header = page.locator('header');
  if (await header.count() > 0) {
    console.log('找到header元素');
    await expect(header.first()).toBeVisible();
  }
  
  // 检查是否有main内容
  const main = page.locator('main');
  if (await main.count() > 0) {
    console.log('找到main元素');
    await expect(main.first()).toBeVisible();
  }
  
  // 检查导航链接
  console.log('检查导航链接...');
  const navLinks = page.locator('nav a, header a, a[href]');
  const linkCount = await navLinks.count();
  console.log(`找到 ${linkCount} 个链接`);
  
  if (linkCount > 0) {
    // 测试第一个链接
    const firstLink = navLinks.first();
    const href = await firstLink.getAttribute('href');
    console.log(`第一个链接: ${href}`);
    
    if (href && !href.startsWith('#') && !href.startsWith('javascript:')) {
      console.log('点击第一个链接...');
      await firstLink.click();
      await page.waitForLoadState('networkidle');
      
      // 检查新页面加载
      await expect(page.locator('body')).toBeVisible();
      console.log('链接点击成功，页面加载正常');
    }
  }
  
  // 截图记录
  console.log('截图记录...');
  await page.screenshot({ path: 'playturbo-test.png', fullPage: true });
  
  console.log('测试完成！');
});

test('PlayTurbo网站响应式测试', async ({ page }) => {
  console.log('测试响应式设计...');
  
  // 访问网站
  await page.goto('https://www.playturbo.com/');
  
  // 测试不同屏幕尺寸
  const viewports = [
    { width: 1920, height: 1080, name: 'desktop' },
    { width: 768, height: 1024, name: 'tablet' },
    { width: 375, height: 667, name: 'mobile' }
  ];
  
  for (const viewport of viewports) {
    console.log(`测试 ${viewport.name} 视图 (${viewport.width}x${viewport.height})`);
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    
    // 检查页面显示
    await expect(page.locator('body')).toBeVisible();
    
    // 截图
    await page.screenshot({ 
      path: `playturbo-${viewport.name}.png`,
      fullPage: true 
    });
  }
  
  console.log('响应式测试完成！');
});

test('PlayTurbo网站性能测试', async ({ page }) => {
  console.log('测试页面性能...');
  
  // 测量加载时间
  const startTime = Date.now();
  await page.goto('https://www.playturbo.com/');
  await page.waitForLoadState('networkidle');
  const loadTime = Date.now() - startTime;
  
  console.log(`页面加载时间: ${loadTime}ms`);
  
  // 检查加载时间是否合理
  expect(loadTime).toBeLessThan(10000); // 10秒内
  
  // 检查资源加载
  const resourceCount = await page.evaluate(() => {
    return performance.getEntriesByType('resource').length;
  });
  
  console.log(`加载的资源数量: ${resourceCount}`);
  
  console.log('性能测试完成！');
});