

const ToolBase = require('../base/ToolBase');
const https = require('https');
const http = require('http');
const { URL } = require('url');
const fs = require('fs').promises;
const path = require('path');

// Try to load GraphQL for SDL parsing
let graphql;
try {
    graphql = require('graphql');
    if (!graphql.buildSchema || !graphql.introspectionFromSchema || !graphql.getIntrospectionQuery) {
        console.warn('GraphQL loaded but required functions not available');
        graphql = null;
    }
} catch (error) {
    console.warn('GraphQL library not available, SDL files will not be supported:', error.message);
    graphql = null;
}

// Try to load faker.js for enhanced sample data generation
let faker;
try {
    const fakerModule = require('@faker-js/faker');
    faker = fakerModule.faker || fakerModule.default?.faker || fakerModule;
    if (!faker || typeof faker.person?.firstName !== 'function') {
        console.warn('Faker.js loaded but API not as expected, using fallback');
        faker = null;
    }
} catch (error) {
    console.warn('Faker.js not available, using built-in sample generation:', error.message);
    faker = null;
}

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
        union: () => ({ optional: () => ({}) })
    };
}

// Input schema for the API planner tool
const apiPlannerInputSchema = z.object({
    schemaUrl: z.string().optional(),
    schemaPath: z.string().optional(),
    schemaType: z.enum(['openapi', 'swagger', 'graphql', 'auto']).optional(),
    apiBaseUrl: z.string().optional(),
    includeAuth: z.boolean().optional(),
    includeSecurity: z.boolean().optional(),
    includeErrorHandling: z.boolean().optional(),
    outputPath: z.string().optional(),
    testCategories: z.array(z.enum(['functional', 'security', 'performance', 'integration', 'edge-cases'])).optional(),
    validateEndpoints: z.boolean().optional(),
    validationSampleSize: z.number().optional(),
    validationTimeout: z.number().optional()
});

/**
 * API Planner Tool - Analyze API schemas and generate comprehensive test plans
 */
class ApiPlannerTool extends ToolBase {
    static definition = {
        name: "api_planner",
        description: "Analyze API schemas (OpenAPI/Swagger, GraphQL) and generate comprehensive test plans with detailed scenarios covering functional, security, and edge case testing.",
        input_schema: {
            type: "object",
            properties: {
                schemaUrl: {
                    type: "string",
                    description: "URL to fetch the API schema/documentation (e.g., OpenAPI spec URL, GraphQL introspection endpoint)"
                },
                schemaPath: {
                    type: "string",
                    description: "File path to a local schema file (.graphql, .json, .yaml, .yml). GraphQL SDL files (.graphql, .gql) are automatically converted to introspection JSON. For large files, this is the recommended approach as it reads the complete file without truncation."
                },
                schemaType: {
                    type: "string",
                    enum: ["openapi", "swagger", "graphql", "auto"],
                    description: "Type of API schema - auto-detects if not specified"
                },
                apiBaseUrl: {
                    type: "string",
                    description: "Base URL of the API to be tested (overrides schema baseUrl if provided)"
                },
                includeAuth: {
                    type: "boolean",
                    description: "Include authentication testing scenarios (default: true)"
                },
                includeSecurity: {
                    type: "boolean", 
                    description: "Include security testing scenarios (default: true)"
                },
                includeErrorHandling: {
                    type: "boolean",
                    description: "Include error handling and edge case scenarios (default: true)"
                },
                outputPath: {
                    type: "string",
                    description: "File path to save the generated test plan (default: ./api-test-plan.md)"
                },
                testCategories: {
                    type: "array",
                    items: {
                        type: "string",
                        enum: ["functional", "security", "performance", "integration", "edge-cases"]
                    },
                    description: "Categories of tests to include (default: all categories)"
                },
                validateEndpoints: {
                    type: "boolean",
                    description: "Validate endpoints by making actual API calls to verify they work (default: false)"
                },
                validationSampleSize: {
                    type: "number",
                    description: "Number of endpoints to validate when validateEndpoints is true (default: 3, use -1 for all)"
                },
                validationTimeout: {
                    type: "number",
                    description: "Timeout in milliseconds for each validation request (default: 5000)"
                }
            },
            oneOf: [
                { required: ["schemaUrl"] },
                { required: ["schemaContent"] }
            ]
        }
    };

    constructor() {
        super();
        this.fs = require('fs');
        this.path = require('path');
        this.yaml = this._loadYaml();
    }

    _loadYaml() {
        try {
            return require('yaml');
        } catch (error) {
            console.warn('[ApiPlanner] YAML library not available, JSON-only parsing');
            return null;
        }
    }
// FIXME  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TTNWQ1JnPT06NmNkM2Q5Yzg=

    async execute(parameters) {
        try {
            const params = apiPlannerInputSchema.parse(parameters);
            
            // Validate apiBaseUrl if provided
            if (params.apiBaseUrl && !params.apiBaseUrl.match(/^https?:\/\//)) {
                throw new Error(
                    `Invalid apiBaseUrl: "${params.apiBaseUrl}". ` +
                    `The apiBaseUrl must be a full URL starting with http:// or https://, not a relative path. ` +
                    `Example: "https://petstore3.swagger.io/api/v3" instead of "/api/v3". ` +
                    `If you want to use the base URL from the OpenAPI schema, omit the apiBaseUrl parameter.`
                );
            }
            
            // Set defaults
            const options = {
                schemaType: params.schemaType || 'auto',
                includeAuth: params.includeAuth !== false,
                includeSecurity: params.includeSecurity !== false,
                includeErrorHandling: params.includeErrorHandling !== false,
                outputPath: params.outputPath || './api-test-plan.md',
                testCategories: params.testCategories || ['functional', 'security', 'performance', 'integration', 'edge-cases'],
                apiBaseUrl: params.apiBaseUrl,
                validateEndpoints: params.validateEndpoints || false,
                validationSampleSize: params.validationSampleSize || 3,
                validationTimeout: params.validationTimeout || 5000
            };

            // Fetch or parse schema
            let schemaData;
            if (params.schemaUrl) {
                schemaData = await this._fetchSchema(params.schemaUrl, options.schemaType);
            } else if (params.schemaPath) {
                schemaData = await this._readSchemaFromFile(params.schemaPath, options.schemaType);
            } else {
                throw new Error('Either schemaUrl or schemaPath must be provided. For local schema files, use schemaPath parameter.');
            }

            if (!schemaData) {
                throw new Error('Failed to load or parse API schema');
            }

            // Auto-detect schema type if needed
            if (options.schemaType === 'auto') {
                options.schemaType = this._detectSchemaType(schemaData);
            }

            // Generate test plan based on schema type
            let testPlan;
            switch (options.schemaType) {
                case 'openapi':
                case 'swagger':
                    testPlan = await this._generateOpenApiTestPlan(schemaData, options);
                    break;
                case 'graphql':
                    testPlan = await this._generateGraphQLTestPlan(schemaData, options);
                    break;
                default:
                    throw new Error(`Unsupported schema type: ${options.schemaType}`);
            }

            // Save test plan to file
            if (options.outputPath) {
                await this._saveTestPlan(testPlan, options.outputPath);
            }

            const result = {
                success: true,
                message: "API test plan generated successfully",
                schemaType: options.schemaType,
                outputPath: options.outputPath,
                endpoints: testPlan.summary.totalEndpoints,
                scenarios: testPlan.summary.totalScenarios,
                testPlan: testPlan.content
            };

            // Add validation results if available
            if (testPlan.validationSummary) {
                result.validationSummary = testPlan.validationSummary;
                result.message = `API test plan generated successfully. Validated ${testPlan.validationSummary.totalValidated} endpoints (${testPlan.validationSummary.successful} successful, ${testPlan.validationSummary.failed} failed)`;
            }

            return result;

        } catch (error) {
            return {
                success: false,
                error: error.message,
                details: error.stack
            };
        }
    }

    async _fetchSchema(url, schemaType = 'auto') {
        // If schemaType is 'graphql' or if URL suggests GraphQL endpoint, perform introspection
        const isGraphQL = schemaType === 'graphql' || 
                         url.toLowerCase().includes('graphql') ||
                         url.toLowerCase().includes('/graph');
        
        if (isGraphQL) {
            return await this._fetchGraphQLSchema(url);
        }
        
        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);
            const client = urlObj.protocol === 'https:' ? https : http;
// @ts-expect-error  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TTNWQ1JnPT06NmNkM2Q5Yzg=
            
            const options = {
                hostname: urlObj.hostname,
                port: urlObj.port,
                path: urlObj.pathname + urlObj.search,
                method: 'GET',
                headers: {
                    'Accept': 'application/json, application/yaml, text/yaml',
                    'User-Agent': 'Automation-Quality-MCP-Server/1.0'
                }
            };

            const req = client.request(options, (res) => {
                let data = '';
                
                res.on('data', (chunk) => {
                    data += chunk;
                });
                
                res.on('end', () => {
                    try {
                        const schema = this._parseSchemaContent(data, 'auto');
                        resolve(schema);
                    } catch (error) {
                        reject(new Error(`Failed to parse schema: ${error.message}`));
                    }
                });
            });

            req.on('error', (error) => {
                reject(new Error(`Failed to fetch schema: ${error.message}`));
            });

            req.setTimeout(30000, () => {
                req.destroy();
                reject(new Error('Schema fetch timeout'));
            });

            req.end();
        });
    }
    
    /**
     * Fetch GraphQL schema via introspection query
     * GENERIC - Works with any GraphQL endpoint
     */
    async _fetchGraphQLSchema(url) {
        return new Promise((resolve, reject) => {
            const urlObj = new URL(url);
            const client = urlObj.protocol === 'https:' ? https : http;
            
            const introspectionQuery = this._getGraphQLIntrospectionQuery();
            const postData = JSON.stringify({
                query: introspectionQuery
            });
            
            const options = {
                hostname: urlObj.hostname,
                port: urlObj.port,
                path: urlObj.pathname + urlObj.search,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'User-Agent': 'Automation-Quality-MCP-Server/1.0',
                    'Content-Length': Buffer.byteLength(postData)
                }
            };
// NOTE  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TTNWQ1JnPT06NmNkM2Q5Yzg=

            const req = client.request(options, (res) => {
                let data = '';
                
                res.on('data', (chunk) => {
                    data += chunk;
                });
                
                res.on('end', () => {
                    try {
                        const response = JSON.parse(data);
                        
                        // Check for GraphQL errors
                        if (response.errors) {
                            reject(new Error(`GraphQL introspection failed: ${response.errors[0].message}`));
                            return;
                        }
                        
                        // Return the introspection result
                        resolve(response);
                    } catch (error) {
                        reject(new Error(`Failed to parse GraphQL response: ${error.message}`));
                    }
                });
            });

            req.on('error', (error) => {
                reject(new Error(`Failed to fetch GraphQL schema: ${error.message}`));
            });

            req.setTimeout(30000, () => {
                req.destroy();
                reject(new Error('GraphQL introspection timeout'));
            });

            req.write(postData);
            req.end();
        });
    }

    /**
     * Read schema from local file system
     */
    async _readSchemaFromFile(filePath, schemaType = 'auto') {
        try {
            // Resolve absolute path
            const absolutePath = path.isAbsolute(filePath) ? filePath : path.resolve(process.cwd(), filePath);
            
            // Check file exists
            try {
                await fs.access(absolutePath);
            } catch (error) {
                throw new Error(`Schema file not found: ${absolutePath}`);
            }

            // Read file content
            const content = await fs.readFile(absolutePath, 'utf-8');
            const ext = path.extname(filePath).toLowerCase();

            // Handle .graphql files
            if (ext === '.graphql' || ext === '.gql') {
                // Check if content is GraphQL SDL or introspection JSON
                const trimmedContent = content.trim();
                
                // If it starts with '{', it's likely JSON introspection result
                if (trimmedContent.startsWith('{')) {
                    try {
                        return JSON.parse(content);
                    } catch (error) {
                        throw new Error(`GraphQL file contains invalid JSON: ${error.message}`);
                    }
                }
                
                // Otherwise it's SDL (Schema Definition Language) - convert it
                console.error(`📝 Detected GraphQL SDL in ${path.basename(filePath)}, converting to introspection JSON...`);
                
                if (!graphql) {
                    throw new Error(
                        `GraphQL SDL detected but 'graphql' package is not installed.\n` +
                        `Please install it: npm install graphql\n` +
                        `Or convert manually: npx graphql-cli introspect ${filePath}`
                    );
                }
                
                try {
                    // Build schema from SDL
                    const schema = graphql.buildSchema(content);
                    
                    // Generate introspection query result
                    const introspectionQuery = graphql.getIntrospectionQuery();
                    const introspectionResult = graphql.introspectionFromSchema(schema);
                    
                    // Create output filename (e.g., schema.graphql -> schema.json)
                    const baseName = path.basename(filePath, ext);
                    const outputPath = path.join(path.dirname(absolutePath), `${baseName}.json`);
                    
                    // Save introspection JSON file
                    await fs.writeFile(outputPath, JSON.stringify(introspectionResult, null, 2));
                    console.error(`✅ Introspection JSON saved to: ${outputPath}`);
                    
                    return introspectionResult;
                } catch (error) {
                    throw new Error(
                        `Failed to convert GraphQL SDL to introspection JSON: ${error.message}\n` +
                        `Please check that your SDL syntax is valid.`
                    );
                }
            }

            // Parse JSON or YAML content
            return this._parseSchemaContent(content, schemaType);
        } catch (error) {
            // Re-throw with original message if it's already formatted
            if (error.message.includes('GraphQL SDL') || error.message.includes('Schema file not found')) {
                throw error;
            }
            throw new Error(`Failed to read schema file: ${error.message}`);
        }
    }
