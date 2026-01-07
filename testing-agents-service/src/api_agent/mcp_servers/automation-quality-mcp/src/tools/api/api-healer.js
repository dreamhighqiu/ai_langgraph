/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

const ToolBase = require('../base/ToolBase');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

let z;
try {
    const zod = require('zod');
    z = zod.z || zod.default?.z || zod;
    if (!z || typeof z.object !== 'function') {
        throw new Error('Zod not properly loaded');
    }
} catch (error) {
    console.error('Failed to load Zod:', error.message);
    // Fallback: create a simple validation function
    z = {
        object: (schema) => ({ parse: (data) => data }),
        string: () => ({ optional: () => ({}) }),
        enum: () => ({ optional: () => ({}) }),
        record: () => ({ optional: () => ({}) }),
        any: () => ({ optional: () => ({}) }),
        number: () => ({ optional: () => ({}) }),
        array: () => ({ optional: () => ({}) }),
        boolean: () => ({ optional: () => ({}) })
    };
}

// Input schema for the API healer tool
const apiHealerInputSchema = z.object({
    testPath: z.string().optional(),
    testFiles: z.array(z.string()).optional(),
    testType: z.enum(['jest', 'playwright', 'postman', 'auto']).optional(),
    sessionId: z.string().optional(),
    maxHealingAttempts: z.number().optional(),
    autoFix: z.boolean().optional(),
    backupOriginal: z.boolean().optional(),
    analysisOnly: z.boolean().optional(),
    healingStrategies: z.array(z.enum(['schema-update', 'endpoint-fix', 'auth-repair', 'data-correction', 'assertion-update'])).optional()
});

/**
 * API Healer Tool - Debug and fix failing API tests
 */
class ApiHealerTool extends ToolBase {
    static definition = {
        name: "api_healer",
        description: "Debug and automatically fix failing API tests by analyzing errors, updating assertions, fixing endpoints, and correcting test data.",
        input_schema: {
            type: "object",
            properties: {
                testPath: {
                    type: "string",
                    description: "Path to a specific test file to heal"
                },
                testFiles: {
                    type: "array",
                    items: { type: "string" },
                    description: "Array of test file paths to heal (alternative to testPath)"
                },
                testType: {
                    type: "string",
                    enum: ["jest", "playwright", "postman", "auto"],
                    description: "Type of tests to heal - auto-detects if not specified"
                },
                sessionId: {
                    type: "string",
                    description: "Session ID for tracking healing process"
                },
                maxHealingAttempts: {
                    type: "number",
                    description: "Maximum number of healing attempts per test (default: 3)"
                },
                autoFix: {
                    type: "boolean",
                    description: "Automatically apply fixes without confirmation (default: true)"
                },
                backupOriginal: {
                    type: "boolean",
                    description: "Create backup of original test files (default: true)"
                },
                analysisOnly: {
                    type: "boolean",
                    description: "Only analyze failures without applying fixes (default: false)"
                },
                healingStrategies: {
                    type: "array",
                    items: {
                        type: "string",
                        enum: ["schema-update", "endpoint-fix", "auth-repair", "data-correction", "assertion-update"]
                    },
                    description: "Specific healing strategies to apply (default: all strategies)"
                }
            },
            oneOf: [
                { required: ["testPath"] },
                { required: ["testFiles"] }
            ]
        }
    };

    constructor() {
        super();
        this.apiRequestTool = null;
    }

