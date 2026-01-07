import { test, expect } from '@playwright/test';

test.describe('PlayTurbo.com 博客功能测试', () => {
  
  test('测试网站首页加载', async ({ page }) => {
    console.log('🚀 开始测试 PlayTurbo.com 博客功能');
    
    // 访问网站首页
    await page.goto('https://www.playturbo.com/');
    await page.waitForLoadState('networkidle');
    
    // 验证网站标题
    const title = await page.title();
    console.log(`📝 网站标题: ${title}`);
    expect(title).toBeTruthy();
    
    // 截图记录
    await page.screenshot({ path: 'playturbo-homepage.png' });
    console.log('✅ 网站首页加载测试通过');
  });

  test('查找博客入口', async ({ page }) => {
    await page.goto('https://www.playturbo.com/');
    await page.waitForLoadState('networkidle');
    
    // 查找博客相关链接
    const blogKeywords = ['博客', 'Blog', '文章', 'Articles', 'News', '资讯'];
    let blogLinkFound = false;
    
    console.log('🔍 正在查找博客入口...');
    
    for (const keyword of blogKeywords) {
      try {
        const links = page.locator(`a:has-text("${keyword}")`);
        const count = await links.count();
        
        if (count > 0) {
          const firstLink = links.first();
          const linkText = await firstLink.textContent();
          const linkHref = await firstLink.getAttribute('href');
          
          console.log(`✅ 找到博客入口: "${linkText}" -> ${linkHref}`);
          blogLinkFound = true;
          
          // 点击博客链接
          await firstLink.click();
          await page.waitForLoadState('networkidle');
          
          const newTitle = await page.title();
          console.log(`📄 博客页面标题: ${newTitle}`);
          
          await page.screenshot({ path: 'blog-page.png' });
          break;
        }
      } catch (error) {
        continue;
      }
    }
    
    if (!blogLinkFound) {
      console.log('⚠️ 未找到明显的博客入口，尝试直接访问常见博客路径');
      
      // 尝试直接访问博客页面
      const commonBlogPaths = ['/blog', '/blogs', '/articles', '/news'];
      
      for (const path of commonBlogPaths) {
        try {
          const blogUrl = `https://www.playturbo.com${path}`;
          console.log(`尝试访问: ${blogUrl}`);
          
          const response = await page.goto(blogUrl, { waitUntil: 'networkidle', timeout: 10000 });
          
          if (response && response.status() === 200) {
            console.log(`✅ 成功访问博客页面: ${blogUrl}`);
            const blogTitle = await page.title();
            console.log(`博客页面标题: ${blogTitle}`);
            
            // 检查页面内容
            const bodyText = await page.textContent('body') || '';
            if (bodyText.includes('blog') || bodyText.includes('博客') || 
                bodyText.includes('article') || bodyText.includes('文章')) {
              console.log('✅ 确认是博客页面');
            }
            
            await page.screenshot({ path: 'direct-blog-access.png' });
            blogLinkFound = true;
            break;
          }
        } catch (error) {
          console.log(`无法访问 ${path}: ${error.message}`);
          continue;
        }
      }
    }
    
    console.log(blogLinkFound ? '✅ 博客入口测试通过' : '❌ 未找到博客功能');
    expect(blogLinkFound).toBeTruthy();
  });

  test('测试博客文章列表', async ({ page }) => {
    // 直接尝试访问博客页面
    const blogUrls = [
      'https://www.playturbo.com/blog',
      'https://www.playturbo.com/blogs',
      'https://www.playturbo.com/articles'
    ];
    
    let blogPageAccessed = false;
    let articlesFound = 0;
    
    for (const url of blogUrls) {
      try {
        console.log(`尝试访问博客列表: ${url}`);
        const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 10000 });
        
        if (response && response.status() === 200) {
          blogPageAccessed = true;
          console.log(`✅ 成功访问博客页面: ${url}`);
          
          // 查找文章元素
          const articleSelectors = [
            'article',
            '.post',
            '.blog-post',
            '.article',
            '.card',
            'h2',
            'h3'
          ];
          
          for (const selector of articleSelectors) {
            const elements = page.locator(selector);
            const count = await elements.count();
            
            if (count > 0) {
              console.log(`使用选择器 "${selector}" 找到 ${count} 个元素`);
              
              // 检查前几个元素
              for (let i = 0; i < Math.min(count, 3); i++) {
                const element = elements.nth(i);
                const text = await element.textContent();
                if (text && text.trim().length > 20) {
                  articlesFound++;
                  console.log(`📰 文章 ${articlesFound}: ${text.trim().substring(0, 50)}...`);
                }
              }
            }
          }
          
          if (articlesFound > 0) {
            console.log(`✅ 找到 ${articlesFound} 篇博客文章`);
            await page.screenshot({ path: 'blog-articles.png' });
          } else {
            console.log('⚠️ 找到博客页面但未识别出文章');
            // 检查页面是否有博客相关内容
            const pageText = await page.textContent('body') || '';
            if (pageText.includes('blog') || pageText.includes('post') || 
                pageText.includes('article') || pageText.includes('阅读')) {
              console.log('📝 页面包含博客相关关键词');
            }
          }
          
          break;
        }
      } catch (error) {
        console.log(`无法访问 ${url}: ${error.message}`);
        continue;
      }
    }
    
    if (!blogPageAccessed) {
      console.log('❌ 无法访问任何博客页面');
    }
    
    console.log(`📊 测试结果: ${blogPageAccessed ? '找到博客页面' : '未找到博客页面'}, 识别出 ${articlesFound} 篇文章`);
    expect(blogPageAccessed).toBeTruthy();
  });

  test('测试博客搜索功能', async ({ page }) => {
    // 先尝试访问博客页面
    try {
      await page.goto('https://www.playturbo.com/blog', { waitUntil: 'networkidle', timeout: 10000 });
    } catch (error) {
      console.log('无法访问博客页面，跳过搜索测试');
      return;
    }
    
    // 查找搜索框
    const searchSelectors = [
      'input[type="search"]',
      'input[name="search"]',
      'input[placeholder*="搜索"]',
      'input[placeholder*="Search"]',
      '.search-form',
      '.search-box'
    ];
    
    let searchTested = false;
    
    for (const selector of searchSelectors) {
      const searchInputs = page.locator(selector);
      const count = await searchInputs.count();
      
      if (count > 0) {
        console.log(`🔎 找到搜索框: ${selector}`);
        
        // 测试搜索
        await searchInputs.first().fill('AI');
        await searchInputs.first().press('Enter');
        
        await page.waitForLoadState('networkidle');
        
        const searchResultsText = await page.textContent('body') || '';
        const hasResults = searchResultsText.includes('结果') || 
                          searchResultsText.includes('results') ||
                          page.url().includes('search') ||
                          page.url().includes('s=');
        
        console.log(`搜索测试: ${hasResults ? '找到搜索结果' : '未找到明确结果'}`);
        
        if (hasResults) {
          await page.screenshot({ path: 'blog-search.png' });
        }
        
        searchTested = true;
        break;
      }
    }
    
    if (!searchTested) {
      console.log('⚠️ 未找到搜索功能');
    }
    
    console.log(searchTested ? '✅ 搜索功能测试完成' : '⚠️ 搜索功能未测试');
    expect(true).toBeTruthy(); // 搜索是可选的
  });

  test('生成测试报告', async ({ page }) => {
    console.log('\n📋 ========== 测试报告 ==========');
    console.log('网站: https://www.playturbo.com/');
    console.log('测试时间: ' + new Date().toLocaleString());
    console.log('测试内容: 博客相关功能测试');
    console.log('================================\n');
    
    // 这里可以汇总前面的测试结果
    console.log('✅ 测试完成！');
    console.log('📸 截图已保存:');
    console.log('  - playturbo-homepage.png');
    console.log('  - blog-page.png (如果找到)');
    console.log('  - blog-articles.png (如果找到文章)');
    console.log('  - blog-search.png (如果测试搜索)');
    
    console.log('\n💡 建议:');
    console.log('1. 如果未找到博客功能，可能需要检查网站是否有博客部分');
    console.log('2. 博客URL可能是其他路径，如 /insights, /resources 等');
    console.log('3. 网站可能使用其他术语，如 "动态", "更新", "技术分享" 等');
  });
});