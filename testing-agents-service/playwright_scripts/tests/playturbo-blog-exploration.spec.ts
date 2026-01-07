import { test, expect, Page } from '@playwright/test';

test.describe('PlayTurbo网站博客页面探索', () => {
  let page: Page;

  test.beforeAll(async ({ browser }) => {
    page = await browser.newPage();
    await page.goto('https://www.playturbo.com/');
  });

  test.afterAll(async () => {
    await page.close();
  });

  test('访问网站主页并检查基本元素', async () => {
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    // 检查页面标题
    const title = await page.title();
    console.log('页面标题:', title);
    
    // 检查页面URL
    const url = page.url();
    console.log('当前URL:', url);
    
    // 截图保存主页
    await page.screenshot({ path: 'playturbo-homepage.png', fullPage: true });
    
    // 检查是否有导航菜单
    const navMenu = page.locator('nav, header, .navbar, .menu, [role="navigation"]').first();
    if (await navMenu.count() > 0) {
      console.log('找到导航菜单');
      await navMenu.screenshot({ path: 'playturbo-nav.png' });
    }
  });

  test('查找博客相关链接', async () => {
    // 查找所有包含博客关键词的链接
    const blogKeywords = ['blog', '博客', '文章', 'post', 'news', '新闻'];
    
    console.log('\n=== 查找博客相关链接 ===');
    
    // 方法1：查找文本包含博客关键词的链接
    for (const keyword of blogKeywords) {
      const blogLinks = page.locator(`a:has-text("${keyword}")`);
      const count = await blogLinks.count();
      
      if (count > 0) {
        console.log(`找到 ${count} 个包含"${keyword}"的链接:`);
        
        for (let i = 0; i < Math.min(count, 5); i++) {
          const link = blogLinks.nth(i);
          const text = await link.textContent();
          const href = await link.getAttribute('href');
          console.log(`  ${i+1}. 文本: "${text?.trim()}" - 链接: ${href}`);
          
          // 点击第一个找到的博客链接
          if (i === 0) {
            console.log(`点击链接: ${text}`);
            await link.click();
            await page.waitForLoadState('networkidle');
            
            // 检查新页面
            const newUrl = page.url();
            console.log('博客页面URL:', newUrl);
            
            // 截图博客页面
            await page.screenshot({ path: 'playturbo-blog-page.png', fullPage: true });
            
            // 返回主页继续搜索
            await page.goBack();
            await page.waitForLoadState('networkidle');
          }
        }
      }
    }
    
    // 方法2：查找href包含博客关键词的链接
    console.log('\n=== 查找href包含博客关键词的链接 ===');
    const allLinks = page.locator('a[href]');
    const totalLinks = await allLinks.count();
    console.log(`页面总链接数: ${totalLinks}`);
    
    const blogLinkPatterns = ['/blog', '/posts', '/articles', '/news'];
    
    for (let i = 0; i < Math.min(totalLinks, 50); i++) {
      const link = allLinks.nth(i);
      const href = await link.getAttribute('href');
      
      if (href) {
        for (const pattern of blogLinkPatterns) {
          if (href.toLowerCase().includes(pattern)) {
            const text = await link.textContent();
            console.log(`找到博客链接: "${text?.trim()}" - ${href}`);
            
            // 点击访问
            console.log(`访问博客链接: ${href}`);
            await link.click();
            await page.waitForLoadState('networkidle');
            
            const blogUrl = page.url();
            console.log('博客页面URL:', blogUrl);
            
            // 截图
            await page.screenshot({ path: 'playturbo-blog-detail.png', fullPage: true });
            
            return; // 找到博客页面，停止搜索
          }
        }
      }
    }
    
    console.log('未找到明显的博客链接，尝试搜索功能...');
  });

  test('探索博客页面结构', async ({ page: testPage }) => {
    // 直接尝试访问可能的博客URL
    const possibleBlogUrls = [
      'https://www.playturbo.com/blog',
      'https://www.playturbo.com/blogs',
      'https://www.playturbo.com/posts',
      'https://www.playturbo.com/articles',
      'https://blog.playturbo.com',
      'https://www.playturbo.com/news'
    ];
    
    console.log('\n=== 尝试直接访问可能的博客URL ===');
    
    for (const blogUrl of possibleBlogUrls) {
      try {
        console.log(`尝试访问: ${blogUrl}`);
        await testPage.goto(blogUrl, { timeout: 10000 });
        
        const currentUrl = testPage.url();
        const status = testPage.url();
        
        if (currentUrl.includes('blog') || currentUrl.includes('post') || 
            currentUrl.includes('article') || currentUrl.includes('news')) {
          console.log(`成功访问博客页面: ${currentUrl}`);
          
          // 截图
          await testPage.screenshot({ path: 'playturbo-blog-direct.png', fullPage: true });
          
          // 分析页面结构
          await analyzeBlogStructure(testPage);
          return;
        }
      } catch (error) {
        console.log(`无法访问 ${blogUrl}: ${error.message}`);
      }
    }
    
    console.log('无法直接访问博客页面，尝试在主页搜索');
    
    // 返回主页尝试搜索
    await testPage.goto('https://www.playturbo.com/');
    
    // 查找搜索框
    const searchInput = testPage.locator('input[type="search"], input[name="search"], .search-input, [placeholder*="search"], [placeholder*="搜索"]');
    
    if (await searchInput.count() > 0) {
      console.log('找到搜索框，尝试搜索"blog"');
      await searchInput.first().fill('blog');
      await searchInput.first().press('Enter');
      await testPage.waitForLoadState('networkidle');
      
      const searchUrl = testPage.url();
      console.log('搜索结果页面:', searchUrl);
      await testPage.screenshot({ path: 'playturbo-search-results.png', fullPage: true });
    }
  });

  async function analyzeBlogStructure(page: Page) {
    console.log('\n=== 分析博客页面结构 ===');
    
    // 1. 检查页面标题和描述
    const title = await page.title();
    const metaDescription = await page.locator('meta[name="description"]').getAttribute('content');
    console.log('博客页面标题:', title);
    console.log('页面描述:', metaDescription || '未找到');
    
    // 2. 检查主要结构元素
    console.log('\n=== 主要结构元素 ===');
    
    // 文章列表容器
    const articleContainers = [
      page.locator('.articles, .posts, .blog-posts, .post-list, .article-list'),
      page.locator('[class*="article"]'),
      page.locator('[class*="post"]'),
      page.locator('article'),
      page.locator('.content, .main-content')
    ];
    
    for (const container of articleContainers) {
      if (await container.count() > 0) {
        console.log(`找到文章容器: ${await container.first().getAttribute('class')}`);
        break;
      }
    }
    
    // 3. 查找文章项
    const articleItems = page.locator('article, .post, .article, .blog-post, [class*="post-"], [class*="article-"]');
    const articleCount = await articleItems.count();
    console.log(`找到 ${articleCount} 篇文章`);
    
    if (articleCount > 0) {
      // 分析第一篇文章
      const firstArticle = articleItems.first();
      
      // 文章标题
      const articleTitle = firstArticle.locator('h1, h2, h3, .title, .post-title, .article-title');
      if (await articleTitle.count() > 0) {
        const titleText = await articleTitle.first().textContent();
        console.log('文章标题:', titleText?.trim());
      }
      
      // 文章元信息（日期、作者、分类）
      const metaInfo = firstArticle.locator('.date, .post-date, .article-date, .author, .category, .tags, time');
      const metaCount = await metaInfo.count();
      console.log(`文章元信息元素: ${metaCount} 个`);
      
      for (let i = 0; i < Math.min(metaCount, 5); i++) {
        const meta = metaInfo.nth(i);
        const text = await meta.textContent();
        console.log(`  元信息 ${i+1}: ${text?.trim()}`);
      }
      
      // 文章摘要/内容
      const excerpt = firstArticle.locator('.excerpt, .summary, .content, p').first();
      if (await excerpt.count() > 0) {
        const excerptText = await excerpt.textContent();
        console.log('文章摘要:', excerptText?.substring(0, 100) + '...');
      }
      
      // 阅读更多链接
      const readMore = firstArticle.locator('a:has-text("Read"), a:has-text("阅读"), a:has-text("More"), a:has-text("更多")');
      if (await readMore.count() > 0) {
        const readMoreHref = await readMore.first().getAttribute('href');
        console.log('阅读更多链接:', readMoreHref);
      }
    }
    
    // 4. 检查侧边栏
    console.log('\n=== 侧边栏检查 ===');
    const sidebars = page.locator('.sidebar, aside, .widget-area, [class*="sidebar"]');
    const sidebarCount = await sidebars.count();
    console.log(`找到 ${sidebarCount} 个侧边栏`);
    
    if (sidebarCount > 0) {
      const sidebar = sidebars.first();
      
      // 检查侧边栏内容
      const sidebarWidgets = sidebar.locator('.widget, .sidebar-widget, section, div');
      const widgetCount = await sidebarWidgets.count();
      console.log(`侧边栏组件数量: ${widgetCount}`);
      
      // 检查常见侧边栏功能
      const commonWidgets = [
        { name: '搜索', selector: 'input[type="search"], .search-form' },
        { name: '分类', selector: '.categories, .category-list, [class*="categor"]' },
        { name: '标签云', selector: '.tags, .tag-cloud, [class*="tag"]' },
        { name: '最新文章', selector: '.recent-posts, [class*="recent"]' },
        { name: '归档', selector: '.archive, [class*="archive"]' },
        { name: '关于', selector: '.about, [class*="about"]' }
      ];
      
      for (const widget of commonWidgets) {
        const element = sidebar.locator(widget.selector);
        if (await element.count() > 0) {
          console.log(`找到${widget.name}组件`);
        }
      }
    }
    
    // 5. 检查分页
    console.log('\n=== 分页检查 ===');
    const pagination = page.locator('.pagination, .page-numbers, .pager, [class*="pagination"], nav:has(a[rel="prev"]), nav:has(a[rel="next"])');
    if (await pagination.count() > 0) {
      console.log('找到分页组件');
      
      // 分页链接
      const pageLinks = pagination.locator('a');
      const pageLinkCount = await pageLinks.count();
      console.log(`分页链接数量: ${pageLinkCount}`);
      
      // 上一页/下一页
      const prevLink = pagination.locator('a[rel="prev"], :has-text("Previous"), :has-text("上一页")');
      const nextLink = pagination.locator('a[rel="next"], :has-text("Next"), :has-text("下一页")');
      
      if (await prevLink.count() > 0) console.log('有"上一页"链接');
      if (await nextLink.count() > 0) console.log('有"下一页"链接');
    }
    
    // 6. 检查搜索功能
    console.log('\n=== 搜索功能检查 ===');
    const searchForms = page.locator('form[role="search"], form:has(input[type="search"])');
    if (await searchForms.count() > 0) {
      console.log('找到搜索表单');
      
      const searchInput = searchForms.locator('input[type="search"], input[name="s"]');
      const searchButton = searchForms.locator('button[type="submit"], input[type="submit"]');
      
      if (await searchInput.count() > 0) {
        const placeholder = await searchInput.first().getAttribute('placeholder');
        console.log(`搜索框placeholder: ${placeholder || '无'}`);
      }
      
      if (await searchButton.count() > 0) {
        const buttonText = await searchButton.first().textContent();
        console.log(`搜索按钮文本: ${buttonText?.trim() || '无文本'}`);
      }
    }
    
    // 7. 检查评论功能
    console.log('\n=== 评论功能检查 ===');
    const commentSections = page.locator('#comments, .comments, [class*="comment"]');
    if (await commentSections.count() > 0) {
      console.log('找到评论区域');
      
      // 评论表单
      const commentForm = page.locator('#commentform, form[class*="comment"]');
      if (await commentForm.count() > 0) {
        console.log('有评论表单');
        
        // 检查表单字段
        const formFields = ['name', 'email', 'website', 'comment'];
        for (const field of formFields) {
          const fieldElement = commentForm.locator(`[name="${field}"], #${field}`);
          if (await fieldElement.count() > 0) {
            console.log(`  有${field}字段`);
          }
        }
      }
    }
    
    // 8. 收集页面元素选择器
    console.log('\n=== 页面元素选择器 ===');
    collectSelectors(page);
  }

  async function collectSelectors(page: Page) {
    const selectors = {
      // 导航
      navigation: await findNavigationSelectors(page),
      
      // 文章相关
      articleContainer: await findSelector(page, '.articles, .posts, .blog-posts, article'),
      articleItem: await findSelector(page, 'article, .post, .blog-post'),
      articleTitle: await findSelector(page, 'h1, h2, .post-title, .article-title'),
      articleDate: await findSelector(page, '.date, .post-date, time'),
      articleAuthor: await findSelector(page, '.author, .post-author'),
      articleCategory: await findSelector(page, '.category, .categories, .post-category'),
      articleExcerpt: await findSelector(page, '.excerpt, .summary, .entry-content p'),
      readMoreLink: await findSelector(page, 'a:has-text("Read"), a:has-text("阅读"), a:has-text("More")'),
      
      // 侧边栏
      sidebar: await findSelector(page, '.sidebar, aside'),
      searchWidget: await findSelector(page, '.search-form, form[role="search"]'),
      categoriesWidget: await findSelector(page, '.categories, .widget_categories'),
      recentPostsWidget: await findSelector(page, '.recent-posts, .widget_recent_entries'),
      
      // 分页
      pagination: await findSelector(page, '.pagination, .page-numbers'),
      prevPage: await findSelector(page, 'a[rel="prev"], .prev, :has-text("Previous")'),
      nextPage: await findSelector(page, 'a[rel="next"], .next, :has-text("Next")'),
      
      // 搜索
      searchInput: await findSelector(page, 'input[type="search"], input[name="s"]'),
      searchButton: await findSelector(page, 'button[type="submit"], input[type="submit"]'),
      
      // 评论
      commentSection: await findSelector(page, '#comments, .comments'),
      commentForm: await findSelector(page, '#commentform, form[class*="comment"]'),
      commentInput: await findSelector(page, 'textarea[name="comment"], #comment'),
      submitComment: await findSelector(page, '#submit, [name="submit"]')
    };
    
    console.log('收集到的选择器:');
    for (const [key, value] of Object.entries(selectors)) {
      if (value) {
        console.log(`  ${key}: ${value}`);
      }
    }
  }

  async function findNavigationSelectors(page: Page): Promise<string> {
    const navSelectors = [
      'nav',
      'header nav',
      '.navbar',
      '.main-nav',
      '[role="navigation"]',
      'ul.menu',
      '.site-navigation'
    ];
    
    for (const selector of navSelectors) {
      if (await page.locator(selector).count() > 0) {
        return selector;
      }
    }
    return '';
  }

  async function findSelector(page: Page, selectors: string): Promise<string> {
    const selectorList = selectors.split(', ');
    for (const selector of selectorList) {
      if (await page.locator(selector).count() > 0) {
        return selector;
      }
    }
    return '';
  }
});