    async execute(parameters) {
        try {
            const params = apiHealerInputSchema.parse(parameters);
            
            // Set defaults
            const options = {
                testType: params.testType || 'auto',
                sessionId: params.sessionId || `api-heal-${Date.now()}`,
                maxHealingAttempts: params.maxHealingAttempts || 3,
                autoFix: params.autoFix !== false,
                backupOriginal: params.backupOriginal !== false,
                analysisOnly: params.analysisOnly || false,
                healingStrategies: params.healingStrategies || ['schema-update', 'endpoint-fix', 'auth-repair', 'data-correction', 'assertion-update']
            };

            // Get test files to heal
            let testFiles = [];
            if (params.testPath) {
                testFiles = [params.testPath];
            } else if (params.testFiles) {
                testFiles = params.testFiles;
            }
// NOTE  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlRCdFNRPT06MThmZDE2ZWI=

            // Validate test files exist
            for (const testFile of testFiles) {
                if (!fs.existsSync(testFile)) {
                    throw new Error(`Test file not found: ${testFile}`);
                }
            }

            // Auto-detect test type if needed
            if (options.testType === 'auto') {
                options.testType = this._detectTestType(testFiles[0]);
            }

            const healingResults = {
                sessionId: options.sessionId,
                totalFiles: testFiles.length,
                processedFiles: 0,
                fixedFiles: 0,
                failedFiles: 0,
                results: []
            };

            // Process each test file
            for (const testFile of testFiles) {
                console.error(`[API Healer] Processing: ${testFile}`);
                
                try {
                    const fileResult = await this._healTestFile(testFile, options);
                    healingResults.results.push(fileResult);
                    healingResults.processedFiles++;
                    
                    if (fileResult.success) {
                        healingResults.fixedFiles++;
                    } else {
                        healingResults.failedFiles++;
                    }
                } catch (error) {
                    healingResults.results.push({
                        file: testFile,
                        success: false,
                        error: error.message,
                        healingAttempts: 0,
                        appliedFixes: []
                    });
                    healingResults.failedFiles++;
                }
            }

            return {
                success: true,
                message: `API healing completed for ${healingResults.processedFiles} files`,
                ...healingResults
            };

        } catch (error) {
            return {
                success: false,
                error: error.message,
                details: error.stack
            };
        }
    }

    _detectTestType(testFile) {
        const content = fs.readFileSync(testFile, 'utf8');
        
        if (content.includes('@playwright/test') || content.includes('test.describe')) {
            return 'playwright';
        } else if (content.includes('describe(') && content.includes('jest')) {
            return 'jest';
        } else if (testFile.endsWith('.postman_collection.json')) {
            return 'postman';
        } else if (content.includes('describe(') || content.includes('test(')) {
            return 'jest'; // Default to Jest for generic test files
        }
        
        throw new Error(`Unable to detect test type for file: ${testFile}`);
    }

    async _healTestFile(testFile, options) {
        const result = {
            file: testFile,
            success: false,
            healingAttempts: 0,
            appliedFixes: [],
            errors: [],
            finalStatus: 'failed'
        };

        // Create backup if requested
        if (options.backupOriginal) {
            const backupPath = `${testFile}.backup.${Date.now()}`;
            fs.copyFileSync(testFile, backupPath);
            result.backupPath = backupPath;
        }

        // Initial test run to identify failures
        let testErrors = await this._runTests(testFile, options.testType);
        result.errors = testErrors;

        if (testErrors.length === 0) {
            result.success = true;
            result.finalStatus = 'passing';
            return result;
        }
// @ts-expect-error  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlRCdFNRPT06MThmZDE2ZWI=

        if (options.analysisOnly) {
            result.analysis = await this._analyzeErrors(testErrors, testFile);
            return result;
        }

        // Healing loop
        for (let attempt = 1; attempt <= options.maxHealingAttempts && testErrors.length > 0; attempt++) {
            result.healingAttempts = attempt;
            console.error(`[API Healer] Healing attempt ${attempt}/${options.maxHealingAttempts} for ${testFile}`);

            const fixes = await this._generateFixes(testErrors, testFile, options);

            if (fixes.length === 0) {
                console.error('[API Healer] No fixes available for current errors');
                break;
            }

            // Apply fixes
            for (const fix of fixes) {
                try {
                    await this._applyFix(fix, testFile);
                    result.appliedFixes.push(fix);
                    console.error(`[API Healer] Applied fix: ${fix.type} - ${fix.description}`);
                } catch (error) {
                    console.error(`[API Healer] Failed to apply fix: ${fix.type} - ${error.message}`);
                }
            }

            // Re-run tests to check if issues are resolved
            testErrors = await this._runTests(testFile, options.testType);
            
            if (testErrors.length === 0) {
                result.success = true;
                result.finalStatus = 'healed';
                break;
            }
        }

        if (testErrors.length > 0) {
            result.finalStatus = 'partially-healed';
            result.remainingErrors = testErrors;
        }

        return result;
    }

