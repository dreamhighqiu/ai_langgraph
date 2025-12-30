/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// @ts-expect-error  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVhSTk9BPT06NGM3ZTU2MDA=

/**
 * API-only environment configuration
 * Only enables API testing tools, disables all browser automation tools
 * Ideal for lightweight deployments focused on API testing
 */
module.exports = {
    features: {
        enableDebugMode: process.env.MCP_FEATURES_ENABLEDEBUGMODE === 'true',
        // Only API tools enabled
        enableApiTools: true,
        enableBrowserTools: false,
        enableAdvancedTools: false,
        enableFileTools: false,
        enableNetworkTools: false,
        enableOtherTools: false
    },
    
    logging: {
        level: 'warn',
        enableToolDebug: false
    },
    
    tools: {
        validationLevel: 'strict',
        // API tool specific configurations
        api: {
            api_request: {
                maxSessionTimeout: 300000, // 5 minutes
                maxConcurrentSessions: 10,
                enableRetries: true,
                defaultRetryAttempts: 3,
                enableRequestLogging: true,
                enableResponseLogging: true
            },
            api_session_report: {
                defaultTheme: 'light',
                includeTimestamp: true,
                maxReportSize: '10MB',
                enableCompressionForLargeReports: true
            },
            api_session_status: {
                enableRealTimeUpdates: true,
                maxHistoryEntries: 1000
            }
        }
    },
    
    security: {
        enableInputValidation: true,
        rateLimiting: true,
        maxRequestsPerMinute: 100
    }
};
// eslint-disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVhSTk9BPT06NGM3ZTU2MDA=
