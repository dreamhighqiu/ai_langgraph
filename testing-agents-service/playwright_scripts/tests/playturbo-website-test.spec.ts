import { test, expect } from '@playwright/test';

test.describe('PlayTurbo网站功能测试', () => {
  test.beforeEach(async ({ page }) => {
    // 访问网站主页
    await page.goto('https://www.playturbo.com/');
    await page.waitForLoadState('networkidle');
  });

  test('主页加载和基本元素检查', async ({ page }) => {
    // 检查页面标题
    await expect(page).toHaveTitle(/PlayTurbo/);
    
    // 检查主要元素存在
    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();
    
    // 检查Logo
    const logo = page.locator('img[alt*="PlayTurbo"], img[alt*="logo"], .logo');
    await expect(logo.first()).toBeVisible();
    
    // 检查导航菜单
    const navLinks = page.locator('nav a, header a');
    await expect(navLinks.first()).toBeVisible();
    
    // 检查主要标题
    const mainHeading = page.locator('h1, h2').first();
    await expect(mainHeading).toBeVisible();
    
    // 截图记录
    await page.screenshot({ path: 'homepage-loaded.png' });
  });

  test('导航链接有效性测试', async ({ page }) => {
    // 收集所有导航链接
    const navLinks = page.locator('nav a, header a');
    const linkCount = await navLinks.count();
    
    console.log(`找到 ${linkCount} 个导航链接`);
    
    // 测试前5个链接（避免测试过多）
    for (let i = 0; i < Math.min(linkCount, 5); i++) {
      const link = navLinks.nth(i);
      const href = await link.getAttribute('href');
      
      if (href && !href.startsWith('#') && !href.startsWith('javascript:')) {
        console.log(`测试链接: ${href}`);
        
        // 点击链接
        await link.click();
        await page.waitForLoadState('networkidle');
        
        // 检查页面加载成功
        await expect(page.locator('body')).toBeVisible();
        
        // 返回主页继续测试其他链接
        await page.goto('https://www.playturbo.com/');
        await page.waitForLoadState('networkidle');
      }
    }
  });

  test('搜索功能测试（如果存在）', async ({ page }) => {
    // 查找搜索框
    const searchInput = page.locator('input[type="search"], input[placeholder*="搜索"], .search-input');
    const searchButton = page.locator('button[type="submit"], .search-button');
    
    const searchInputCount = await searchInput.count();
    const searchButtonCount = await searchButton.count();
    
    if (searchInputCount > 0 && searchButtonCount > 0) {
      // 测试搜索功能
      await searchInput.first().fill('test');
      await searchButton.first().click();
      
      // 等待搜索结果
      await page.waitForTimeout(2000);
      
      // 检查是否有搜索结果或搜索页面
      await expect(page.locator('body')).toBeVisible();
      
      // 截图记录
      await page.screenshot({ path: 'search-test.png' });
    } else {
      console.log('未找到搜索功能，跳过此测试');
      test.skip();
    }
  });

  test('响应式设计测试', async ({ page }) => {
    // 测试不同屏幕尺寸
    const viewports = [
      { width: 1920, height: 1080, name: 'desktop' },
      { width: 768, height: 1024, name: 'tablet' },
      { width: 375, height: 667, name: 'mobile' }
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      
      // 检查页面在特定尺寸下的显示
      await expect(page.locator('body')).toBeVisible();
      
      // 截图记录不同尺寸
      await page.screenshot({ 
        path: `responsive-${viewport.name}.png`,
        fullPage: true 
      });
      
      console.log(`已测试 ${viewport.name} 视图 (${viewport.width}x${viewport.height})`);
    }
    
    // 恢复默认视图
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('表单交互测试（如果存在）', async ({ page }) => {
    // 查找表单元素
    const forms = page.locator('form');
    const formCount = await forms.count();
    
    if (formCount > 0) {
      console.log(`找到 ${formCount} 个表单`);
      
      // 测试第一个表单
      const firstForm = forms.first();
      
      // 查找表单内的输入字段
      const inputs = firstForm.locator('input, textarea, select');
      const inputCount = await inputs.count();
      
      console.log(`表单包含 ${inputCount} 个输入字段`);
      
      // 测试表单提交（如果有提交按钮）
      const submitButton = firstForm.locator('button[type="submit"], input[type="submit"]');
      const submitCount = await submitButton.count();
      
      if (submitCount > 0) {
        // 填写表单字段（如果有文本输入）
        const textInputs = firstForm.locator('input[type="text"], input[type="email"], textarea');
        const textInputCount = await textInputs.count();
        
        if (textInputCount > 0) {
          // 填写第一个文本输入
          await textInputs.first().fill('test@example.com');
        }
        
        // 尝试提交表单
        await submitButton.first().click();
        await page.waitForTimeout(3000);
        
        // 检查提交后的状态
        await expect(page.locator('body')).toBeVisible();
        
        // 截图记录
        await page.screenshot({ path: 'form-submission.png' });
      }
    } else {
      console.log('未找到表单，跳过此测试');
      test.skip();
    }
  });

  test('页面性能测试', async ({ page }) => {
    // 测量页面加载时间
    const startTime = Date.now();
    await page.goto('https://www.playturbo.com/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    console.log(`页面加载时间: ${loadTime}ms`);
    
    // 检查页面性能指标
    const performanceTiming = await page.evaluate(() => JSON.stringify(window.performance.timing));
    console.log('性能时间线:', performanceTiming);
    
    // 检查资源加载
    const resources = await page.evaluate(() => 
      JSON.stringify(performance.getEntriesByType('resource'))
    );
    console.log(`加载的资源数量: ${JSON.parse(resources).length}`);
    
    // 断言页面加载时间在合理范围内（10秒内）
    expect(loadTime).toBeLessThan(10000);
  });

  test('浏览器兼容性检查', async ({ page }) => {
    // 检查现代Web API支持
    const webAPIs = await page.evaluate(() => ({
      fetch: typeof fetch !== 'undefined',
      localStorage: typeof localStorage !== 'undefined',
      sessionStorage: typeof sessionStorage !== 'undefined',
      geolocation: typeof navigator.geolocation !== 'undefined',
      serviceWorker: typeof navigator.serviceWorker !== 'undefined'
    }));
    
    console.log('Web API支持情况:', webAPIs);
    
    // 检查JavaScript错误
    page.on('pageerror', error => {
      console.error('页面JavaScript错误:', error.message);
    });
    
    // 检查控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error('控制台错误:', msg.text());
      }
    });
    
    // 重新加载页面以捕获可能的错误
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // 截图记录
    await page.screenshot({ path: 'browser-compatibility.png' });
  });
});

