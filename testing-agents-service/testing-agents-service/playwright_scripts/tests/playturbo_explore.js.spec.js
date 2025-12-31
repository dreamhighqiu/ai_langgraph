const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('正在访问 PlayTurbo 网站...');
  await page.goto('https://www.playturbo.com/');
  
  // 等待页面加载
  await page.waitForLoadState('networkidle');
  
  // 获取页面基本信息
  const title = await page.title();
  const url = page.url();
  
  console.log('=== 网站基本信息 ===');
  console.log(`标题: ${title}`);
  console.log(`URL: ${url}`);
  
  // 获取所有链接
  const links = await page.$$eval('a[href]', anchors => 
    anchors.map(a => ({
      text: a.textContent?.trim() || '',
      href: a.getAttribute('href'),
      class: a.getAttribute('class') || ''
    }))
  );
  
  console.log(`\n=== 找到 ${links.length} 个链接 ===`);
  
  // 过滤并显示主要链接
  const mainLinks = links.filter(link => 
    link.href && 
    !link.href.startsWith('#') && 
    !link.href.includes('javascript:') &&
    link.text.length > 0
  );
  
  console.log(`主要链接数量: ${mainLinks.length}`);
  
  // 按域名分组链接
  const internalLinks = mainLinks.filter(link => 
    link.href.startsWith('/') || link.href.includes('playturbo.com')
  );
  
  const externalLinks = mainLinks.filter(link => 
    !link.href.startsWith('/') && !link.href.includes('playturbo.com')
  );
  
  console.log(`\n内部链接 (${internalLinks.length}):`);
  internalLinks.slice(0, 20).forEach((link, i) => {
    console.log(`  ${i+1}. "${link.text}" -> ${link.href}`);
  });
  
  console.log(`\n外部链接 (${externalLinks.length}):`);
  externalLinks.slice(0, 10).forEach((link, i) => {
    console.log(`  ${i+1}. "${link.text}" -> ${link.href}`);
  });
  
  // 获取所有按钮
  const buttons = await page.$$eval('button, [role="button"], .btn, input[type="button"], input[type="submit"]', elements =>
    elements.map(el => ({
      text: el.textContent?.trim() || el.value || '',
      type: el.tagName.toLowerCase(),
      class: el.getAttribute('class') || '',
      id: el.getAttribute('id') || ''
    }))
  );
  
  console.log(`\n=== 找到 ${buttons.length} 个按钮 ===`);
  buttons.slice(0, 15).forEach((btn, i) => {
    console.log(`  ${i+1}. ${btn.type} "${btn.text}" class="${btn.class}" id="${btn.id}"`);
  });
  
  // 获取所有表单
  const forms = await page.$$eval('form', forms =>
    forms.map(form => ({
      id: form.getAttribute('id') || '',
      class: form.getAttribute('class') || '',
      action: form.getAttribute('action') || '',
      method: form.getAttribute('method') || 'GET'
    }))
  );
  
  console.log(`\n=== 找到 ${forms.length} 个表单 ===`);
  forms.forEach((form, i) => {
    console.log(`  ${i+1}. id="${form.id}" class="${form.class}" action="${form.action}" method="${form.method}"`);
  });
  
  // 查找测试相关关键词
  const testKeywords = ['test', 'demo', 'trial', 'try', 'play', 'sandbox', '示例', '演示', '试用', '体验'];
  console.log('\n=== 测试相关功能搜索 ===');
  
  for (const keyword of testKeywords) {
    const elements = await page.$$(`:text("${keyword}"):visible`);
    if (elements.length > 0) {
      console.log(`找到 "${keyword}" 相关元素: ${elements.length} 个`);
    }
  }
  
  // 截图保存
  await page.screenshot({ path: 'playturbo_homepage.png', fullPage: true });
  console.log('\n截图已保存: playturbo_homepage.png');
  
  // 尝试访问主要内部链接
  console.log('\n=== 尝试访问主要页面 ===');
  const pagesToVisit = internalLinks
    .filter(link => link.text && link.text.length > 0)
    .slice(0, 5);
  
  for (const link of pagesToVisit) {
    try {
      console.log(`访问: "${link.text}" -> ${link.href}`);
      
      if (link.href.startsWith('/')) {
        await page.goto(`https://www.playturbo.com${link.href}`);
      } else if (link.href.startsWith('http')) {
        await page.goto(link.href);
      }
      
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      const pageTitle = await page.title();
      console.log(`  页面标题: ${pageTitle}`);
      
      // 返回主页
      await page.goto('https://www.playturbo.com/');
      await page.waitForLoadState('networkidle');
      
    } catch (error) {
      console.log(`  访问失败: ${error.message}`);
    }
  }
  
  await browser.close();
  console.log('\n=== 分析完成 ===');
})();