    async _runTests(testFile, testType) {
        return new Promise((resolve) => {
            let command, args;
            
            switch (testType) {
                case 'jest':
                    command = 'npx';
                    args = ['jest', testFile, '--verbose', '--no-coverage'];
                    break;
                case 'playwright':
                    command = 'npx';
                    args = ['playwright', 'test', testFile];
                    break;
                default:
                    resolve([{ type: 'unknown', message: `Unsupported test type: ${testType}` }]);
                    return;
            }

            const process = spawn(command, args, { cwd: path.dirname(testFile) });
            let output = '';
            let errorOutput = '';

            process.stdout.on('data', (data) => {
                output += data.toString();
            });

            process.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });

            process.on('close', (code) => {
                const errors = this._parseTestErrors(output + errorOutput, testType);
                resolve(errors);
            });

            process.on('error', (error) => {
                resolve([{ type: 'execution', message: `Failed to run tests: ${error.message}` }]);
            });
        });
    }
// @ts-expect-error  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlRCdFNRPT06MThmZDE2ZWI=

    _parseTestErrors(output, testType) {
        const errors = [];
        
        switch (testType) {
            case 'jest':
                errors.push(...this._parseJestErrors(output));
                break;
            case 'playwright':
                errors.push(...this._parsePlaywrightErrors(output));
                break;
        }

        return errors;
    }

    _parseJestErrors(output) {
        const errors = [];
        const lines = output.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // HTTP errors
            if (line.includes('Request failed with status code')) {
                const statusMatch = line.match(/status code (\d+)/);
                if (statusMatch) {
                    errors.push({
                        type: 'http-error',
                        statusCode: parseInt(statusMatch[1]),
                        message: line.trim(),
                        line: i + 1
                    });
                }
            }
            
            // Assertion errors
            else if (line.includes('expect(') && line.includes('toBe')) {
                errors.push({
                    type: 'assertion-error',
                    message: line.trim(),
                    line: i + 1
                });
            }
            
            // Network errors
            else if (line.includes('ECONNREFUSED') || line.includes('ENOTFOUND')) {
                errors.push({
                    type: 'network-error',
                    message: line.trim(),
                    line: i + 1
                });
            }
            
            // Authentication errors
            else if (line.includes('401') || line.includes('403') || line.includes('Unauthorized')) {
                errors.push({
                    type: 'auth-error',
                    message: line.trim(),
                    line: i + 1
                });
            }
            
            // Timeout errors
            else if (line.includes('timeout') || line.includes('ETIMEDOUT')) {
                errors.push({
                    type: 'timeout-error',
                    message: line.trim(),
                    line: i + 1
                });
            }
        }