test.describe('端到端用户流程测试', () => {
  test('完整用户旅程测试', async ({ page }) => {
    // 步骤1: 访问主页
    await page.goto('https://www.playturbo.com/');
    await page.waitForLoadState('networkidle');
    
    // 步骤2: 浏览主要页面
    const mainPages = ['/', '/pricing', '/docs', '/blog', '/contact'];
    
    for (const pagePath of mainPages) {
      try {
        await page.goto(`https://www.playturbo.com${pagePath}`);
        await page.waitForLoadState('networkidle');
        
        // 检查页面基本元素
        await expect(page.locator('body')).toBeVisible();
        
        console.log(`成功访问页面: ${pagePath}`);
        
        // 返回主页继续测试
        await page.goto('https://www.playturbo.com/');
        await page.waitForLoadState('networkidle');
      } catch (error) {
        console.log(`页面 ${pagePath} 可能不存在或无法访问`);
      }
    }
    
    // 步骤3: 测试交互元素
    const buttons = page.locator('button:not([disabled])');
    const buttonCount = await buttons.count();
    
    console.log(`找到 ${buttonCount} 个可用按钮`);
    
    // 点击第一个非链接按钮（如果有）
    if (buttonCount > 0) {
      const firstButton = buttons.first();
      await firstButton.click();
      await page.waitForTimeout(2000);
      
      // 检查点击后的状态
      await expect(page.locator('body')).toBeVisible();
    }
    
    // 步骤4: 验证页面完整性
    const images = page.locator('img');
    const imageCount = await images.count();
    
    console.log(`页面包含 ${imageCount} 张图片`);
    
    // 检查图片加载
    for (let i = 0; i < Math.min(imageCount, 3); i++) {
      const img = images.nth(i);
      await expect(img).toBeVisible();
    }
    
    // 最终截图
    await page.screenshot({ path: 'e2e-user-journey.png', fullPage: true });
  });
});