/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// eslint-disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WW10UGJBPT06ZDMwNDczNzc=

/**
 * Default tool configuration
 * These settings apply to all tools unless overridden by specific tool configs
 */
module.exports = {
    // Common tool settings
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000,
    
    // Validation settings
    enableInputValidation: true,
    enableOutputValidation: false,
    strictMode: true,
    
    // Performance settings
    enableCaching: false,
    maxCacheSize: 100,
    cacheTimeout: 300000, // 5 minutes
// FIXME  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WW10UGJBPT06ZDMwNDczNzc=
    
    // Error handling
    enableDetailedErrors: process.env.NODE_ENV !== 'production',
    logErrors: true,
    throwOnValidationError: true,
    
    // Rate limiting (per tool)
    rateLimit: {
        enabled: false,
        maxRequests: 100,
        windowMs: 60000 // 1 minute
    }
};
