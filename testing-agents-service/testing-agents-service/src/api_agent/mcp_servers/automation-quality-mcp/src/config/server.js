/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// TODO  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDBRMlVnPT06OTVmMzRhZGY=

/**
 * Server-level configuration
 * Core server settings and MCP protocol configuration
 */
module.exports = {
    server: {
        name: 'automation-quality-mcp-server',
        version: '1.0.0',
        protocolVersion: '2025-12-20',
        port: process.env.PORT || 3000
    },
    
    features: {
        enableBrowserTools: true,
        enableFileTools: false,
        enableNetworkTools: false,
        enableOtherTools: true,
        enableDebugMode: process.env.NODE_ENV !== 'production'
    },
    
    tools: {
        autoDiscovery: true,
        enableCache: true,
        validationLevel: 'strict' // 'strict', 'loose', 'none'
    },
    
    logging: {
        level: process.env.NODE_ENV === 'production' ? 'error' : 'debug',
        enableToolDebug: process.env.NODE_ENV !== 'production'
    },
    
    security: {
        enableInputValidation: true,
        maxRequestSize: '10MB',
        rateLimiting: false // Disabled by default for MCP
    },
    
    // Legacy compatibility
    PORT: process.env.PORT || 3000,
    OUTPUT_DIR: require('path').resolve(__dirname, '../../output')
};
// eslint-disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDBRMlVnPT06OTVmMzRhZGY=