// FIXME  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YlRCdFNRPT06MThmZDE2ZWI=

        return errors;
    }

    _parsePlaywrightErrors(output) {
        const errors = [];
        const lines = output.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            // API response errors
            if (line.includes('apiRequestContext.get') || line.includes('apiRequestContext.post')) {
                if (lines[i + 1] && lines[i + 1].includes('Error:')) {
                    errors.push({
                        type: 'api-error',
                        message: lines[i + 1].trim(),
                        line: i + 1
                    });
                }
            }
            
            // Assertion errors
            else if (line.includes('expect(') && line.includes('toBe')) {
                errors.push({
                    type: 'assertion-error',
                    message: line.trim(),
                    line: i + 1
                });
            }
        }

        return errors;
    }

    async _analyzeErrors(errors, testFile) {
        const analysis = {
            totalErrors: errors.length,
            errorTypes: {},
            recommendations: [],
            healable: true
        };

        // Categorize errors
        errors.forEach(error => {
            if (!analysis.errorTypes[error.type]) {
                analysis.errorTypes[error.type] = 0;
            }
            analysis.errorTypes[error.type]++;
        });

        // Generate recommendations
        Object.keys(analysis.errorTypes).forEach(errorType => {
            switch (errorType) {
                case 'http-error':
                    analysis.recommendations.push('Check API endpoint URLs and HTTP methods');
                    break;
                case 'assertion-error':
                    analysis.recommendations.push('Update test assertions to match current API responses');
                    break;
                case 'auth-error':
                    analysis.recommendations.push('Update authentication tokens or credentials');
                    break;
                case 'network-error':
                    analysis.recommendations.push('Verify API server is running and accessible');
                    analysis.healable = false;
                    break;
                case 'timeout-error':
                    analysis.recommendations.push('Increase timeout values or check API performance');
                    break;
            }
        });

        return analysis;
    }

    async _generateFixes(errors, testFile, options) {
        const fixes = [];
        const testContent = fs.readFileSync(testFile, 'utf8');

        for (const error of errors) {
            switch (error.type) {
                case 'http-error':
                    if (error.statusCode === 404) {
                        fixes.push(await this._generateEndpointFix(error, testContent));
                    } else if (error.statusCode === 401 || error.statusCode === 403) {
                        fixes.push(await this._generateAuthFix(error, testContent));
                    } else if (error.statusCode >= 400 && error.statusCode < 500) {
                        fixes.push(await this._generateDataFix(error, testContent));
                    }
                    break;
                    
                case 'assertion-error':
                    fixes.push(await this._generateAssertionFix(error, testContent));
                    break;
                    
                case 'auth-error':
                    fixes.push(await this._generateAuthFix(error, testContent));
                    break;
                    
                case 'timeout-error':
                    fixes.push(this._generateTimeoutFix(error, testContent));
                    break;
            }
        }

        return fixes.filter(fix => fix !== null);
    }

    async _generateEndpointFix(error, testContent) {
        // Try to identify the failing endpoint and suggest alternatives
        const urlMatches = testContent.match(/['"`]([^'"`]*\/[^'"`]*)['"`]/g);
        
        if (urlMatches && urlMatches.length > 0) {
            // For now, return a placeholder fix
            return {
                type: 'endpoint-fix',
                description: 'Update endpoint URL to match current API',
                pattern: urlMatches[0],
                replacement: urlMatches[0], // Would implement actual endpoint discovery
                confidence: 0.5
            };
        }
        
        return null;
    }

    async _generateAuthFix(error, testContent) {
        return {
            type: 'auth-repair',
            description: 'Update authentication method or refresh tokens',
            pattern: /Authorization['":\s]+['"`]([^'"`]*)['"`]/,
            replacement: 'Authorization: "Bearer {{updated_token}}"',
            confidence: 0.8
        };
    }

    async _generateDataFix(error, testContent) {
        return {
            type: 'data-correction',
            description: 'Update request payload to match API schema',
            pattern: /data:\s*{[^}]*}/,
            replacement: 'data: { /* Updated payload */ }',
            confidence: 0.6
        };
    }

    async _generateAssertionFix(error, testContent) {
        // Extract expected vs actual values from error message
        const expectMatch = error.message.match(/expect\(([^)]+)\)\.toBe\(([^)]+)\)/);
        
        if (expectMatch) {
            return {
                type: 'assertion-update',
                description: 'Update assertion to match actual API response',
                pattern: expectMatch[0],
                replacement: `expect(${expectMatch[1]}).toBe(/* actual value */)`,
                confidence: 0.9
            };
        }
        
        return null;
    }

    _generateTimeoutFix(error, testContent) {
        return {
            type: 'timeout-fix',
            description: 'Increase timeout values',
            pattern: /timeout:\s*\d+/,
            replacement: 'timeout: 30000',
            confidence: 0.7
        };
    }

    async _applyFix(fix, testFile) {
        if (!fix || !fix.pattern || !fix.replacement) {
            throw new Error('Invalid fix object');
        }

        let content = fs.readFileSync(testFile, 'utf8');
        
        if (typeof fix.pattern === 'string') {
            content = content.replace(fix.pattern, fix.replacement);
        } else if (fix.pattern instanceof RegExp) {
            content = content.replace(fix.pattern, fix.replacement);
        }
        
        fs.writeFileSync(testFile, content);
    }

    // Initialize API request tool for live API testing
    async _initializeApiTool() {
        if (!this.apiRequestTool) {
            const ApiRequestTool = require('./api-request');
            this.apiRequestTool = new ApiRequestTool();
        }
        return this.apiRequestTool;
    }

    // Test API endpoint to verify if it exists and returns expected data
    async _testApiEndpoint(method, url, headers = {}, data = null) {
        try {
            const apiTool = await this._initializeApiTool();
            const result = await apiTool.execute({
                method: method,
                url: url,
                headers: headers,
                data: data
            });
            
            return {
                success: result.success,
                statusCode: result.statusCode,
                data: result.data,
                headers: result.headers
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

module.exports = ApiHealerTool;
