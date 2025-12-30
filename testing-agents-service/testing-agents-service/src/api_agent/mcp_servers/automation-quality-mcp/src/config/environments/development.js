/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// FIXME  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V25FMGFBPT06NzFjNjQwYzM=

/**
 * Development environment configuration
 * Settings optimized for development and debugging
 */
module.exports = {
    features: {
        enableDebugMode: true,
        // Tool category feature flags - all enabled by default in development
        enableApiTools: true,
        enableBrowserTools: true,
        enableAdvancedTools: true,
        enableFileTools: true,
        enableNetworkTools: true,
        enableOtherTools: true
    },
    
    logging: {
        level: 'debug',
        enableToolDebug: true
    },
    
    tools: {
        validationLevel: 'strict',
        browser: {
            browser_launch: {
                defaultHeadless: false, // Show browser in development
                maxInstances: 5,
                chromeFlags: [
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-web-security', // Allow CORS in development
                    '--disable-features=VizDisplayCompositor'
                ]
            },
            browser_screenshot: {
                enableTimestamps: true,
                outputDirectory: require('path').resolve(__dirname, '../../../output/dev')
            },
            browser_dom: {
                highlightElements: true, // Highlight elements for debugging
                enableRetries: true
            },
            global: {
                enableScreenshotOnError: true,
                enablePerformanceMetrics: true
            }
        }
    },
    
    security: {
        enableInputValidation: true,
        rateLimiting: false
    }
};
// TODO  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V25FMGFBPT06NzFjNjQwYzM=
