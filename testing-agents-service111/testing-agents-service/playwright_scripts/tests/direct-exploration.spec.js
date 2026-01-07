// 直接探索脚本
const { chromium } = require('playwright');

(async () => {
  console.log('=== PlayTurbo网站博客探索 ===\n');
  
  const browser = await chromium.launch({ 
    headless: true,  // 使用无头模式
    timeout: 60000
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  
  const page = await context.newPage();
  
  try {
    // 1. 访问主页
    console.log('1. 访问主页...');
    await page.goto('https://www.playturbo.com/', { 
      waitUntil: 'domcontentloaded',
      timeout: 30000 
    });
    
    const homepageInfo = {
      url: page.url(),
      title: await page.title(),
      status: '成功'
    };
    
    console.log(`   主页URL: ${homepageInfo.url}`);
    console.log(`   页面标题: ${homepageInfo.title}`);
    
    // 2. 搜索博客内容
    console.log('\n2. 搜索博客内容...');
    
    // 获取页面内容
    const content = await page.content();
    
    // 检查是否有博客相关内容
    const hasBlogContent = content.toLowerCase().includes('blog') || 
                          content.includes('博客') ||
                          content.toLowerCase().includes('article') ||
                          content.toLowerCase().includes('post');
    
    console.log(`   页面是否包含博客内容: ${hasBlogContent ? '是' : '否'}`);
    
    // 3. 查找博客链接
    console.log('\n3. 查找博客链接...');
    
    const blogLinks = await page.evaluate(() => {
      const links = [];
      const allLinks = document.querySelectorAll('a[href]');
      
      const blogKeywords = ['blog', '博客', '文章', 'post', 'news', '新闻'];
      
      allLinks.forEach(link => {
        const text = link.textContent?.toLowerCase() || '';
        const href = link.href?.toLowerCase() || '';
        
        const isBlogLink = blogKeywords.some(keyword => 
          text.includes(keyword) || href.includes(keyword)
        );
        
        if (isBlogLink && link.offsetParent !== null) { // 只取可见链接
          links.push({
            text: link.textContent?.trim().substring(0, 50),
            href: link.href,
            visible: true
          });
        }
      });
      
      return links.slice(0, 10); // 只取前10个
    });
    
    console.log(`   找到 ${blogLinks.length} 个可能的博客链接:`);
    blogLinks.forEach((link, i) => {
      console.log(`   ${i+1}. ${link.text} -> ${link.href}`);
    });
    
    // 4. 尝试访问博客页面
    console.log('\n4. 尝试访问博客页面...');
    
    let blogUrl = null;
    let blogTitle = null;
    
    if (blogLinks.length > 0) {
      const firstLink = blogLinks[0];
      console.log(`   尝试访问: ${firstLink.href}`);
      
      try {
        await page.goto(firstLink.href, { waitUntil: 'domcontentloaded', timeout: 15000 });
        blogUrl = page.url();
        blogTitle = await page.title();
        
        console.log(`   访问成功: ${blogUrl}`);
        console.log(`   页面标题: ${blogTitle}`);
      } catch (error) {
        console.log(`   访问失败: ${error.message}`);
      }
    }
    
    // 如果没找到链接，尝试常见URL
    if (!blogUrl) {
      console.log('   尝试常见博客URL...');
      
      const commonUrls = [
        'https://www.playturbo.com/blog',
        'https://blog.playturbo.com',
        'https://www.playturbo.com/blogs',
        'https://www.playturbo.com/posts'
      ];
      
      for (const url of commonUrls) {
        try {
          console.log(`   尝试: ${url}`);
          await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });
          
          if (page.url() !== homepageInfo.url) {
            blogUrl = page.url();
            blogTitle = await page.title();
            console.log(`   成功: ${blogUrl}`);
            break;
          }
        } catch (error) {
          console.log(`   失败: ${error.message}`);
        }
      }
    }
    
    // 5. 分析页面结构
    console.log('\n5. 分析页面结构...');
    
    const analysis = await page.evaluate(() => {
      const result = {
        url: window.location.href,
        title: document.title,
        // 基本结构
        hasHeader: !!document.querySelector('header'),
        hasNav: !!document.querySelector('nav'),
        hasMain: !!document.querySelector('main'),
        hasFooter: !!document.querySelector('footer'),
        // 博客相关
        articles: document.querySelectorAll('article, .post, .blog-post, .article').length,
        hasSidebar: !!document.querySelector('.sidebar, aside'),
        hasPagination: !!document.querySelector('.pagination, .page-numbers'),
        hasSearch: !!document.querySelector('input[type="search"]'),
        // 内容区域
        h1Count: document.querySelectorAll('h1').length,
        h2Count: document.querySelectorAll('h2').length,
        paragraphCount: document.querySelectorAll('p').length
      };
      
      // 获取文章信息
      if (result.articles > 0) {
        const firstArticle = document.querySelector('article, .post, .blog-post');
        if (firstArticle) {
          result.firstArticle = {
            hasTitle: !!firstArticle.querySelector('h1, h2, h3, .title'),
            hasDate: !!firstArticle.querySelector('.date, time, .post-date'),
            hasExcerpt: !!firstArticle.querySelector('.excerpt, .summary, p')
          };
        }
      }
      
      return result;
    });
    
    console.log('   页面分析结果:');
    console.log(`   URL: ${analysis.url}`);
    console.log(`   标题: ${analysis.title}`);
    console.log(`   是否有header: ${analysis.hasHeader}`);
    console.log(`   是否有nav: ${analysis.hasNav}`);
    console.log(`   是否有main: ${analysis.hasMain}`);
    console.log(`   是否有footer: ${analysis.hasFooter}`);
    console.log(`   文章数量: ${analysis.articles}`);
    console.log(`   是否有侧边栏: ${analysis.hasSidebar}`);
    console.log(`   是否有分页: ${analysis.hasPagination}`);
    console.log(`   是否有搜索框: ${analysis.hasSearch}`);
    console.log(`   H1标题数量: ${analysis.h1Count}`);
    console.log(`   H2标题数量: ${analysis.h2Count}`);
    console.log(`   段落数量: ${analysis.paragraphCount}`);
    
    if (analysis.firstArticle) {
      console.log('   第一篇文章信息:');
      console.log(`     是否有标题: ${analysis.firstArticle.hasTitle}`);
      console.log(`     是否有日期: ${analysis.firstArticle.hasDate}`);
      console.log(`     是否有摘要: ${analysis.firstArticle.hasExcerpt}`);
    }
    
    // 6. 生成探索报告
    console.log('\n6. 生成探索报告...');
    
    const report = {
      explorationDate: new Date().toISOString(),
      homepage: homepageInfo,
      blogPage: {
        found: !!blogUrl,
        url: blogUrl,
        title: blogTitle
      },
      pageAnalysis: analysis,
      testableFeatures: [
        '页面加载和导航',
        '链接可点击性',
        '响应式布局',
        '文章列表展示',
        '搜索功能（如果存在）',
        '分页功能（如果存在）',
        '分类筛选（如果存在）'
      ],
      elementSelectors: {
        navigation: analysis.hasNav ? 'nav' : 'header nav, .navbar, .menu',
        articles: analysis.articles > 0 ? 'article, .post, .blog-post' : '可能需要自定义选择器',
        sidebar: analysis.hasSidebar ? '.sidebar, aside' : '无',
        pagination: analysis.hasPagination ? '.pagination, .page-numbers' : '无',
        search: analysis.hasSearch ? 'input[type="search"]' : '无'
      }
    };
    
    console.log('\n=== 探索报告摘要 ===');
    console.log(`探索时间: ${report.explorationDate}`);
    console.log(`主页URL: ${report.homepage.url}`);
    console.log(`是否找到博客页面: ${report.blogPage.found ? '是' : '否'}`);
    if (report.blogPage.found) {
      console.log(`博客页面URL: ${report.blogPage.url}`);
      console.log(`博客页面标题: ${report.blogPage.title}`);
    }
    console.log(`文章数量: ${report.pageAnalysis.articles}`);
    console.log('\n可测试功能点:');
    report.testableFeatures.forEach((feature, i) => {
      console.log(`  ${i+1}. ${feature}`);
    });
    console.log('\n元素选择器:');
    for (const [element, selector] of Object.entries(report.elementSelectors)) {
      console.log(`  ${element}: ${selector}`);
    }
    
  } catch (error) {
    console.error('探索过程中出错:', error);
  } finally {
    await browser.close();
    console.log('\n=== 探索完成 ===');
  }
})();