// FIXME  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TTNWQ1JnPT06NmNkM2Q5Yzg=

    /**
     * Parse schema content (JSON/YAML) - Internal method used by _fetchSchema and _readSchemaFromFile
     * Note: SDL conversion is handled in _readSchemaFromFile before reaching this method
     */
    _parseSchemaContent(content, schemaType) {
        const trimmedContent = content.trim();
        
        try {
            // Try JSON first
            return JSON.parse(content);
        } catch (jsonError) {
            // Try YAML if available
            if (this.yaml) {
                try {
                    return this.yaml.parse(content);
                } catch (yamlError) {
                    throw new Error(`Failed to parse as JSON or YAML: ${jsonError.message}`);
                }
            } else {
                throw new Error(`Failed to parse as JSON: ${jsonError.message}`);
            }
        }
    }

    /**
     * Validate endpoints by making actual API calls
     */
    async _validateEndpoints(testPlan, baseUrl, options) {
        if (!options.validateEndpoints) {
            return testPlan;
        }

        console.error(`\n🔍 Validating endpoints (sample size: ${options.validationSampleSize})...`);
        
        const validationResults = {
            totalValidated: 0,
            successful: 0,
            failed: 0,
            results: []
        };

        // Collect all scenarios that can be validated (happy path scenarios)
        const validatableScenarios = [];
        for (const section of testPlan.sections) {
            if (section.scenarios) {
                for (const scenario of section.scenarios) {
                    // Only validate happy path scenarios (not error scenarios)
                    if (scenario.title && scenario.title.includes('Happy Path')) {
                        validatableScenarios.push({ section, scenario });
                    }
                }
            }
        }

        // Determine how many to validate
        const sampleSize = options.validationSampleSize === -1 
            ? validatableScenarios.length 
            : Math.min(options.validationSampleSize, validatableScenarios.length);

        // Select sample scenarios (evenly distributed)
        const step = Math.floor(validatableScenarios.length / sampleSize) || 1;
        const selectedScenarios = [];
        for (let i = 0; i < validatableScenarios.length && selectedScenarios.length < sampleSize; i += step) {
            selectedScenarios.push(validatableScenarios[i]);
        }

        // Validate each selected scenario
        for (const { section, scenario } of selectedScenarios) {
            const validationResult = await this._validateEndpoint(scenario, baseUrl, options);
            validationResults.totalValidated++;
            
            if (validationResult.success) {
                validationResults.successful++;
                scenario.validation = validationResult;
            } else {
                validationResults.failed++;
                scenario.validation = validationResult;
            }
            
            validationResults.results.push({
                endpoint: `${scenario.method} ${scenario.endpoint}`,
                ...validationResult
            });

            console.error(`  ${validationResult.success ? '✅' : '❌'} ${scenario.method} ${scenario.endpoint} - ${validationResult.success ? 'SUCCESS' : validationResult.error}`);
        }

        // Add validation summary to test plan
        testPlan.validationSummary = validationResults;
        
        console.error(`\n✨ Validation complete: ${validationResults.successful}/${validationResults.totalValidated} successful\n`);
        
        return testPlan;
    }

    /**
     * Validate a single endpoint by making an actual API call
     */
    async _validateEndpoint(scenario, baseUrl, options) {
        try {
            // Construct full URL
            const endpoint = scenario.endpoint || '';
            // Replace path parameters with sample values
            const processedEndpoint = endpoint.replace(/{([^}]+)}/g, (match, param) => {
                // Use common test IDs
                if (param.toLowerCase().includes('id')) return '1';
                return 'test-value';
            });
            
            const fullUrl = baseUrl.replace(/\/$/, '') + processedEndpoint;
            
            // Prepare headers - ensure Content-Type is set for requests with body
            const headers = { ...(scenario.headers || {}) };
            if (scenario.data && !headers['Content-Type'] && !headers['content-type']) {
                headers['Content-Type'] = 'application/json';
            }
            
            // Prepare request
            const requestData = {
                method: scenario.method || 'GET',
                url: fullUrl,
                headers: headers,
                expect: scenario.expect
            };
            
            // Only add data for methods that support request body
            if (['POST', 'PUT', 'PATCH'].includes(scenario.method) && scenario.data) {
                requestData.data = scenario.data;
            }
            
            // Add query parameters if present
            if (scenario.query) {
                requestData.query = scenario.query;
            }

            // Import api_request tool
            const ApiRequestTool = require('./api-request.js');
            const apiRequest = new ApiRequestTool();
            
            const startTime = Date.now();
            
            // Make the request with timeout
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Request timeout')), options.validationTimeout)
            );
            
            const requestPromise = apiRequest.execute(requestData);
            const result = await Promise.race([requestPromise, timeoutPromise]);
            
            const responseTime = Date.now() - startTime;

            if (result.success) {
                return {
                    success: true,
                    statusCode: result.statusCode,
                    responseTime: responseTime,
                    responseBody: result.body,
                    responseHeaders: result.headers
                };
            } else {
                return {
                    success: false,
                    error: result.error || 'Unknown error',
                    responseTime: responseTime
                };
            }
        } catch (error) {
            return {
                success: false,
                error: error.message || 'Validation failed',
                responseTime: 0
            };
        }
    }

    _detectSchemaType(schema) {
        if (schema.openapi) {
            return 'openapi';
        } else if (schema.swagger) {
            return 'swagger';
        } else if (schema.__schema || schema.data?.__schema) {
            return 'graphql';
        } else {
            throw new Error('Unable to detect schema type - must be OpenAPI/Swagger or GraphQL');
        }
    }

    async _generateOpenApiTestPlan(schema, options) {
        const baseUrl = options.apiBaseUrl || this._getBaseUrl(schema);
        const paths = schema.paths || {};
        const components = schema.components || {};
        const security = schema.security || [];

        const testPlan = {
            summary: {
                title: schema.info?.title || 'API Test Plan',
                version: schema.info?.version || '1.0.0',
                description: schema.info?.description || '',
                baseUrl: baseUrl,
                totalEndpoints: 0,
                totalScenarios: 0
            },
            sections: []
        };

        // Authentication section
        if (options.includeAuth && (security.length > 0 || components.securitySchemes)) {
            const authSection = this._generateAuthTestSection(components.securitySchemes, security);
            testPlan.sections.push(authSection);
            testPlan.summary.totalScenarios += authSection.scenarios.length;
        }

        // Endpoint sections
        for (const [path, pathItem] of Object.entries(paths)) {
            for (const [method, operation] of Object.entries(pathItem)) {
                if (['get', 'post', 'put', 'delete', 'patch', 'head', 'options'].includes(method.toLowerCase())) {
                    testPlan.summary.totalEndpoints++;
                    
                    const endpointSection = this._generateEndpointTestSection(
                        path, method.toUpperCase(), operation, components, options
                    );
                    
                    testPlan.sections.push(endpointSection);
                    testPlan.summary.totalScenarios += endpointSection.scenarios.length;
                }
            }
        }

        // Security testing section
        if (options.includeSecurity) {
            const securitySection = this._generateSecurityTestSection(schema, options);
            testPlan.sections.push(securitySection);
            testPlan.summary.totalScenarios += securitySection.scenarios.length;
        }

        // Integration testing section
        if (options.testCategories.includes('integration')) {
            const integrationSection = this._generateIntegrationTestSection(schema, options);
            testPlan.sections.push(integrationSection);
            testPlan.summary.totalScenarios += integrationSection.scenarios.length;
        }

        // Validate endpoints if requested
        if (options.validateEndpoints && baseUrl) {
            await this._validateEndpoints(testPlan, baseUrl, options);
        }

        testPlan.content = this._generateMarkdownContent(testPlan);
        return testPlan;
    }

    _getBaseUrl(schema) {
        if (schema.servers && schema.servers.length > 0) {
            return schema.servers[0].url;
        } else if (schema.host) {
            const scheme = schema.schemes ? schema.schemes[0] : 'https';
            const basePath = schema.basePath || '';
            return `${scheme}://${schema.host}${basePath}`;
        }
        return 'https://api.example.com';
    }

    _generateAuthTestSection(securitySchemes, security) {
        const scenarios = [];
        
        if (securitySchemes) {
            for (const [schemeName, scheme] of Object.entries(securitySchemes)) {
                switch (scheme.type) {
                    case 'http':
                        if (scheme.scheme === 'bearer') {
                            scenarios.push(this._generateBearerTokenScenarios(schemeName));
                        } else if (scheme.scheme === 'basic') {
                            scenarios.push(this._generateBasicAuthScenarios(schemeName));
                        }
                        break;
                    case 'apiKey':
                        scenarios.push(this._generateApiKeyScenarios(schemeName, scheme));
                        break;
                    case 'oauth2':
                        scenarios.push(this._generateOAuth2Scenarios(schemeName, scheme));
                        break;
                }
            }
        }

        return {
            title: 'Authentication Testing',
            description: 'Test various authentication mechanisms and security scenarios',
            scenarios: scenarios.flat()
        };
    }

    _generateBearerTokenScenarios(schemeName) {
        return [
            {
                title: `Valid ${schemeName} Token`,
                method: 'GET',
                endpoint: '/protected-endpoint',
                headers: {
                    'Authorization': 'Bearer {{valid_token}}'
                },
                expect: {
                    status: 200
                },
                description: 'Test access with valid bearer token'
            },
            {
                title: `Invalid ${schemeName} Token`,
                method: 'GET',
                endpoint: '/protected-endpoint',
                headers: {
                    'Authorization': 'Bearer invalid_token'
                },
                expect: {
                    status: 401
                },
                description: 'Test rejection of invalid bearer token'
            },
            {
                title: `Missing ${schemeName} Token`,
                method: 'GET',
                endpoint: '/protected-endpoint',
                headers: {},
                expect: {
                    status: 401
                },
                description: 'Test rejection when no authorization header provided'
            }
        ];
    }

    _generateBasicAuthScenarios(schemeName) {
        return [
            {
                title: `Valid ${schemeName} Credentials`,
                method: 'GET',
                endpoint: '/protected-endpoint',
                headers: {
                    'Authorization': 'Basic {{valid_basic_auth}}'
                },
                expect: {
                    status: 200
                },
                description: 'Test access with valid basic auth credentials'
            },
            {
                title: `Invalid ${schemeName} Credentials`,
                method: 'GET',
                endpoint: '/protected-endpoint',
                headers: {
                    'Authorization': 'Basic aW52YWxpZDppbnZhbGlk'
                },
                expect: {
                    status: 401
                },
                description: 'Test rejection of invalid basic auth credentials'
            }
        ];
    }

    _generateApiKeyScenarios(schemeName, scheme) {
        const location = scheme.in;
        const keyName = scheme.name;
        
        const scenarios = [
            {
                title: `Valid ${schemeName} API Key`,
                method: 'GET',
                endpoint: '/protected-endpoint',
                expect: {
                    status: 200
                },
                description: `Test access with valid API key in ${location}`
            },
            {
                title: `Invalid ${schemeName} API Key`,
                method: 'GET',
                endpoint: '/protected-endpoint',
                expect: {
                    status: 401
                },
                description: `Test rejection of invalid API key in ${location}`
            }
        ];

        // Add location-specific parameters
        scenarios.forEach(scenario => {
            if (location === 'header') {
                scenario.headers = scenario.headers || {};
                scenario.headers[keyName] = scenario.title.includes('Valid') ? '{{valid_api_key}}' : 'invalid_key';
            } else if (location === 'query') {
                scenario.query = scenario.query || {};
                scenario.query[keyName] = scenario.title.includes('Valid') ? '{{valid_api_key}}' : 'invalid_key';
            }
        });

        return scenarios;
    }

    _generateOAuth2Scenarios(schemeName, scheme) {
        return [
            {
                title: `OAuth2 Authorization Code Flow - ${schemeName}`,
                method: 'POST',
                endpoint: '/oauth/token',
                data: {
                    grant_type: 'authorization_code',
                    code: '{{auth_code}}',
                    client_id: '{{client_id}}',
                    client_secret: '{{client_secret}}'
                },
                expect: {
                    status: 200,
                    body: {
                        access_token: 'string',
                        token_type: 'Bearer'
                    }
                },
                description: 'Test OAuth2 token exchange'
            }
        ];
    }

    _generateEndpointTestSection(path, method, operation, components, options) {
        const scenarios = [];
        const operationName = operation.operationId || `${method.toLowerCase()}_${path.replace(/[^a-zA-Z0-9]/g, '_')}`;
        
        // Happy path scenario
        const happyPathScenario = {
            title: `${operationName} - Happy Path`,
            method: method,
            endpoint: path,
            description: operation.summary || operation.description || `Test successful ${method} request to ${path}`,
            expect: {
                status: this._getSuccessStatus(method, operation)
            }
        };

        // Add request body for POST/PUT/PATCH
        if (['POST', 'PUT', 'PATCH'].includes(method) && operation.requestBody) {
            happyPathScenario.data = this._generateSampleRequestData(operation.requestBody, components);
        }

        // Add query parameters
        if (operation.parameters) {
            const queryParams = operation.parameters.filter(p => p.in === 'query');
            if (queryParams.length > 0) {
                happyPathScenario.query = this._generateSampleQueryParams(queryParams, components);
            }

            const headerParams = operation.parameters.filter(p => p.in === 'header');
            if (headerParams.length > 0) {
                happyPathScenario.headers = this._generateSampleHeaders(headerParams, components);
            }
        }

        scenarios.push(happyPathScenario);

        // Error scenarios
        if (options.includeErrorHandling) {
            scenarios.push(...this._generateErrorScenarios(path, method, operation, components));
        }

        // Edge case scenarios
        if (options.testCategories.includes('edge-cases')) {
            scenarios.push(...this._generateEdgeCaseScenarios(path, method, operation, components));
        }

        return {
            title: `${method} ${path}`,
            description: operation.summary || operation.description || '',
            operationId: operationName,
            scenarios: scenarios
        };
    }

    _getSuccessStatus(method, operation) {
        if (operation.responses) {
            const successCodes = Object.keys(operation.responses).filter(code => 
                code.startsWith('2') && code !== 'default'
            );
            if (successCodes.length > 0) {
                return parseInt(successCodes[0]);
            }
        }

        // Default success codes by method
        switch (method) {
            case 'POST': return 201;
            case 'DELETE': return 204;
            default: return 200;
        }
    }

    _generateSampleRequestData(requestBody, components) {
        const content = requestBody.content;
        if (!content) {
            return {};
        }

        // Priority order for content type selection
        const contentTypes = Object.keys(content);
        let selectedContentType = null;
        let contentTypeCategory = null;

        // 1. JSON types (highest priority for structured data)
        selectedContentType = contentTypes.find(ct => {
            const lower = ct.toLowerCase();
            return lower === 'application/json' || 
                   lower.startsWith('application/json') || 
                   lower.startsWith('text/json') ||
                   lower.includes('+json') ||
                   lower.includes('json');
        });
        if (selectedContentType) contentTypeCategory = 'json';

        // 2. XML types
        if (!selectedContentType) {
            selectedContentType = contentTypes.find(ct => {
                const lower = ct.toLowerCase();
                return lower === 'application/xml' || 
                       lower === 'text/xml' ||
                       lower.startsWith('application/xml') || 
                       lower.startsWith('text/xml') ||
                       lower.includes('+xml') ||
                       lower.includes('xml');
            });
            if (selectedContentType) contentTypeCategory = 'xml';
        }

        // 3. Form data types
        if (!selectedContentType) {
            selectedContentType = contentTypes.find(ct => {
                const lower = ct.toLowerCase();
                return lower === 'application/x-www-form-urlencoded' ||
                       lower.startsWith('application/x-www-form-urlencoded');
            });
            if (selectedContentType) contentTypeCategory = 'form';
        }

        // 4. Multipart types
        if (!selectedContentType) {
            selectedContentType = contentTypes.find(ct => {
                const lower = ct.toLowerCase();
                return lower === 'multipart/form-data' ||
                       lower.startsWith('multipart/form-data') ||
                       lower.startsWith('multipart/');
            });
            if (selectedContentType) contentTypeCategory = 'multipart';
        }

        // 5. Plain text
        if (!selectedContentType) {
            selectedContentType = contentTypes.find(ct => {
                const lower = ct.toLowerCase();
                return lower === 'text/plain' || lower.startsWith('text/plain');
            });
            if (selectedContentType) contentTypeCategory = 'text';
        }

        // 6. Binary/file types (image, audio, video, application/octet-stream, etc.)
        if (!selectedContentType) {
            selectedContentType = contentTypes.find(ct => {
                const lower = ct.toLowerCase();
                return lower.startsWith('image/') || 
                       lower.startsWith('audio/') || 
                       lower.startsWith('video/') ||
                       lower === 'application/octet-stream' ||
                       lower === 'application/pdf' ||
                       lower === 'application/zip';
            });
            if (selectedContentType) contentTypeCategory = 'binary';
        }

        // 7. Fallback: use first available content type
        if (!selectedContentType && contentTypes.length > 0) {
            selectedContentType = contentTypes[0];
            contentTypeCategory = 'unknown';
        }

        // Generate sample data based on content type category
        if (selectedContentType && content[selectedContentType]?.schema) {
            const schema = content[selectedContentType].schema;
            
            switch (contentTypeCategory) {
                case 'json':
                    return this._generateSampleFromSchema(schema, components);
                
                case 'xml':
                    return this._generateXmlSample(schema, components);
                
                case 'form':
                case 'multipart':
                    return this._generateFormSample(schema, components);
                
                case 'text':
                    return this._generateTextSample(schema, components);
                
                case 'binary':
                    return this._generateBinarySample(schema, selectedContentType);
                
                default:
                    // Unknown content type - try to generate from schema anyway
                    return this._generateSampleFromSchema(schema, components);
            }
        }

        return {};
    }

    /**
     * Generate sample XML data from schema
     */
    _generateXmlSample(schema, components) {
        // For XML, we return a simplified representation
        // In practice, this would be converted to XML format
        const data = this._generateSampleFromSchema(schema, components);
        return {
            _comment: 'XML representation',
            _contentType: 'application/xml',
            data: data
        };
    }

    /**
     * Generate sample form data from schema
     */
    _generateFormSample(schema, components) {
        // Form data is typically key-value pairs
        const data = this._generateSampleFromSchema(schema, components);
        
        // Flatten nested objects for form data
        if (typeof data === 'object' && !Array.isArray(data)) {
            return data;
        }
        
        return { value: data };
    }

    /**
     * Generate sample plain text from schema
     */
    _generateTextSample(schema, components) {
        if (schema.example !== undefined) return schema.example;
        if (schema.default !== undefined) return schema.default;
        
        // If schema has properties, try to generate structured text
        if (schema.type === 'object' || schema.properties) {
            const data = this._generateSampleFromSchema(schema, components);
            return JSON.stringify(data, null, 2);
        }
        
        // For simple types, return a plain text value
        return 'Sample plain text content';
    }

    /**
     * Generate sample binary/file data representation
     */
    _generateBinarySample(schema, contentType) {
        const lower = contentType.toLowerCase();
        
        if (lower.startsWith('image/')) {
            return {
                _comment: 'Binary file upload',
                _contentType: contentType,
                _file: 'sample-image.jpg',
                _description: 'Upload image file here'
            };
        }
        
        if (lower.startsWith('audio/')) {
            return {
                _comment: 'Binary file upload',
                _contentType: contentType,
                _file: 'sample-audio.mp3',
                _description: 'Upload audio file here'
            };
        }
        
        if (lower.startsWith('video/')) {
            return {
                _comment: 'Binary file upload',
                _contentType: contentType,
                _file: 'sample-video.mp4',
                _description: 'Upload video file here'
            };
        }
        
        if (lower === 'application/pdf') {
            return {
                _comment: 'Binary file upload',
                _contentType: contentType,
                _file: 'sample-document.pdf',
                _description: 'Upload PDF file here'
            };
        }
        
        // Generic binary data
        return {
            _comment: 'Binary file upload',
            _contentType: contentType,
            _file: 'sample-file.bin',
            _description: 'Upload binary file here'
        };
    }

    _generateSampleQueryParams(queryParams, components) {
        const params = {};
        queryParams.forEach(param => {
            if (param.required || param.schema) {
                params[param.name] = this._generateSampleValue(param.schema || { type: 'string' }, components);
            }
        });
        return params;
    }

    _generateSampleHeaders(headerParams, components) {
        const headers = {};
        headerParams.forEach(param => {
            if (param.required || param.schema) {
                headers[param.name] = this._generateSampleValue(param.schema || { type: 'string' }, components);
            }
        });
        return headers;
    }

    _generateSampleFromSchema(schema, components, fieldName = '') {
        if (schema.$ref) {
            const refPath = schema.$ref.replace('#/', '').split('/');
            // If the refPath starts with 'components', skip it since we're already in components
            const pathToResolve = refPath[0] === 'components' ? refPath.slice(1) : refPath;
            const resolvedSchema = this._resolveRef(components, pathToResolve);
            return this._generateSampleFromSchema(resolvedSchema, components, fieldName);
        }

        switch (schema.type) {
            case 'object':
                const obj = {};
                if (schema.properties) {
                    // Include ALL properties for complete test coverage
                    // Tests should demonstrate all available fields, not randomly exclude them
                    Object.entries(schema.properties).forEach(([key, propSchema]) => {
                        obj[key] = this._generateSampleFromSchema(propSchema, components, key);
                    });
                }
                return obj;
            
            case 'array':
                return [this._generateSampleFromSchema(schema.items, components, fieldName)];
            
            default:
                return this._generateSampleValue(schema, components, fieldName);
        }
    }

    _generateSampleValue(schema, components, fieldName = '') {
        // Use explicit examples or defaults if provided
        if (schema.example !== undefined) return schema.example;
        if (schema.default !== undefined) return schema.default;

        switch (schema.type) {
            case 'string':
                return this._generateStringValue(schema, fieldName);
            
            case 'number':
            case 'integer':
                return this._generateNumericValue(schema, fieldName);
            
            case 'boolean':
                return this._generateBooleanValue(schema, fieldName);
            
            default:
                return 'value';
        }
    }

    /**
     * Generate realistic string values based on field name and format
     */
    _generateStringValue(schema, fieldName = '') {
        const lowerName = fieldName.toLowerCase();
        
        // Use faker.js if available for high-quality data with graceful error handling
        if (faker) {
            try {
                // Email addresses
                if (schema.format === 'email' || lowerName.match(/email|e-mail|emailaddress/)) {
                    return faker.internet.email();
                }
                
                // Names
                if (lowerName.match(/^(first|given)name$/)) return faker.person.firstName();
                if (lowerName.match(/^(last|sur|family)name$/)) return faker.person.lastName();
                if (lowerName.match(/^(full|complete)?name$/)) return faker.person.fullName();
                if (lowerName.match(/^(middle|mid)name$/)) return faker.person.middleName();
                
                // Contact information
                if (lowerName.match(/phone|mobile|tel|telephone/)) return faker.phone.number();
                if (lowerName.match(/address|street|addr/)) return faker.location.streetAddress();
                if (lowerName.match(/city|town/)) return faker.location.city();
                if (lowerName.match(/state|province|region/)) return faker.location.state();
                if (lowerName.match(/country/)) return faker.location.country();
                if (lowerName.match(/zip|postal|postcode/)) return faker.location.zipCode();
                
                // Internet & Technology
                if (schema.format === 'uri' || schema.format === 'url' || lowerName.match(/url|uri|link|website/)) {
                    return faker.internet.url();
                }
                if (lowerName.match(/username|login|handle/)) return faker.internet.username();
                if (lowerName.match(/password|passwd|pwd/)) return faker.internet.password({ length: Math.max(schema.minLength || 8, 12) });
                if (lowerName.match(/ip|ipaddress/)) return faker.internet.ip();
                if (lowerName.match(/domain/)) return faker.internet.domainName();
                if (lowerName.match(/avatar|image|photo|picture/)) return faker.image.avatar();
                
                // Business
                if (lowerName.match(/company|organization|org/)) return faker.company.name();
                if (lowerName.match(/job|position|title|role/)) return faker.person.jobTitle();
                if (lowerName.match(/department|dept/)) return faker.commerce.department();
                
                // Identifiers
                if (lowerName.match(/uuid|guid/)) return faker.string.uuid();
                if (lowerName.match(/^id$|id$/)) return faker.string.alphanumeric(10);  // Matches 'id', 'productId', 'userId', etc.
                if (lowerName.match(/token|key|secret/)) return faker.string.alphanumeric(32);
                
                // Content
                if (lowerName.match(/description|desc|summary/)) return faker.lorem.sentence();
                if (lowerName.match(/comment|note|remark/)) return faker.lorem.paragraph();
                if (lowerName.match(/title|heading/)) return faker.lorem.words(3);
                if (lowerName.match(/tag|label/)) return faker.lorem.word();
                
                // Dates & Times
                if (schema.format === 'date') return faker.date.recent().toISOString().split('T')[0];
                if (schema.format === 'date-time' || lowerName.match(/date|time|timestamp|created|updated/)) {
                    return faker.date.recent().toISOString();
                }
            } catch (error) {
                // Graceful fallback: if faker fails for any reason, continue to built-in generation
                console.warn(`[ApiPlanner] Faker.js error for field "${fieldName}":`, error.message);
            }
        }
        
        // Fallback to built-in semantic detection
        // Email addresses
        if (schema.format === 'email' || lowerName.match(/email|e-mail|emailaddress/)) {
            return 'john.doe@example.com';
        }
        
        // Names
        if (lowerName.match(/^(first|given)name$/)) return 'John';
        if (lowerName.match(/^(last|sur|family)name$/)) return 'Doe';
        if (lowerName.match(/^(full|complete)?name$/)) return 'John Doe';
        if (lowerName.match(/^(middle|mid)name$/)) return 'Michael';
        
        // Contact information
        if (lowerName.match(/phone|mobile|tel|telephone/)) return '+1-555-0123';
        if (lowerName.match(/address|street|addr/)) return '123 Main Street';
        if (lowerName.match(/city|town/)) return 'New York';
        if (lowerName.match(/state|province|region/)) return 'NY';
        if (lowerName.match(/country/)) return 'United States';
        if (lowerName.match(/zip|postal|postcode/)) return '10001';
        
        // Internet & Technology
        if (schema.format === 'uri' || schema.format === 'url' || lowerName.match(/url|uri|link|website/)) {
            return 'https://example.com';
        }
        if (lowerName.match(/username|login|handle/)) return 'johndoe';
        if (lowerName.match(/password|passwd|pwd/)) {
            const minLen = schema.minLength || 8;
            return 'SecurePass123!'.substring(0, Math.max(minLen, 14));
        }
        if (lowerName.match(/ip|ipaddress/)) return '192.168.1.1';
        if (lowerName.match(/domain/)) return 'example.com';
        if (lowerName.match(/avatar|image|photo|picture/)) return 'https://example.com/avatar.jpg';
        
        // Business
        if (lowerName.match(/company|organization|org/)) return 'Acme Corp';
        if (lowerName.match(/job|position|title|role/)) return 'Software Engineer';
        if (lowerName.match(/department|dept/)) return 'Engineering';
        
        // Identifiers
        if (lowerName.match(/uuid|guid/)) return '550e8400-e29b-41d4-a716-446655440000';
        if (lowerName.match(/^id$|id$/)) return 'abc123';  // Matches 'id', 'productId', 'userId', 'orderId', etc.
        if (lowerName.match(/token|key|secret/)) return 'sk_test_1234567890abcdef';
        
        // Content
        if (lowerName.match(/description|desc|summary/)) return 'This is a sample description';
        if (lowerName.match(/comment|note|remark/)) return 'This is a sample comment';
        if (lowerName.match(/title|heading/)) return 'Sample Title';
        if (lowerName.match(/tag|label/)) return 'sample-tag';
        if (lowerName.match(/code/)) return 'CODE123';
        if (lowerName.match(/status/)) return 'active';
        if (lowerName.match(/type|kind|category/)) return 'standard';
        
        // Dates & Times
        if (schema.format === 'date') return '2025-10-19';
        if (schema.format === 'date-time' || lowerName.match(/date|time|timestamp|created|updated/)) {
            return '2025-10-19T10:30:00Z';
        }
        
        // Colors
        if (lowerName.match(/color|colour/)) return '#3B82F6';
        
        // Enum values
        if (schema.enum && schema.enum.length > 0) {
            return schema.enum[0];
        }
        
        // Pattern-based generation
        if (schema.pattern) {
            // Simple pattern detection for common cases
            if (schema.pattern.includes('uuid')) return '550e8400-e29b-41d4-a716-446655440000';
            if (schema.pattern.includes('[0-9]')) return '123456';
        }
        
        // Length constraints
        if (schema.minLength || schema.maxLength) {
            const minLen = schema.minLength || 1;
            const maxLen = schema.maxLength || minLen + 10;
            const targetLen = Math.min(maxLen, Math.max(minLen, 10));
            return 'sample_value'.substring(0, targetLen).padEnd(targetLen, '_');
        }
        
        // Generic fallback
        return 'string_value';
    }

    /**
     * Generate realistic numeric values based on field name and constraints
     */
    _generateNumericValue(schema, fieldName = '') {
        const lowerName = fieldName.toLowerCase();
        const isInteger = schema.type === 'integer';
        
        // Use faker.js if available with graceful error handling
        if (faker) {
            try {
                if (lowerName.match(/age/)) return faker.number.int({ min: 18, max: 80 });
                if (lowerName.match(/price|cost|amount|total/)) return parseFloat(faker.commerce.price());
                if (lowerName.match(/quantity|qty|count/)) return faker.number.int({ min: 1, max: 100 });
                if (lowerName.match(/rating|score/)) return faker.number.float({ min: 1, max: 5, multipleOf: 0.1 });
                if (lowerName.match(/percentage|percent/)) return faker.number.int({ min: 0, max: 100 });
                if (lowerName.match(/year/)) return faker.date.recent().getFullYear();
                if (lowerName.match(/month/)) return faker.number.int({ min: 1, max: 12 });
                if (lowerName.match(/day/)) return faker.number.int({ min: 1, max: 31 });
                if (lowerName.match(/latitude|lat/)) return parseFloat(faker.location.latitude());
                if (lowerName.match(/longitude|lng|lon/)) return parseFloat(faker.location.longitude());
            } catch (error) {
                // Graceful fallback: if faker fails, continue to built-in generation
                console.warn(`[ApiPlanner] Faker.js error for numeric field "${fieldName}":`, error.message);
            }
        }
        
        // Built-in semantic detection
        if (lowerName.match(/age/)) return isInteger ? 25 : 25.0;
        if (lowerName.match(/price|cost|amount|total/)) return isInteger ? 1999 : 19.99;
        if (lowerName.match(/quantity|qty|count/)) return isInteger ? 10 : 10.0;
        if (lowerName.match(/rating|score/)) return isInteger ? 4 : 4.5;
        if (lowerName.match(/percentage|percent/)) return isInteger ? 75 : 75.0;
        if (lowerName.match(/year/)) return 2025;
        if (lowerName.match(/month/)) return 10;
        if (lowerName.match(/day/)) return 19;
        if (lowerName.match(/hour/)) return 10;
        if (lowerName.match(/minute|min/)) return 30;
        if (lowerName.match(/second|sec/)) return 45;
        if (lowerName.match(/latitude|lat/)) return 40.7128;
        if (lowerName.match(/longitude|lng|lon/)) return -74.0060;
        if (lowerName.match(/^id$/)) return isInteger ? 12345 : 12345.0;
        
        // Use schema constraints
        if (schema.minimum !== undefined) {
            const min = schema.minimum;
            const max = schema.maximum !== undefined ? schema.maximum : min + 100;
            const value = min + (max - min) / 2;
            return isInteger ? Math.round(value) : parseFloat(value.toFixed(2));
        }
        
        if (schema.maximum !== undefined) {
            const max = schema.maximum;
            const value = max / 2;
            return isInteger ? Math.round(value) : parseFloat(value.toFixed(2));
        }
        
        // Default values
        return isInteger ? 123 : 123.45;
    }

    /**
     * Generate realistic boolean values based on field name
     */
    _generateBooleanValue(schema, fieldName = '') {
        const lowerName = fieldName.toLowerCase();
        
        // Semantic detection for booleans
        if (lowerName.match(/^is|^has|^can|^should|^will|^does/)) {
            // Common patterns suggest true
            if (lowerName.match(/active|enabled|verified|confirmed|published/)) return true;
            // Common patterns suggest false
            if (lowerName.match(/deleted|disabled|suspended|banned|archived/)) return false;
        }
        
        // Default to true for convenience
        return true;
    }

    _resolveRef(components, refPath) {
        let current = components;
        for (const segment of refPath) {
            if (current && current[segment]) {
                current = current[segment];
            } else {
                return {};
            }
        }
        return current;
    }

    _generateErrorScenarios(path, method, operation, components) {
        const scenarios = [];

        // 400 Bad Request scenarios
        if (['POST', 'PUT', 'PATCH'].includes(method)) {
            scenarios.push({
                title: `${operation.operationId || method} - Invalid Request Data`,
                method: method,
                endpoint: path,
                data: { invalid: 'data' },
                expect: {
                    status: 400
                },
                description: 'Test validation of malformed request data'
            });
        }

        // 404 Not Found scenarios
        if (path.includes('{')) {
            scenarios.push({
                title: `${operation.operationId || method} - Resource Not Found`,
                method: method,
                endpoint: path.replace(/{[^}]+}/g, '99999'),
                expect: {
                    status: 404
                },
                description: 'Test behavior with non-existent resource ID'
            });
        }

        return scenarios;
    }

    _generateEdgeCaseScenarios(path, method, operation, components) {
        const scenarios = [];

        // Large payload testing
        if (['POST', 'PUT', 'PATCH'].includes(method)) {
            scenarios.push({
                title: `${operation.operationId || method} - Large Payload`,
                method: method,
                endpoint: path,
                data: { largeField: 'x'.repeat(10000) },
                expect: {
                    status: [200, 201, 413] // Accept success or payload too large
                },
                description: 'Test handling of large request payloads'
            });
        }

        // Empty/null data testing
        if (['POST', 'PUT', 'PATCH'].includes(method)) {
            scenarios.push({
                title: `${operation.operationId || method} - Empty Payload`,
                method: method,
                endpoint: path,
                data: {},
                expect: {
                    status: [200, 201, 400] // May succeed or fail validation
                },
                description: 'Test handling of empty request payload'
            });
        }

        return scenarios;
    }

    _generateSecurityTestSection(schema, options) {
        const scenarios = [
            {
                title: 'SQL Injection Protection',
                method: 'GET',
                endpoint: '/vulnerable-endpoint',
                query: {
                    search: "'; DROP TABLE users; --"
                },
                expect: {
                    status: [200, 400]
                },
                description: 'Test protection against SQL injection attacks'
            },
            {
                title: 'XSS Protection',
                method: 'POST',
                endpoint: '/user-input',
                data: {
                    content: '<script>alert("xss")</script>'
                },
                expect: {
                    status: [200, 201, 400]
                },
                description: 'Test protection against XSS attacks'
            },
            {
                title: 'CSRF Protection',
                method: 'POST',
                endpoint: '/sensitive-action',
                headers: {
                    'Origin': 'https://malicious-site.com'
                },
                expect: {
                    status: [403, 400]
                },
                description: 'Test CSRF protection mechanisms'
            }
        ];

        return {
            title: 'Security Testing',
            description: 'Test security measures and vulnerability protections',
            scenarios: scenarios
        };
    }

    _generateIntegrationTestSection(schema, options) {
        const scenarios = [
            {
                title: 'End-to-End User Workflow',
                method: 'CHAIN',
                description: 'Test complete user journey from registration to data manipulation',
                chain: [
                    {
                        name: 'register',
                        method: 'POST',
                        endpoint: '/auth/register',
                        data: {
                            email: 'integration@test.com',
                            password: 'TestPassword123'
                        },
                        expect: { status: 201 },
                        extract: { userId: 'id' }
                    },
                    {
                        name: 'login',
                        method: 'POST',
                        endpoint: '/auth/login',
                        data: {
                            email: 'integration@test.com',
                            password: 'TestPassword123'
                        },
                        expect: { status: 200 },
                        extract: { token: 'token' }
                    },
                    {
                        name: 'create_resource',
                        method: 'POST',
                        endpoint: '/resources',
                        headers: {
                            'Authorization': 'Bearer {{ login.token }}'
                        },
                        data: {
                            title: 'Integration Test Resource',
                            ownerId: '{{ register.userId }}'
                        },
                        expect: { status: 201 },
                        extract: { resourceId: 'id' }
                    },
                    {
                        name: 'verify_resource',
                        method: 'GET',
                        endpoint: '/resources/{{ create_resource.resourceId }}',
                        headers: {
                            'Authorization': 'Bearer {{ login.token }}'
                        },
                        expect: { 
                            status: 200,
                            body: { title: 'Integration Test Resource' }
                        }
                    }
                ]
            }
        ];

        return {
            title: 'Integration Testing',
            description: 'Test complete workflows and cross-service interactions',
            scenarios: scenarios
        };
    }

    // ============================================================================
    // GRAPHQL SUPPORT - GENERIC IMPLEMENTATION
    // ============================================================================
    
    /**
     * Standard GraphQL introspection query (works with ANY GraphQL endpoint)
     * Follows GraphQL specification: https://spec.graphql.org/October2021/#sec-Introspection
     */
    _getGraphQLIntrospectionQuery() {
        return `
            query IntrospectionQuery {
                __schema {
                    queryType { name }
                    mutationType { name }
                    subscriptionType { name }
                    types {
                        kind
                        name
                        description
                        fields(includeDeprecated: true) {
                            name
                            description
                            args {
                                name
                                description
                                type { ...TypeRef }
                                defaultValue
                            }
                            type { ...TypeRef }
                            isDeprecated
                            deprecationReason
                        }
                        inputFields {
                            name
                            description
                            type { ...TypeRef }
                            defaultValue
                        }
                        interfaces { ...TypeRef }
                        enumValues(includeDeprecated: true) {
                            name
                            description
                            isDeprecated
                            deprecationReason
                        }
                        possibleTypes { ...TypeRef }
                    }
                    directives {
                        name
                        description
                        locations
                        args {
                            name
                            description
                            type { ...TypeRef }
                            defaultValue
                        }
                    }
                }
            }
            
            fragment TypeRef on __Type {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                        ofType {
                            kind
                            name
                            ofType {
                                kind
                                name
                                ofType {
                                    kind
                                    name
                                }
                            }
                        }
                    }
                }
            }
        `;
    }

    async _generateGraphQLTestPlan(schema, options) {
        // Parse schema (generic - works with any GraphQL schema)
        const parsedSchema = this._parseGraphQLSchema(schema);
        
        // Discover operations (generic)
        const operations = this._discoverGraphQLOperations(parsedSchema);
        
        const testPlan = {
            summary: {
                title: 'GraphQL API Test Plan',
                type: 'graphql',
                baseUrl: options.apiBaseUrl || 'https://graphql.example.com/graphql',
                totalQueries: operations.queries.length,
                totalMutations: operations.mutations.length,
                totalSubscriptions: operations.subscriptions.length,
                totalScenarios: 0,
                totalEndpoints: 1 // GraphQL typically has single endpoint
            },
            sections: []
        };
        
        // Generate test scenarios for queries (generic)
        for (const query of operations.queries) {
            const section = this._generateGraphQLQueryTestSection(query, parsedSchema, options);
            testPlan.sections.push(section);
            testPlan.summary.totalScenarios += section.scenarios.length;
        }
        
        // Generate test scenarios for mutations (generic)
        for (const mutation of operations.mutations) {
            const section = this._generateGraphQLMutationTestSection(mutation, parsedSchema, options);
            testPlan.sections.push(section);
            testPlan.summary.totalScenarios += section.scenarios.length;
        }
        
        // Generate test scenarios for subscriptions if requested
        if (options.testCategories.includes('subscriptions') && operations.subscriptions.length > 0) {
            for (const subscription of operations.subscriptions) {
                const section = this._generateGraphQLSubscriptionTestSection(subscription, parsedSchema, options);
                testPlan.sections.push(section);
                testPlan.summary.totalScenarios += section.scenarios.length;
            }
        }
        
        testPlan.content = this._generateMarkdownContent(testPlan);
        return testPlan;
    }
    
    /**
     * Parse GraphQL introspection result into usable structure
     * GENERIC - Works with any GraphQL schema following the spec
     */
    _parseGraphQLSchema(introspectionResult) {
        // Handle both direct introspection result and wrapped result
        const schemaData = introspectionResult.__schema || introspectionResult.data?.__schema;
        
        if (!schemaData) {
            throw new Error('Invalid GraphQL introspection result - missing __schema');
        }
        
        const schema = {
            queryType: schemaData.queryType?.name,
            mutationType: schemaData.mutationType?.name,
            subscriptionType: schemaData.subscriptionType?.name,
            types: {},
            directives: schemaData.directives || []
        };
        
        // Index all types by name (skip internal GraphQL types starting with __)
        for (const type of schemaData.types) {
            if (!type.name.startsWith('__')) {
                schema.types[type.name] = {
                    kind: type.kind,
                    name: type.name,
                    description: type.description,
                    fields: type.fields || [],
                    inputFields: type.inputFields || [],
                    enumValues: type.enumValues || [],
                    interfaces: type.interfaces || [],
                    possibleTypes: type.possibleTypes || []
                };
            }
        }
        
        return schema;
    }
    
    /**
     * Discover all queries, mutations, and subscriptions from schema
     * GENERIC - Extracts operations from any GraphQL schema
     */
    _discoverGraphQLOperations(schema) {
        const operations = {
            queries: [],
            mutations: [],
            subscriptions: []
        };
        
        // Find Query type operations
        if (schema.queryType && schema.types[schema.queryType]) {
            const queryType = schema.types[schema.queryType];
            operations.queries = (queryType.fields || []).map(field => ({
                name: field.name,
                description: field.description,
                args: field.args || [],
                returnType: field.type,
                isDeprecated: field.isDeprecated,
                deprecationReason: field.deprecationReason
            }));
        }
        
        // Find Mutation type operations
        if (schema.mutationType && schema.types[schema.mutationType]) {
            const mutationType = schema.types[schema.mutationType];
            operations.mutations = (mutationType.fields || []).map(field => ({
                name: field.name,
                description: field.description,
                args: field.args || [],
                returnType: field.type,
                isDeprecated: field.isDeprecated,
                deprecationReason: field.deprecationReason
            }));
        }
        
        // Find Subscription type operations
        if (schema.subscriptionType && schema.types[schema.subscriptionType]) {
            const subscriptionType = schema.types[schema.subscriptionType];
            operations.subscriptions = (subscriptionType.fields || []).map(field => ({
                name: field.name,
                description: field.description,
                args: field.args || [],
                returnType: field.type,
                isDeprecated: field.isDeprecated,
                deprecationReason: field.deprecationReason
            }));
        }
        
        return operations;
    }
    
    /**
     * Generate realistic value for GraphQL scalar type
     * GENERIC - Handles built-in scalars and custom scalars using field name semantics
     */
    _generateGraphQLScalarValue(scalarType, fieldName = '') {
        const scalarName = scalarType.name;
        
        // ===== BUILT-IN SCALARS (GraphQL Spec - these 5 are always present) =====
        switch (scalarName) {
            case 'String':
                return this._generateStringValue({ type: 'string' }, fieldName);
            
            case 'Int':
                return this._generateNumericValue({ type: 'integer' }, fieldName);
            
            case 'Float':
                return this._generateNumericValue({ type: 'number' }, fieldName);
            
            case 'Boolean':
                return this._generateBooleanValue({}, fieldName);
            
            case 'ID':
                // Generic ID generation
                if (faker) {
                    return faker.string.alphanumeric(16);
                }
                return `id_${Math.random().toString(36).substr(2, 9)}`;
        }
        
        // ===== COMMON CUSTOM SCALAR PATTERNS (Generic Detection) =====
        const lowerScalar = scalarName.toLowerCase();
        
        // Date/Time scalars (various naming conventions)
        if (lowerScalar.includes('date') || lowerScalar.includes('time')) {
            if (lowerScalar.includes('date') && !lowerScalar.includes('time')) {
                return this._generateStringValue({ format: 'date' }, fieldName);
            }
            return this._generateStringValue({ format: 'date-time' }, fieldName);
        }
        
        // URL/URI scalars
        if (lowerScalar.includes('url') || lowerScalar.includes('uri')) {
            return this._generateStringValue({ format: 'uri' }, fieldName);
        }
        
        // JSON scalars
        if (lowerScalar.includes('json')) {
            return { example: 'json_data' };
        }
        
        // Email scalars
        if (lowerScalar.includes('email')) {
            return this._generateStringValue({ format: 'email' }, fieldName);
        }
        
        // HTML/Markdown scalars
        if (lowerScalar.includes('html')) {
            return '<p>Sample HTML content</p>';
        }
        
        if (lowerScalar.includes('markdown')) {
            return '# Sample Markdown\n\nThis is sample content.';
        }
        
        // ===== FALLBACK: Use field name semantic analysis =====
        // This is the SECRET WEAPON - works for ANY custom scalar!
        // We analyze the field name to generate appropriate data
        return this._generateStringValue({ type: 'string' }, fieldName);
    }
    
    /**
     * Recursively generate sample data from GraphQL type
     * GENERIC - Handles all GraphQL type kinds with circular reference protection
     */
    _generateSampleFromGraphQLType(type, schema, fieldName = '', visited = new Set(), depth = 0) {
        // Prevent infinite recursion
        const MAX_DEPTH = 5;
        if (depth > MAX_DEPTH) {
            return null;
        }
        
        // Circular reference detection
        const typeKey = type.name ? `${type.name}_${fieldName}` : `${type.kind}_${fieldName}`;
        if (visited.has(typeKey)) {
            return null;
        }
        
        switch (type.kind) {
            case 'NON_NULL':
                // Unwrap non-null and continue
                return this._generateSampleFromGraphQLType(type.ofType, schema, fieldName, visited, depth);
            
            case 'LIST':
                // Generate array with 1-2 sample items
                visited.add(typeKey);
                const itemValue = this._generateSampleFromGraphQLType(type.ofType, schema, fieldName, visited, depth + 1);
                visited.delete(typeKey);
                return itemValue !== null ? [itemValue] : [];
            
            case 'SCALAR':
                return this._generateGraphQLScalarValue(type, fieldName);
            
            case 'ENUM':
                // Pick first enum value
                const enumType = schema.types[type.name];
                if (enumType?.enumValues && enumType.enumValues.length > 0) {
                    return enumType.enumValues[0].name;
                }
                return 'ENUM_VALUE';
            
            case 'OBJECT':
            case 'INPUT_OBJECT':
                visited.add(typeKey);
                const objValue = this._generateGraphQLObject(type, schema, visited, depth + 1);
                visited.delete(typeKey);
                return objValue;
            
            case 'INTERFACE':
                // For interfaces, generate fields from the interface itself
                visited.add(typeKey);
                const interfaceValue = this._generateGraphQLObject(type, schema, visited, depth + 1);
                visited.delete(typeKey);
                return interfaceValue;
            
            case 'UNION':
                // Pick first possible type
                const unionType = schema.types[type.name];
                if (unionType?.possibleTypes && unionType.possibleTypes.length > 0) {
                    const firstType = unionType.possibleTypes[0];
                    return this._generateSampleFromGraphQLType(firstType, schema, fieldName, visited, depth + 1);
                }
                return null;
            
            default:
                return null;
        }
    }
    
    /**
     * Generate sample object with all fields
     * GENERIC - Works with any GraphQL object type
     */
    _generateGraphQLObject(type, schema, visited, depth) {
        const typeDefinition = schema.types[type.name];
        if (!typeDefinition) {
            return {};
        }
        
        const obj = {};
        const fields = typeDefinition.fields || typeDefinition.inputFields || [];
        
        // Limit fields at deep nesting levels to prevent bloat
        const maxFieldsAtDepth = depth > 3 ? 3 : (depth > 2 ? 5 : 10);
        const fieldsToGenerate = fields.slice(0, maxFieldsAtDepth);
        
        for (const field of fieldsToGenerate) {
            // Use field name for semantic data generation
            const value = this._generateSampleFromGraphQLType(
                field.type,
                schema,
                field.name,
                visited,
                depth
            );
            
            if (value !== null) {
                obj[field.name] = value;
            }
        }
        
        return obj;
    }
    
    /**
     * Build GraphQL query string with variables
     * GENERIC - Constructs valid GraphQL query/mutation syntax
     */
    _buildGraphQLQueryString(operation, args, schema, operationType = 'query') {
        const operationName = this._capitalize(operation.name);
        
        // Build variable definitions
        const variableDefinitions = [];
        const argumentsList = [];
        
        for (const arg of args) {
            const varName = arg.name;
            const typeString = this._getGraphQLTypeString(arg.type);
            variableDefinitions.push(`$${varName}: ${typeString}`);
            argumentsList.push(`${arg.name}: $${varName}`);
        }
        
        // Build field selection (simplified - select first level fields)
        const returnType = this._unwrapType(operation.returnType);
        const fields = this._buildFieldSelection(returnType, schema, 0);
        
        // Construct query string
        let queryString = operationType;
        if (variableDefinitions.length > 0) {
            queryString += ` ${operationName}(${variableDefinitions.join(', ')})`;
        } else {
            queryString += ` ${operationName}`;
        }
        
        queryString += ' {\n';
        if (argumentsList.length > 0) {
            queryString += `  ${operation.name}(${argumentsList.join(', ')}) `;
        } else {
            queryString += `  ${operation.name} `;
        }
        queryString += fields;
        queryString += '\n}';
        
        return queryString;
    }
    
    /**
     * Build field selection for GraphQL query
     * GENERIC - Selects appropriate fields based on return type
     */
    _buildFieldSelection(type, schema, depth = 0) {
        const MAX_DEPTH = 2;
        if (depth > MAX_DEPTH) {
            return '';
        }
        
        const typeDefinition = schema.types[type.name];
        if (!typeDefinition || !typeDefinition.fields || typeDefinition.fields.length === 0) {
            return '';
        }
        
        let selection = '{\n';
        const indent = '  '.repeat(depth + 2);
        
        // Select up to 5 fields to keep queries manageable
        const fieldsToSelect = typeDefinition.fields.slice(0, 5);
        
        for (const field of fieldsToSelect) {
            const fieldType = this._unwrapType(field.type);
            const fieldTypeDefinition = schema.types[fieldType.name];
            
            // If field is scalar or enum, just select it
            if (!fieldTypeDefinition || fieldType.kind === 'SCALAR' || fieldType.kind === 'ENUM') {
                selection += `${indent}${field.name}\n`;
            } else if (fieldType.kind === 'OBJECT' && depth < MAX_DEPTH) {
                // If field is object, recursively build selection
                const subSelection = this._buildFieldSelection(fieldType, schema, depth + 1);
                if (subSelection) {
                    selection += `${indent}${field.name} ${subSelection}`;
                } else {
                    selection += `${indent}${field.name}\n`;
                }
            }
        }
        
        selection += '  '.repeat(depth + 1) + '}';
        return selection;
    }
    
    /**
     * Get GraphQL type string (e.g., "String!", "[ID!]!")
     * GENERIC - Constructs type strings following GraphQL syntax
     */
    _getGraphQLTypeString(type) {
        if (type.kind === 'NON_NULL') {
            return this._getGraphQLTypeString(type.ofType) + '!';
        }
        if (type.kind === 'LIST') {
            return '[' + this._getGraphQLTypeString(type.ofType) + ']';
        }
        return type.name;
    }
    
    /**
     * Unwrap type to get base type (remove NON_NULL and LIST wrappers)
     */
    _unwrapType(type) {
        if (type.kind === 'NON_NULL' || type.kind === 'LIST') {
            return this._unwrapType(type.ofType);
        }
        return type;
    }
    
    /**
     * Capitalize first letter
     */
    _capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    /**
     * Generate test section for GraphQL query
     * GENERIC - Creates test scenarios for any GraphQL query operation
     */
    _generateGraphQLQueryTestSection(query, schema, options) {
        const scenarios = [];
        
        // Happy path scenario
        const happyPathScenario = {
            title: `${query.name} - Happy Path`,
            method: 'POST',
            endpoint: '/graphql',
            description: query.description || `Test successful execution of ${query.name} query`,
            data: {
                query: this._buildGraphQLQueryString(query, query.args, schema, 'query'),
                variables: this._generateGraphQLVariables(query.args, schema)
            },
            headers: {
                'Content-Type': 'application/json'
            },
            expect: {
                status: 200,
                body: {
                    data: {
                        [query.name]: this._generateExpectedGraphQLResponse(query.returnType, schema)
                    }
                }
            }
        };
        
        if (options.includeAuth) {
            happyPathScenario.headers['Authorization'] = 'Bearer {{auth_token}}';
        }
        
        scenarios.push(happyPathScenario);
        
        // Error scenarios
        if (options.includeErrorHandling) {
            // Missing required arguments
            if (query.args.some(arg => arg.type.kind === 'NON_NULL')) {
                scenarios.push({
                    title: `${query.name} - Missing Required Arguments`,
                    method: 'POST',
                    endpoint: '/graphql',
                    description: 'Test error handling when required arguments are missing',
                    data: {
                        query: this._buildGraphQLQueryString(query, query.args, schema, 'query'),
                        variables: {}
                    },
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    expect: {
                        status: 200,
                        body: {
                            errors: [
                                {
                                    message: 'string'
                                }
                            ]
                        }
                    }
                });
            }
            
            // Invalid field selection
            scenarios.push({
                title: `${query.name} - Invalid Field Selection`,
                method: 'POST',
                endpoint: '/graphql',
                description: 'Test error handling for invalid field in query',
                data: {
                    query: `query { ${query.name} { invalidField } }`,
                    variables: this._generateGraphQLVariables(query.args, schema)
                },
                headers: {
                    'Content-Type': 'application/json'
                },
                expect: {
                    status: 200,
                    body: {
                        errors: [
                            {
                                message: 'string'
                            }
                        ]
                    }
                }
            });
        }
        
        // Authentication error
        if (options.includeAuth) {
            scenarios.push({
                title: `${query.name} - Unauthorized Access`,
                method: 'POST',
                endpoint: '/graphql',
                description: 'Test access without authentication',
                data: {
                    query: this._buildGraphQLQueryString(query, query.args, schema, 'query'),
                    variables: this._generateGraphQLVariables(query.args, schema)
                },
                headers: {
                    'Content-Type': 'application/json'
                },
                expect: {
                    status: [200, 401],
                    body: {
                        errors: [
                            {
                                message: 'string'
                            }
                        ]
                    }
                }
            });
        }
        
        return {
            title: `Query: ${query.name}`,
            description: query.description || `Test cases for ${query.name} query`,
            scenarios: scenarios
        };
    }
    
    /**
     * Generate test section for GraphQL mutation
     * GENERIC - Creates test scenarios for any GraphQL mutation operation
     */
    _generateGraphQLMutationTestSection(mutation, schema, options) {
        const scenarios = [];
        
        // Happy path scenario
        const happyPathScenario = {
            title: `${mutation.name} - Happy Path`,
            method: 'POST',
            endpoint: '/graphql',
            description: mutation.description || `Test successful execution of ${mutation.name} mutation`,
            data: {
                query: this._buildGraphQLQueryString(mutation, mutation.args, schema, 'mutation'),
                variables: this._generateGraphQLVariables(mutation.args, schema)
            },
            headers: {
                'Content-Type': 'application/json'
            },
            expect: {
                status: 200,
                body: {
                    data: {
                        [mutation.name]: this._generateExpectedGraphQLResponse(mutation.returnType, schema)
                    }
                }
            }
        };
        
        if (options.includeAuth) {
            happyPathScenario.headers['Authorization'] = 'Bearer {{auth_token}}';
        }
        
        scenarios.push(happyPathScenario);
        
        // Error scenarios
        if (options.includeErrorHandling) {
            // Invalid input data
            scenarios.push({
                title: `${mutation.name} - Invalid Input Data`,
                method: 'POST',
                endpoint: '/graphql',
                description: 'Test error handling with invalid input data',
                data: {
                    query: this._buildGraphQLQueryString(mutation, mutation.args, schema, 'mutation'),
                    variables: this._generateInvalidGraphQLVariables(mutation.args, schema)
                },
                headers: {
                    'Content-Type': 'application/json'
                },
                expect: {
                    status: 200,
                    body: {
                        errors: [
                            {
                                message: 'string'
                            }
                        ]
                    }
                }
            });
        }
        
        // Authorization error for mutations
        if (options.includeAuth) {
            scenarios.push({
                title: `${mutation.name} - Unauthorized Mutation`,
                method: 'POST',
                endpoint: '/graphql',
                description: 'Test mutation without proper authorization',
                data: {
                    query: this._buildGraphQLQueryString(mutation, mutation.args, schema, 'mutation'),
                    variables: this._generateGraphQLVariables(mutation.args, schema)
                },
                headers: {
                    'Content-Type': 'application/json'
                },
                expect: {
                    status: [200, 401, 403],
                    body: {
                        errors: [
                            {
                                message: 'string'
                            }
                        ]
                    }
                }
            });
        }
        
        return {
            title: `Mutation: ${mutation.name}`,
            description: mutation.description || `Test cases for ${mutation.name} mutation`,
            scenarios: scenarios
        };
    }
    
    /**
     * Generate test section for GraphQL subscription
     * GENERIC - Creates test scenarios for any GraphQL subscription operation
     */
    _generateGraphQLSubscriptionTestSection(subscription, schema, options) {
        const scenarios = [];
        
        // Happy path scenario
        const happyPathScenario = {
            title: `${subscription.name} - Happy Path`,
            method: 'POST',
            endpoint: '/graphql',
            description: subscription.description || `Test successful subscription to ${subscription.name}`,
            data: {
                query: this._buildGraphQLQueryString(subscription, subscription.args, schema, 'subscription'),
                variables: this._generateGraphQLVariables(subscription.args, schema)
            },
            headers: {
                'Content-Type': 'application/json'
            },
            expect: {
                status: 200,
                body: {
                    data: {
                        [subscription.name]: this._generateExpectedGraphQLResponse(subscription.returnType, schema)
                    }
                }
            }
        };
        
        if (options.includeAuth) {
            happyPathScenario.headers['Authorization'] = 'Bearer {{auth_token}}';
        }
        
        scenarios.push(happyPathScenario);
        
        return {
            title: `Subscription: ${subscription.name}`,
            description: subscription.description || `Test cases for ${subscription.name} subscription`,
            scenarios: scenarios
        };
    }
    
    /**
     * Generate variables object for GraphQL operation
     * GENERIC - Creates realistic variable values based on argument types
     */
    _generateGraphQLVariables(args, schema) {
        const variables = {};
        
        for (const arg of args) {
            const argType = this._unwrapType(arg.type);
            variables[arg.name] = this._generateSampleFromGraphQLType(argType, schema, arg.name, new Set(), 0);
        }
        
        return variables;
    }
    
    /**
     * Generate invalid variables for error testing
     * GENERIC - Creates intentionally invalid data for negative testing
     */
    _generateInvalidGraphQLVariables(args, schema) {
        const variables = {};
        
        for (const arg of args) {
            const argType = this._unwrapType(arg.type);
            
            // Generate wrong type of data based on expected type
            if (argType.kind === 'SCALAR') {
                switch (argType.name) {
                    case 'String':
                        variables[arg.name] = 12345; // Wrong type
                        break;
                    case 'Int':
                    case 'Float':
                        variables[arg.name] = 'not_a_number'; // Wrong type
                        break;
                    case 'Boolean':
                        variables[arg.name] = 'not_a_boolean'; // Wrong type
                        break;
                    case 'ID':
                        variables[arg.name] = { invalid: 'object' }; // Wrong type
                        break;
                    default:
                        variables[arg.name] = null;
                }
            } else {
                variables[arg.name] = null;
            }
        }
        
        return variables;
    }
    
    /**
     * Generate expected response structure for GraphQL operation
     * GENERIC - Creates expected response based on return type
     */
    _generateExpectedGraphQLResponse(returnType, schema) {
        const unwrappedType = this._unwrapType(returnType);
        return this._generateSampleFromGraphQLType(unwrappedType, schema, '', new Set(), 0);
    }

    _generateMarkdownContent(testPlan) {
        let markdown = `# ${testPlan.summary.title}\n\n`;
        
        markdown += `## API Overview\n\n`;
        markdown += `${testPlan.summary.description}\n\n`;
        markdown += `- **Base URL**: \`${testPlan.summary.baseUrl}\`\n`;
        markdown += `- **Version**: ${testPlan.summary.version}\n`;
        markdown += `- **Total Endpoints**: ${testPlan.summary.totalEndpoints}\n`;
        markdown += `- **Total Test Scenarios**: ${testPlan.summary.totalScenarios}\n`;
        
        // Add validation summary if available
        if (testPlan.validationSummary) {
            const vs = testPlan.validationSummary;
            markdown += `\n### 🔍 Validation Summary\n\n`;
            markdown += `- **Endpoints Validated**: ${vs.totalValidated}\n`;
            markdown += `- **✅ Successful**: ${vs.successful}\n`;
            markdown += `- **❌ Failed**: ${vs.failed}\n`;
            markdown += `- **Success Rate**: ${vs.totalValidated > 0 ? Math.round((vs.successful / vs.totalValidated) * 100) : 0}%\n`;
        }
        
        markdown += `\n`;

        testPlan.sections.forEach((section, index) => {
            markdown += `## ${index + 1}. ${section.title}\n\n`;
            if (section.description) {
                markdown += `${section.description}\n\n`;
            }

            section.scenarios.forEach((scenario, scenarioIndex) => {
                markdown += `### ${index + 1}.${scenarioIndex + 1} ${scenario.title}\n`;
                markdown += `**Endpoint:** \`${scenario.method} ${scenario.endpoint}\`\n\n`;
                
                if (scenario.description) {
                    markdown += `**Description:** ${scenario.description}\n\n`;
                }

                if (scenario.headers) {
                    markdown += `**Headers:**\n\`\`\`json\n${JSON.stringify(scenario.headers, null, 2)}\n\`\`\`\n\n`;
                }

                if (scenario.query) {
                    markdown += `**Query Parameters:**\n\`\`\`json\n${JSON.stringify(scenario.query, null, 2)}\n\`\`\`\n\n`;
                }

                if (scenario.data) {
                    markdown += `**Request Body:**\n\`\`\`json\n${JSON.stringify(scenario.data, null, 2)}\n\`\`\`\n\n`;
                }

                if (scenario.expect) {
                    markdown += `**Expected Response:**\n`;
                    markdown += `- Status Code: ${Array.isArray(scenario.expect.status) ? 
                        scenario.expect.status.join(' or ') : scenario.expect.status}\n`;
                    if (scenario.expect.body) {
                        markdown += `- Response Body:\n\`\`\`json\n${JSON.stringify(scenario.expect.body, null, 2)}\n\`\`\`\n`;
                    }
                    markdown += `\n`;
                }

                // Add validation results if available
                if (scenario.validation) {
                    const val = scenario.validation;
                    markdown += `**${val.success ? '✅' : '❌'} Validation Result:**\n`;
                    if (val.success) {
                        markdown += `- Status: SUCCESS\n`;
                        markdown += `- Status Code: ${val.statusCode}\n`;
                        markdown += `- Response Time: ${val.responseTime}ms\n`;
                        if (val.responseBody) {
                            markdown += `- Actual Response Body:\n\`\`\`json\n${JSON.stringify(val.responseBody, null, 2)}\n\`\`\`\n`;
                        }
                    } else {
                        markdown += `- Status: FAILED\n`;
                        markdown += `- Error: ${val.error}\n`;
                    }
                    markdown += `\n`;
                }

                if (scenario.chain) {
                    markdown += `**Request Chain:**\n`;
                    scenario.chain.forEach((step, stepIndex) => {
                        markdown += `${stepIndex + 1}. **${step.name}**: \`${step.method} ${step.endpoint}\`\n`;
                        if (step.extract) {
                            markdown += `   - Extract: ${Object.entries(step.extract).map(([k,v]) => `${k} from ${v}`).join(', ')}\n`;
                        }
                    });
                    markdown += `\n`;
                }

                markdown += `---\n\n`;
            });
        });

        return markdown;
    }

    async _saveTestPlan(testPlan, outputPath) {
        const dir = this.path.dirname(outputPath);
        if (!this.fs.existsSync(dir)) {
            this.fs.mkdirSync(dir, { recursive: true });
        }
        this.fs.writeFileSync(outputPath, testPlan.content, 'utf8');
    }
}

module.exports = ApiPlannerTool;
