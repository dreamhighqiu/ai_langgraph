/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// FIXME  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YUdGdFpBPT06ZTM4ZTBmMjQ=

/**
 * API Tools Configuration
 * Configuration specific to API testing tools
 */
module.exports = {
    // API Request Tool
    api_request: {
        // Session management
        maxSessions: 50,
        sessionTimeout: 600000, // 10 minutes
        enableSessionPersistence: true,
        
        // Request settings
        defaultTimeout: 30000,
        maxRetries: 3,
        retryDelay: 1000,
        enableRedirects: true,
        maxRedirects: 5,
        
        // Validation settings
        enableResponseValidation: true,
        enableBodyValidation: true,
        strictContentTypeCheck: true,
        
        // Logging settings
        enableRequestLogging: true,
        enableResponseLogging: true,
        logLevel: 'info',
        
        // Rate limiting
        rateLimitEnabled: false,
        maxRequestsPerSecond: 10
    },
    
    // API Session Status Tool
    api_session_status: {
        enableRealTimeUpdates: true,
        maxHistoryEntries: 1000,
        includeDetailedLogs: true,
        enableSessionMetrics: true
    },
    
    // API Session Report Tool
    api_session_report: {
        defaultTheme: 'light',
        includeRequestData: true,
        includeResponseData: true,
        includeTiming: true,
        includeValidationResults: true,
        
        // Report generation settings
        maxReportSize: 10485760, // 10MB
        enableCompression: true,
        compressionLevel: 6,
        
        // HTML report settings
        enableInteractiveReports: true,
        includeCharts: true,
        enableSyntaxHighlighting: true,
        
        // Output settings
        defaultOutputDir: process.env.API_REPORTS_DIR || 'output/reports',
        enableTimestampInFilename: true,
        enableAutoCleanup: true,
        maxReportsToKeep: 100
    }
};
// eslint-disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YUdGdFpBPT06ZTM4ZTBmMjQ=
