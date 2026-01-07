/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// @ts-expect-error  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TW1oUmRnPT06ZjQ1MjA2YzQ=

/**
 * Production environment configuration
 * Settings optimized for production deployment
 */
module.exports = {
    features: {
        enableDebugMode: false,
        // Tool category feature flags - API tools enabled by default, others can be controlled
        enableApiTools: true,
        enableBrowserTools: process.env.ENABLE_BROWSER_TOOLS !== 'false',
        enableAdvancedTools: process.env.ENABLE_ADVANCED_TOOLS === 'true',
        enableFileTools: process.env.ENABLE_FILE_TOOLS === 'true',
        enableNetworkTools: process.env.ENABLE_NETWORK_TOOLS === 'true',
        enableOtherTools: process.env.ENABLE_OTHER_TOOLS === 'true'
    },
    
    logging: {
        level: 'error',
        enableToolDebug: false
    },
    
    tools: {
        validationLevel: 'strict',
        browser: {
            browser_launch: {
                defaultHeadless: true, // Always headless in production
                maxInstances: 3, // Conservative limit
                launchTimeout: 15000, // Shorter timeout
                chromeFlags: [
                    '--headless=new',
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--memory-pressure-off',
                    '--max_old_space_size=4096'
                ]
            },
            browser_screenshot: {
                defaultQuality: 60, // Lower quality for performance
                compressionLevel: 9, // Higher compression
                enableTimestamps: false
            },
            browser_dom: {
                highlightElements: false,
                enableRetries: false, // Fail fast in production
                defaultWaitTimeout: 3000 // Shorter timeout
            },
            browser_type: {
                typingDelay: 5, // Faster typing
                enableNaturalTyping: false
            },
            global: {
                maxConcurrentOperations: 2,
                enableScreenshotOnError: false,
                enablePerformanceMetrics: false,
                healthCheckInterval: 300000 // 5 minutes
            }
        }
    },
    
    security: {
        enableInputValidation: true,
        rateLimiting: true,
        maxRequestSize: '5MB'
    }
};
// @ts-expect-error  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TW1oUmRnPT06ZjQ1MjA2YzQ=
