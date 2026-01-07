const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('=== 开始探索PlayTurbo网站 ===\n');
  
  try {
    // 1. 访问主页
    console.log('1. 访问主页: https://www.playturbo.com/');
    await page.goto('https://www.playturbo.com/', { waitUntil: 'networkidle' });
    
    console.log('   页面标题:', await page.title());
    console.log('   当前URL:', page.url());
    
    // 截图主页
    await page.screenshot({ path: 'playturbo-home.png', fullPage: true });
    console.log('   主页截图已保存: playturbo-home.png\n');
    
    // 2. 查找博客链接
    console.log('2. 查找博客相关链接...');
    
    // 查找所有链接
    const links = await page.$$eval('a', anchors => 
      anchors.map(a => ({
        text: a.textContent?.trim(),
        href: a.href,
        class: a.className
      }))
    );
    
    console.log(`   页面总链接数: ${links.length}`);
    
    // 过滤博客相关链接
    const blogKeywords = ['blog', '博客', '文章', 'post', 'news', '新闻', 'Blog'];
    const blogLinks = links.filter(link => {
      if (!link.text || !link.href) return false;
      
      const text = link.text.toLowerCase();
      const href = link.href.toLowerCase();
      
      return blogKeywords.some(keyword => 
        text.includes(keyword) || href.includes(keyword)
      );
    });
    
    console.log(`   找到 ${blogLinks.length} 个博客相关链接:`);
    blogLinks.forEach((link, i) => {
      console.log(`   ${i+1}. "${link.text}" -> ${link.href}`);
    });
    
    // 3. 尝试点击第一个博客链接
    if (blogLinks.length > 0) {
      const firstBlogLink = blogLinks[0];
      console.log(`\n3. 点击第一个博客链接: "${firstBlogLink.text}"`);
      
      // 找到并点击链接
      const linkElement = await page.$(`a[href="${firstBlogLink.href}"]`);
      if (linkElement) {
        await linkElement.click();
        await page.waitForLoadState('networkidle');
        
        console.log('   博客页面URL:', page.url());
        console.log('   博客页面标题:', await page.title());
        
        // 截图博客页面
        await page.screenshot({ path: 'playturbo-blog.png', fullPage: true });
        console.log('   博客页面截图已保存: playturbo-blog.png\n');
        
        // 4. 分析博客页面结构
        console.log('4. 分析博客页面结构...');
        
        // 检查文章列表
        const articles = await page.$$('article, .post, .blog-post, .article');
        console.log(`   文章数量: ${articles.length}`);
        
        if (articles.length > 0) {
          // 分析第一篇文章
          const firstArticle = articles[0];
          
          // 文章标题
          const title = await firstArticle.$eval('h1, h2, h3, .title', el => el.textContent?.trim());
          console.log(`   第一篇文章标题: ${title || '未找到'}`);
          
          // 文章日期
          const date = await firstArticle.$eval('.date, .post-date, time', el => el.textContent?.trim()).catch(() => null);
          console.log(`   发布日期: ${date || '未找到'}`);
          
          // 文章摘要
          const excerpt = await firstArticle.$eval('.excerpt, .summary, p', el => el.textContent?.trim()).catch(() => null);
          console.log(`   文章摘要: ${excerpt ? excerpt.substring(0, 100) + '...' : '未找到'}`);
        }
        
        // 检查侧边栏
        const sidebar = await page.$('.sidebar, aside');
        if (sidebar) {
          console.log('   找到侧边栏');
          
          // 检查侧边栏内容
          const sidebarText = await sidebar.textContent();
          console.log(`   侧边栏内容预览: ${sidebarText?.substring(0, 150)}...`);
        }
        
        // 检查分页
        const pagination = await page.$('.pagination, .page-numbers');
        if (pagination) {
          console.log('   找到分页组件');
        }
        
        // 检查搜索框
        const searchInput = await page.$('input[type="search"]');
        if (searchInput) {
          console.log('   找到搜索框');
        }
        
      } else {
        console.log('   无法找到链接元素，尝试直接访问...');
        await page.goto(firstBlogLink.href, { waitUntil: 'networkidle' });
        console.log('   直接访问URL:', page.url());
      }
    } else {
      console.log('\n3. 未找到明显的博客链接，尝试常见博客URL...');
      
      // 尝试常见博客URL
      const commonBlogUrls = [
        'https://www.playturbo.com/blog',
        'https://blog.playturbo.com',
        'https://www.playturbo.com/posts',
        'https://www.playturbo.com/articles'
      ];
      
      for (const url of commonBlogUrls) {
        try {
          console.log(`   尝试访问: ${url}`);
          await page.goto(url, { waitUntil: 'networkidle', timeout: 10000 });
          
          if (page.url().includes('blog') || page.url().includes('post') || page.url().includes('article')) {
            console.log(`   成功访问博客页面: ${page.url()}`);
            console.log(`   页面标题: ${await page.title()}`);
            
            await page.screenshot({ path: 'playturbo-blog-direct.png', fullPage: true });
            console.log('   博客页面截图已保存: playturbo-blog-direct.png');
            break;
          }
        } catch (error) {
          console.log(`   无法访问 ${url}`);
        }
      }
    }
    
    // 5. 收集页面元素信息
    console.log('\n5. 收集页面元素信息...');
    
    // 获取当前页面所有重要元素
    const pageInfo = await page.evaluate(() => {
      const elements = {
        // 导航
        nav: document.querySelector('nav') ? 'nav' : 
             document.querySelector('header nav') ? 'header nav' :
             document.querySelector('.navbar') ? '.navbar' : null,
        
        // 文章容器
        articleContainer: document.querySelector('.articles') ? '.articles' :
                         document.querySelector('.posts') ? '.posts' :
                         document.querySelector('.blog-posts') ? '.blog-posts' :
                         document.querySelector('article') ? 'article' : null,
        
        // 侧边栏
        sidebar: document.querySelector('.sidebar') ? '.sidebar' :
                 document.querySelector('aside') ? 'aside' : null,
        
        // 分页
        pagination: document.querySelector('.pagination') ? '.pagination' :
                    document.querySelector('.page-numbers') ? '.page-numbers' : null,
        
        // 搜索
        searchForm: document.querySelector('form[role="search"]') ? 'form[role="search"]' :
                    document.querySelector('form input[type="search"]') ? 'form input[type="search"]' : null,
        
        // 页脚
        footer: document.querySelector('footer') ? 'footer' : null
      };
      
      // 统计文章数量
      const articleCount = document.querySelectorAll('article, .post, .blog-post').length;
      
      return {
        url: window.location.href,
        title: document.title,
        elements,
        articleCount
      };
    });
    
    console.log('   当前页面信息:');
    console.log(`   URL: ${pageInfo.url}`);
    console.log(`   标题: ${pageInfo.title}`);
    console.log(`   文章数量: ${pageInfo.articleCount}`);
    console.log('   元素选择器:');
    for (const [key, value] of Object.entries(pageInfo.elements)) {
      if (value) console.log(`     ${key}: ${value}`);
    }
    
  } catch (error) {
    console.error('探索过程中出错:', error);
  } finally {
    console.log('\n=== 探索完成 ===');
    await browser.close();
  }
})();