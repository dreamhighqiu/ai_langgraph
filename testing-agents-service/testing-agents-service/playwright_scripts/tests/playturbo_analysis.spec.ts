import { test, expect } from '@playwright/test';

test.describe('PlayTurbo网站功能分析', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://www.playturbo.com/');
    await page.waitForLoadState('networkidle');
  });

  test('访问主页并检查基本元素', async ({ page }) => {
    // 检查页面标题
    await expect(page).toHaveTitle(/PlayTurbo/);
    
    // 检查导航栏
    const navBar = page.locator('nav, header, .navbar, .header');
    await expect(navBar).toBeVisible();
    
    // 检查主要部分
    const heroSection = page.locator('.hero, .banner, .jumbotron, section:first-of-type');
    await expect(heroSection).toBeVisible();
    
    // 检查页脚
    const footer = page.locator('footer, .footer');
    await expect(footer).toBeVisible();
    
    // 截图保存页面状态
    await page.screenshot({ path: 'homepage.png', fullPage: true });
  });

  test('识别所有可交互元素', async ({ page }) => {
    // 查找所有按钮
    const buttons = page.locator('button, [role="button"], .btn, input[type="button"], input[type="submit"]');
    const buttonCount = await buttons.count();
    console.log(`找到 ${buttonCount} 个按钮元素`);
    
    // 查找所有链接
    const links = page.locator('a[href]');
    const linkCount = await links.count();
    console.log(`找到 ${linkCount} 个链接元素`);
    
    // 查找所有表单元素
    const formElements = page.locator('input, textarea, select, form');
    const formElementCount = await formElements.count();
    console.log(`找到 ${formElementCount} 个表单元素`);
    
    // 记录所有链接的URL
    for (let i = 0; i < Math.min(linkCount, 20); i++) {
      const link = links.nth(i);
      const href = await link.getAttribute('href');
      const text = await link.textContent();
      console.log(`链接 ${i+1}: "${text?.trim() || '无文本'}" -> ${href}`);
    }
  });

  test('浏览所有导航链接', async ({ page }) => {
    // 获取所有导航链接
    const navLinks = page.locator('nav a, .nav a, .navbar a, .menu a');
    const navLinkCount = await navLinks.count();
    
    console.log(`找到 ${navLinkCount} 个导航链接`);
    
    // 点击每个导航链接并检查页面
    for (let i = 0; i < Math.min(navLinkCount, 10); i++) {
      const link = navLinks.nth(i);
      const href = await link.getAttribute('href');
      const text = await link.textContent();
      
      if (href && !href.startsWith('#') && !href.includes('javascript:')) {
        console.log(`点击导航链接: "${text?.trim() || '无文本'}" -> ${href}`);
        
        try {
          await link.click();
          await page.waitForLoadState('networkidle');
          await page.waitForTimeout(1000);
          
          // 检查新页面
          const currentUrl = page.url();
          console.log(`  当前URL: ${currentUrl}`);
          
          // 截图
          await page.screenshot({ path: `page_${i}.png` });
          
          // 返回主页
          await page.goto('https://www.playturbo.com/');
          await page.waitForLoadState('networkidle');
        } catch (error) {
          console.log(`  无法访问链接: ${error}`);
        }
      }
    }
  });

  test('分析功能模块', async ({ page }) => {
    // 查找主要功能模块
    const sections = page.locator('section, .section, .feature, .module, .card');
    const sectionCount = await sections.count();
    
    console.log(`找到 ${sectionCount} 个主要模块/区域`);
    
    // 分析每个模块
    for (let i = 0; i < Math.min(sectionCount, 10); i++) {
      const section = sections.nth(i);
      const sectionText = await section.textContent();
      const sectionClass = await section.getAttribute('class');
      
      console.log(`模块 ${i+1}:`);
      console.log(`  类名: ${sectionClass}`);
      console.log(`  内容预览: ${sectionText?.substring(0, 100).replace(/\n/g, ' ')}...`);
      
      // 检查模块内是否有交互元素
      const interactiveInSection = section.locator('button, a, input');
      const interactiveCount = await interactiveInSection.count();
      console.log(`  交互元素数量: ${interactiveCount}`);
    }
  });

  test('查找测试相关功能', async ({ page }) => {
    // 搜索测试、演示、试用相关关键词
    const testKeywords = ['test', 'demo', 'trial', 'try', 'play', 'sandbox', '示例', '演示', '试用'];
    
    for (const keyword of testKeywords) {
      const elements = page.locator(`:text("${keyword}"):visible, [href*="${keyword}"]:visible`);
      const count = await elements.count();
      
      if (count > 0) {
        console.log(`找到 ${count} 个包含"${keyword}"的元素`);
        
        for (let i = 0; i < Math.min(count, 5); i++) {
          const element = elements.nth(i);
          const text = await element.textContent();
          const href = await element.getAttribute('href');
          console.log(`  - "${text?.trim()}" ${href ? `-> ${href}` : ''}`);
        }
      }
    }
  });

  test('收集页面结构和选择器信息', async ({ page }) => {
    // 获取页面HTML结构信息
    const pageStructure = {
      title: await page.title(),
      url: page.url(),
      headings: {},
      forms: [],
      interactiveElements: []
    };
    
    // 收集标题
    for (let i = 1; i <= 6; i++) {
      const hElements = page.locator(`h${i}`);
      const count = await hElements.count();
      pageStructure.headings[`h${i}`] = count;
    }
    
    console.log('页面结构分析:');
    console.log(`标题: ${pageStructure.title}`);
    console.log(`URL: ${pageStructure.url}`);
    console.log('标题统计:', pageStructure.headings);
    
    // 收集表单信息
    const forms = page.locator('form');
    const formCount = await forms.count();
    console.log(`表单数量: ${formCount}`);
    
    for (let i = 0; i < formCount; i++) {
      const form = forms.nth(i);
      const formId = await form.getAttribute('id');
      const formClass = await form.getAttribute('class');
      const formAction = await form.getAttribute('action');
      
      console.log(`表单 ${i+1}: id="${formId}" class="${formClass}" action="${formAction}"`);
    }
  });
});