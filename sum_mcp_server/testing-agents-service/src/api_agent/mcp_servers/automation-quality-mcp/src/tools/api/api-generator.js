

const ToolBase = require('../base/ToolBase');
const fs = require('fs');
const path = require('path');

// NEW: Import prompt orchestration system
const { generationPrompts, validationRules } = require('./prompts');

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

// Input schema for the API generator tool
const apiGeneratorInputSchema = z.object({
    testPlanPath: z.string().optional(),
    testPlanContent: z.string().optional(),
    outputFormat: z.enum(['playwright', 'postman', 'jest', 'all']).optional(),
    outputDir: z.string().optional(),
    sessionId: z.string().optional(),
    includeAuth: z.boolean().optional(),
    includeSetup: z.boolean().optional(),
    testFramework: z.enum(['jest', 'mocha', 'playwright-test']).optional(),
    baseUrl: z.string().optional(),
    
    // NEW: Language support (TypeScript is default)
    language: z.enum(['javascript', 'typescript']).optional(),
    
    // NEW: Project configuration (auto-detected by chatmode/Copilot)
    projectInfo: z.object({
        hasTypeScript: z.boolean().optional(),
        hasPlaywrightConfig: z.boolean().optional(),
        hasJestConfig: z.boolean().optional()
    }).optional()
});

/**
 * API Generator Tool - Generate executable tests from test plans using AI
 * 
 * Uses prompt orchestration system: Planning → AI Generation → Validation → Healing
 * Chat mode agents provide AI capabilities for code generation
 */
class ApiGeneratorTool extends ToolBase {
    static definition = {
        name: "api_generator",
        description: "Generate executable API tests (Playwright, Jest, Postman) from test plans using AI-powered code generation. Supports TypeScript and JavaScript. For best results, call api_project_setup tool FIRST to detect/configure framework and language preferences. Can generate tests for specific sections or entire test plans. Uses prompt orchestration for high-quality, validated code.",
        input_schema: {
            type: "object",
            properties: {
                testPlanPath: {
                    type: "string",
                    description: "File path to the test plan markdown file"
                },
                testPlanContent: {
                    type: "string",
                    description: "Direct test plan content as markdown string (use this for specific sections extracted from full plan)"
                },
                outputFormat: {
                    type: "string",
                    enum: ["playwright", "postman", "jest", "all"],
                    description: "Format for generated tests (default: all)"
                },
                outputDir: {
                    type: "string",
                    description: "Directory to save generated test files (default: ./tests)"
                },
                sessionId: {
                    type: "string",
                    description: "Session ID for tracking generated tests"
                },
                includeAuth: {
                    type: "boolean",
                    description: "Include authentication setup in generated tests (default: true)"
                },
                includeSetup: {
                    type: "boolean",
                    description: "Include test setup and teardown code (default: true)"
                },
                testFramework: {
                    type: "string",
                    enum: ["jest", "mocha", "playwright-test"],
                    description: "Test framework to use for generated tests (default: playwright-test for Playwright, jest for Jest)"
                },
                baseUrl: {
                    type: "string",
                    description: "Base URL for API endpoints (overrides test plan base URL)"
                },
                language: {
                    type: "string",
                    enum: ["javascript", "typescript"],
                    description: "Programming language for generated tests (default: typescript). TypeScript is recommended for modern projects."
                },
                projectInfo: {
                    type: "object",
                    description: "Auto-detected project configuration (passed by GitHub Copilot after detection)",
                    properties: {
                        hasTypeScript: {
                            type: "boolean",
                            description: "Whether project has TypeScript configuration (tsconfig.json exists)"
                        },
                        hasPlaywrightConfig: {
                            type: "boolean",
                            description: "Whether project has Playwright configuration"
                        },
                        hasJestConfig: {
                            type: "boolean",
                            description: "Whether project has Jest configuration"
                        }
                    }
                }
            },
            oneOf: [
                { required: ["testPlanPath"] },
                { required: ["testPlanContent"] }
            ]
        }
    };

    constructor() {
        super();
    }

    async execute(parameters) {
        try {
            const params = apiGeneratorInputSchema.parse(parameters);
            
            // Set defaults with TypeScript as default and ./tests as output directory
            const options = {
                outputFormat: params.outputFormat || 'all',
                outputDir: params.outputDir || './tests',
                sessionId: params.sessionId || `api-gen-${Date.now()}`,
                includeAuth: params.includeAuth !== false,
                includeSetup: params.includeSetup !== false,
                testFramework: params.testFramework || (params.outputFormat === 'playwright' ? 'playwright-test' : 'jest'),
                baseUrl: params.baseUrl,
                language: params.language || 'typescript',
                projectInfo: params.projectInfo || { hasTypeScript: false }
            };

            // Load test plan
            let testPlanContent;
            if (params.testPlanPath) {
                if (!fs.existsSync(params.testPlanPath)) {
                    throw new Error(`Test plan file not found: ${params.testPlanPath}`);
                }
                testPlanContent = fs.readFileSync(params.testPlanPath, 'utf8');
            } else {
                testPlanContent = params.testPlanContent;
            }

            // Parse test plan
            const testPlan = this._parseTestPlan(testPlanContent);
            
            // Override base URL if provided
            if (options.baseUrl) {
                testPlan.baseUrl = options.baseUrl;
            }

            // Ensure output directory exists
            if (!fs.existsSync(options.outputDir)) {
                fs.mkdirSync(options.outputDir, { recursive: true });
            }
// @ts-expect-error  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVZjeE9BPT06MzYwMDI2ZTg=

            // ═══════════════════════════════════════════════════════════════
            // NEW: Prepare AI Generation Tasks (Prompt Orchestration)
            // ═══════════════════════════════════════════════════════════════
            // NOTE: Prompts include STRICT instructions to generate ONLY requested test files.
            // AI models should NOT create README, SUMMARY, GUIDE, or any extra documentation
            // files unless explicitly requested by the user.
            // See generation-prompts.js for file generation restrictions.
            // Safety net validation is in orchestrator.js (_validateSingleFileOutput).
            
            const generationTasks = [];
            const generatedFiles = [];

            // Generate tasks based on output format
            if (options.outputFormat === 'playwright' || options.outputFormat === 'all') {
                const playwrightTasks = this._preparePlaywrightGenerationTasks(testPlan, options);
                generationTasks.push(...playwrightTasks);
            }

            if (options.outputFormat === 'postman' || options.outputFormat === 'all') {
                // Postman uses JSON structure generation (keep existing logic)
                const postmanFile = await this._generatePostmanCollection(testPlan, options);
                generatedFiles.push(postmanFile);
            }

            if (options.outputFormat === 'jest' || options.outputFormat === 'all') {
                const jestTasks = this._prepareJestGenerationTasks(testPlan, options);
                generationTasks.push(...jestTasks);
            }

            // Prepare response
            const result = {
                success: true,
                message: generationTasks.length > 0 
                    ? "Test generation tasks prepared. Chat mode will generate code using AI."
                    : "API tests generated successfully",
                sessionId: options.sessionId,
                outputDir: options.outputDir,
                language: options.language,
                generatedFiles: generatedFiles,
                testPlan: {
                    title: testPlan.title,
                    totalSections: testPlan.sections.length,
                    totalScenarios: testPlan.sections.reduce((sum, section) => sum + section.scenarios.length, 0)
                },
                // New: Prompt orchestration data for chat mode
                generationTasks: generationTasks.length > 0 ? generationTasks : undefined,
                validationRules: generationTasks.length > 0 ? validationRules : undefined
            };

            // Add setup instructions if TypeScript is used but not configured
            if (options.language === 'typescript' && !options.projectInfo.hasTypeScript) {
                result.setupInstructions = this._generateTypeScriptSetupInstructions(options);
                
                // Also create SETUP.md file
                const setupFilePath = path.join(options.outputDir, 'SETUP.md');
                fs.writeFileSync(setupFilePath, result.setupInstructions.markdown);
                result.setupInstructions.filePath = setupFilePath;
            }
// eslint-disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVZjeE9BPT06MzYwMDI2ZTg=

            return result;

        } catch (error) {
            return {
                success: false,
                error: error.message,
                details: error.stack
            };
        }
    }

    _parseTestPlan(content) {
        const testPlan = {
            title: '',
            description: '',
            baseUrl: '',
            sections: [],
            isGraphQL: false  // NEW: Track if this is a GraphQL test plan
        };

        const lines = content.split('\n');
        let currentSection = null;
        let currentScenario = null;
        let inCodeBlock = false;
        let codeBlockType = '';
        let codeContent = '';
        let codeBlockContext = ''; // NEW: Track what the code block is for

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            const originalLine = lines[i]; // Keep original for context detection

            // Skip empty lines
            if (!line && !inCodeBlock) continue;

            // Detect context before code block (look back at previous lines)
            if (!inCodeBlock && i > 0 && line.startsWith('```')) {
                // Look at the previous line(s) to determine context
                for (let j = i - 1; j >= Math.max(0, i - 3); j--) {
                    const prevLine = lines[j].trim();
                    if (prevLine.includes('**Request Body:**') || prevLine.includes('Request Body:')) {
                        codeBlockContext = 'request';
                        break;
                    } else if (prevLine.includes('**Response Body:**') || prevLine.includes('Response:') || prevLine.includes('Expected Response:')) {
                        codeBlockContext = 'response';
                        break;
                    } else if (prevLine.includes('**Headers:**') || prevLine.includes('Headers:')) {
                        codeBlockContext = 'headers';
                        break;
                    } else if (prevLine.includes('**Query Parameters:**') || prevLine.includes('Query Parameters:')) {
                        codeBlockContext = 'query';
                        break;
                    } else if (prevLine.includes('**Path Parameters:**') || prevLine.includes('Path Parameters:')) {
                        codeBlockContext = 'path';
                        break;
                    }
                }
            }

            // Handle code blocks
            if (line.startsWith('```')) {
                if (!inCodeBlock) {
                    inCodeBlock = true;
                    codeBlockType = line.substring(3);
                    codeContent = '';
                } else {
                    inCodeBlock = false;
                    if (currentScenario && codeBlockType === 'json') {
                        this._addCodeBlockToScenario(currentScenario, codeContent, codeBlockContext);
                    }
                    codeBlockType = '';
                    codeContent = '';
                    codeBlockContext = ''; // Reset context
                }
                continue;
            }

            if (inCodeBlock) {
                codeContent += line + '\n';
                continue;
            }

            // Parse headers
            if (line.startsWith('# ')) {
                testPlan.title = line.substring(2);
            } else if (line.startsWith('## ') && line.includes('API Overview')) {
                // Skip overview section
                continue;
            } else if (line.startsWith('## ') && /^\d+\./.test(line.substring(3))) {
                // New test section
                const title = line.substring(3).replace(/^\d+\.\s*/, '');
                currentSection = {
                    title: title,
                    description: '',
                    scenarios: []
                };
                testPlan.sections.push(currentSection);
                currentScenario = null;
            } else if (line.startsWith('### ') && /^\d+\.\d+/.test(line.substring(4))) {
                // New test scenario
                if (currentSection) {
                    const title = line.substring(4).replace(/^\d+\.\d+\s*/, '');
                    currentScenario = {
                        title: title,
                        method: '',
                        endpoint: '',
                        headers: {},
                        query: {},
                        pathParams: {},
                        data: null,
                        expect: {},
                        description: '',
                        chain: null
                    };
                    currentSection.scenarios.push(currentScenario);
                }
            } else if (line.startsWith('**Base URL**:') || line.includes('Base URL')) {
                const urlMatch = line.match(/`([^`]+)`/);
                if (urlMatch) {
                    testPlan.baseUrl = urlMatch[1];
                }
            } else if (line.startsWith('**Endpoint:**') && currentScenario) {
                const endpointMatch = line.match(/`([A-Z]+)\s+([^`]+)`/);
                if (endpointMatch) {
                    currentScenario.method = endpointMatch[1];
                    currentScenario.endpoint = endpointMatch[2];
                }
            } else if (line.startsWith('**Description:**') && currentScenario) {
                currentScenario.description = line.substring(16);
            } else if (line.startsWith('- Status Code:') && currentScenario) {
                const statusMatch = line.match(/(\d+)/);
                if (statusMatch) {
                    currentScenario.expect.status = parseInt(statusMatch[1]);
                }
            }
        }
        
        // NEW: Detect if test plan is GraphQL-based
        testPlan.isGraphQL = testPlan.sections.some(section => 
            section.scenarios.some(scenario => scenario.isGraphQL)
        );

        return testPlan;
    }

    _addCodeBlockToScenario(scenario, content, context) {
        try {
            const data = JSON.parse(content);
// TODO  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVZjeE9BPT06MzYwMDI2ZTg=
            
            // NEW: Detect GraphQL structure
            if (data.query || data.mutation || data.subscription) {
                scenario.isGraphQL = true;
                scenario.graphql = {
                    query: data.query || data.mutation || data.subscription,
                    variables: data.variables || {}
                };
                // Also store in data for backward compatibility
                scenario.data = data;
                return;
            }
            
            if (context === 'request') {
                // This is request body data
                scenario.data = data;
            } else if (context === 'headers') {
                // These are headers
                scenario.headers = { ...scenario.headers, ...data };
            } else if (context === 'query') {
                // These are query parameters
                scenario.query = { ...scenario.query, ...data };
            } else if (context === 'path') {
                // These are path parameters (store for URL replacement)
                scenario.pathParams = { ...scenario.pathParams, ...data };
            } else if (context === 'response') {
                // This is expected response body
                scenario.expect.body = data;
            } else {
                // Legacy fallback: try to guess based on content
                if (data.headers) scenario.headers = { ...scenario.headers, ...data.headers };
                if (data.query) scenario.query = { ...scenario.query, ...data.query };
                if (data.expect) scenario.expect = { ...scenario.expect, ...data.expect };
                // If we can't determine context, assume it's request data
                if (!data.headers && !data.query && !data.expect) {
                    scenario.data = data;
                }
            }
        } catch (error) {
            // Ignore invalid JSON or comments in JSON blocks
            console.error(`⚠️  Could not parse JSON block: ${error.message}`);
        }
    }

    // NEW: Prepare Playwright test generation tasks for AI
    _preparePlaywrightGenerationTasks(testPlan, options) {
        const tasks = [];
        const isTS = options.language === 'typescript';
        const ext = isTS ? '.spec.ts' : '.spec.js';
        
        // Get appropriate generation prompts
        const prompts = generationPrompts.playwright;

        // Generate individual test files for each section (one file per scenario)
        testPlan.sections.forEach((section, sectionIndex) => {
            const sanitizedTitle = this._sanitizeFileName(`${sectionIndex + 1}-${section.title}`);
            const sectionFileName = `${sanitizedTitle}${ext}`;
            const targetFile = path.join(options.outputDir, sectionFileName);
            
            // Prepare context for this section
            const context = {
                testPlanTitle: testPlan.title,
                baseUrl: testPlan.baseUrl,
                sectionTitle: section.title,
                sectionIndex: sectionIndex + 1,
                totalSections: testPlan.sections.length,
                scenarios: section.scenarios.map(scenario => ({
                    title: scenario.title,
                    method: scenario.method,
                    endpoint: scenario.endpoint,
                    expectedStatus: scenario.expectedStatus,
                    requestBody: scenario.requestBody,
                    expectedBody: scenario.expectedBody,
                    steps: scenario.steps,
                    isGraphQL: scenario.isGraphQL,  // NEW: GraphQL flag
                    graphql: scenario.graphql        // NEW: GraphQL query/variables
                })),
                language: options.language,
                isTypeScript: isTS,
                sessionId: options.sessionId
            };

            // Create generation task
            tasks.push({
                type: 'playwright-section-test',
                targetFile: targetFile,
                systemPrompt: prompts.system,
                userPrompt: prompts.generateTest(context),
                context: context,
                validation: 'playwright-test' // Validation rule set to apply
            });
        });

        // Optionally generate main test file if there are multiple sections
        if (testPlan.sections.length > 1) {
            const mainTestFile = path.join(options.outputDir, `api-tests${ext}`);
            
            const mainContext = {
                testPlanTitle: testPlan.title,
                baseUrl: testPlan.baseUrl,
                sections: testPlan.sections.map((section, idx) => ({
                    title: section.title,
                    index: idx + 1,
                    scenarioCount: section.scenarios.length
                })),
                language: options.language,
                isTypeScript: isTS,
                sessionId: options.sessionId
            };

            tasks.push({
                type: 'playwright-main-test',
                targetFile: mainTestFile,
                systemPrompt: prompts.system,
                userPrompt: prompts.generateMainTest(mainContext),
                context: mainContext,
                validation: 'playwright-test'
            });
        }

        return tasks;
    }

    // NEW: Prepare Jest test generation tasks for AI
    _prepareJestGenerationTasks(testPlan, options) {
        const tasks = [];
        const isTS = options.language === 'typescript';
        const ext = isTS ? '.test.ts' : '.test.js';
        
        // Get appropriate generation prompts
        const prompts = generationPrompts.jest;

        // Generate individual test files for each section
        testPlan.sections.forEach((section, sectionIndex) => {
            const sanitizedTitle = this._sanitizeFileName(`${sectionIndex + 1}-${section.title}`);
            const sectionFileName = `${sanitizedTitle}${ext}`;
            const targetFile = path.join(options.outputDir, sectionFileName);
            
            // Prepare context for this section
            const context = {
                testPlanTitle: testPlan.title,
                baseUrl: testPlan.baseUrl,
                sectionTitle: section.title,
                sectionIndex: sectionIndex + 1,
                totalSections: testPlan.sections.length,
                scenarios: section.scenarios.map(scenario => ({
                    title: scenario.title,
                    method: scenario.method,
                    endpoint: scenario.endpoint,
                    expectedStatus: scenario.expectedStatus,
                    requestBody: scenario.requestBody,
                    expectedBody: scenario.expectedBody,
                    steps: scenario.steps,
                    isGraphQL: scenario.isGraphQL,  // NEW: GraphQL flag
                    graphql: scenario.graphql        // NEW: GraphQL query/variables
                })),
                language: options.language,
                isTypeScript: isTS,
                sessionId: options.sessionId
            };

            // Create generation task
            tasks.push({
                type: 'jest-section-test',
                targetFile: targetFile,
                systemPrompt: prompts.system,
                userPrompt: prompts.generateTest(context),
                context: context,
                validation: 'jest-test' // Validation rule set to apply
            });
        });

        // Optionally generate main test file if there are multiple sections
        if (testPlan.sections.length > 1) {
            const mainTestFile = path.join(options.outputDir, `api-tests${ext}`);
            
            const mainContext = {
                testPlanTitle: testPlan.title,
                baseUrl: testPlan.baseUrl,
                sections: testPlan.sections.map((section, idx) => ({
                    title: section.title,
                    index: idx + 1,
                    scenarioCount: section.scenarios.length
                })),
                language: options.language,
                isTypeScript: isTS,
                sessionId: options.sessionId
            };

            tasks.push({
                type: 'jest-main-test',
                targetFile: mainTestFile,
                systemPrompt: prompts.system,
                userPrompt: prompts.generateMainTest(mainContext),
                context: mainContext,
                validation: 'jest-test'
            });
        }

        return tasks;
    }

    async _generatePlaywrightTests(testPlan, options) {
        const files = [];
        const isTS = options.language === 'typescript';
        const ext = isTS ? '.spec.ts' : '.spec.js';
        const helperExt = isTS ? '.ts' : '.js';
        
        // Only generate main test file if there are multiple sections (full test plan)
        // Skip main file when generating section-specific tests
        if (testPlan.sections.length > 1) {
            const mainTestFile = path.join(options.outputDir, `api-tests${ext}`);
            const mainTestContent = this._generatePlaywrightMainTest(testPlan, options);
            fs.writeFileSync(mainTestFile, mainTestContent);
            files.push({ path: mainTestFile, type: 'playwright-test', language: options.language });
        }

        // Generate individual test files for each section (one file per scenario)
        testPlan.sections.forEach((section, sectionIndex) => {
            // Sanitize only the section title, then append the extension
            const sanitizedTitle = this._sanitizeFileName(`${sectionIndex + 1}-${section.title}`);
            const sectionFileName = `${sanitizedTitle}${ext}`;
            const sectionFilePath = path.join(options.outputDir, sectionFileName);
            const sectionContent = this._generatePlaywrightSectionTest(section, testPlan, options);
            fs.writeFileSync(sectionFilePath, sectionContent);
            files.push({ path: sectionFilePath, type: 'playwright-test', language: options.language });
        });
// FIXME  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVZjeE9BPT06MzYwMDI2ZTg=

        // Generate helper utilities - but only if they don't already exist
        // This prevents overwriting user customizations when generating additional sections
        const helpersFile = path.join(options.outputDir, `api-test-helpers${helperExt}`);
        const tsHelperFile = path.join(options.outputDir, 'api-test-helpers.ts');
        const jsHelperFile = path.join(options.outputDir, 'api-test-helpers.js');
        
        // NOTE: ApiTestHelper is no longer generated - tests use Playwright's request fixture directly
        // This simplifies tests and removes unnecessary abstraction layer
        // Keeping this comment for backwards compatibility reference
        console.error(`ℹ️  Skipping api-test-helpers generation - tests now use Playwright's request fixture directly`);

        return files;
    }

    _generatePlaywrightMainTest(testPlan, options) {
        const isTS = options.language === 'typescript';
        const imports = isTS 
            ? `import { test, expect } from '@playwright/test';`
            : `const { test, expect } = require('@playwright/test');`;

        return `// Generated API Tests for: ${testPlan.title}
// Generated by Automation Quality MCP Server
// Session ID: ${options.sessionId}
// Language: ${options.language}

${imports}

test.describe('${testPlan.title} - API Tests', () => {
  const baseUrl = '${testPlan.baseUrl}';

  ${testPlan.sections.map(section => `
  test.describe('${section.title}', () => {
    ${section.scenarios.map(scenario => `
    test('${scenario.title}', async ({ request }) => {
${this._generatePlaywrightScenarioTest(scenario, options, testPlan.baseUrl)}
    });`).join('\n')}
  });`).join('\n')}
});`;
    }

    _generatePlaywrightSectionTest(section, testPlan, options) {
        const isTS = options.language === 'typescript';
        const imports = isTS 
            ? `import { test, expect } from '@playwright/test';`
            : `const { test, expect } = require('@playwright/test');`;

        return `// Generated API Tests for: ${section.title}
// Generated by Automation Quality MCP Server
// Session ID: ${options.sessionId}
// Language: ${options.language}

${imports}

test.describe('${section.title}', () => {
  const baseUrl = '${testPlan.baseUrl}';

  ${section.scenarios.map(scenario => `
  test('${scenario.title}', async ({ request }) => {
${this._generatePlaywrightScenarioTest(scenario, options, testPlan.baseUrl)}
  });`).join('\n')}
});`;
    }

    _generatePlaywrightScenarioTest(scenario, options, baseUrl) {
        let testCode = '';

        if (scenario.chain) {
            // Handle chained requests
            testCode += '      // Chained API requests\n';
            testCode += '      const results = {};\n\n';
            
            scenario.chain.forEach((step, index) => {
                const stepUrl = step.endpoint.startsWith('http') 
                    ? `'${step.endpoint}'` 
                    : '`${baseUrl}' + step.endpoint + '`';
                
                testCode += `      // Step ${index + 1}: ${step.name}\n`;
                testCode += `      const ${step.name}Response = await request.${step.method.toLowerCase()}(${stepUrl}`;
                
                // Add options if needed
                const hasOptions = step.headers || step.data;
                if (hasOptions) {
                    testCode += `, {\n`;
                    if (step.headers && Object.keys(step.headers).length > 0) {
                        testCode += `        headers: ${JSON.stringify(step.headers, null, 8)},\n`;
                    }
                    if (step.data) {
                        testCode += `        data: ${JSON.stringify(step.data, null, 8)}\n`;
                    }
                    testCode += `      }`;
                }
                testCode += `);\n\n`;
                
                if (step.expect) {
                    testCode += `      expect(${step.name}Response.status()).toBe(${step.expect.status});\n`;
                    if (step.expect.body) {
                        testCode += `      const ${step.name}Data = await ${step.name}Response.json();\n`;
                        testCode += `      ${this._generatePlaywrightBodyValidation(`${step.name}Data`, step.expect.body)}\n`;
                    }
                }
                
                if (step.extract) {
                    testCode += `      const ${step.name}Data = await ${step.name}Response.json();\n`;
                    Object.entries(step.extract).forEach(([key, field]) => {
                        testCode += `      results['${step.name}.${key}'] = ${step.name}Data.${field};\n`;
                    });
                }
                testCode += '\n';
            });
        } else if (scenario.isGraphQL) {
            // NEW: Handle GraphQL requests
            const endpoint = scenario.endpoint || '/graphql';
            const fullUrl = endpoint.startsWith('http') ? endpoint : `\${baseUrl}${endpoint}`;
            
            testCode += `      // GraphQL Request\n`;
            testCode += `      const response = await request.post('${fullUrl}', {\n`;
            testCode += `        headers: ${JSON.stringify(scenario.headers, null, 8)},\n`;
            testCode += `        data: {\n`;
            testCode += `          query: \`${scenario.graphql.query.replace(/`/g, '\\`')}\`,\n`;
            if (scenario.graphql.variables && Object.keys(scenario.graphql.variables).length > 0) {
                testCode += `          variables: ${JSON.stringify(scenario.graphql.variables, null, 10)}\n`;
            }
            testCode += `        }\n`;
            testCode += `      });\n\n`;
            
            // Add validations for GraphQL
            if (scenario.expect.status) {
                testCode += `      expect(response.status()).toBe(${scenario.expect.status});\n`;
            }
            
            if (scenario.expect.body) {
                testCode += `      \n`;
                testCode += `      const responseData = await response.json();\n`;
                testCode += `      ${this._generateGraphQLPlaywrightValidation('responseData', scenario.expect.body)}\n`;
            }
        } else {
            // Single REST request
            let endpoint = scenario.endpoint;
            
            // Replace path parameters if any
            if (scenario.pathParams && Object.keys(scenario.pathParams).length > 0) {
                Object.entries(scenario.pathParams).forEach(([key, value]) => {
                    endpoint = endpoint.replace(`{${key}}`, value);
                });
            }
            
            // Build full URL
            const fullUrl = endpoint.startsWith('http') ? endpoint : `\${baseUrl}${endpoint}`;
            
            // Generate the request call
            testCode += `      const response = await request.${scenario.method.toLowerCase()}('${fullUrl}'`;
            
            // Add options if headers, params, or data exist
            const hasHeaders = Object.keys(scenario.headers).length > 0;
            const hasQuery = Object.keys(scenario.query).length > 0;
            const hasData = scenario.data && Object.keys(scenario.data).length > 0;
            
            if (hasHeaders || hasQuery || hasData) {
                testCode += `, {\n`;
                
                if (hasHeaders) {
                    testCode += `        headers: ${JSON.stringify(scenario.headers, null, 8)},\n`;
                }
                
                if (hasQuery) {
                    testCode += `        params: ${JSON.stringify(scenario.query, null, 8)},\n`;
                }
                
                if (hasData) {
                    testCode += `        data: ${JSON.stringify(scenario.data, null, 8)}\n`;
                }
                
                testCode += `      }`;
            }
            
            testCode += `);\n\n`;

            // Add validations
            if (scenario.expect.status) {
                testCode += `      expect(response.status()).toBe(${scenario.expect.status});\n`;
            }
            
            if (scenario.expect.body) {
                testCode += `      \n`;
                testCode += `      const responseData = await response.json();\n`;
                testCode += `      ${this._generatePlaywrightBodyValidation('responseData', scenario.expect.body)}\n`;
            }
        }

        return testCode;
    }

    _generatePlaywrightBodyValidation(dataVar, expectedBody) {
        let validation = '';
        
        if (typeof expectedBody === 'object') {
            Object.entries(expectedBody).forEach(([key, value]) => {
                if (typeof value === 'string' && value !== 'string' && value !== 'number') {
                    validation += `      expect(${dataVar}.${key}).toBe(${JSON.stringify(value)});\n`;
                } else if (value === 'string') {
                    validation += `      expect(typeof ${dataVar}.${key}).toBe('string');\n`;
                } else if (value === 'number') {
                    validation += `      expect(typeof ${dataVar}.${key}).toBe('number');\n`;
                } else {
                    validation += `      expect(${dataVar}).toHaveProperty('${key}');\n`;
                }
            });
        }
        
        return validation.trimEnd(); // Remove trailing newline
    }

    _generateGraphQLPlaywrightValidation(dataVar, expectedBody) {
        let validation = '';
        
        // GraphQL responses have either data or errors
        validation += `      // GraphQL response structure validation\n`;
        validation += `      expect(${dataVar}).toBeDefined();\n`;
        
        // Check if we're expecting success (data) or error (errors)
        if (expectedBody && typeof expectedBody === 'object') {
            if (expectedBody.data !== undefined) {
                validation += `      expect(${dataVar}).toHaveProperty('data');\n`;
                validation += `      expect(${dataVar}.errors).toBeUndefined();\n`;
                
                // Validate data structure
                if (typeof expectedBody.data === 'object' && expectedBody.data !== null) {
                    Object.entries(expectedBody.data).forEach(([key, value]) => {
                        validation += `      expect(${dataVar}.data).toHaveProperty('${key}');\n`;
                        
                        // Type checks for nested values
                        if (value === 'string') {
                            validation += `      expect(typeof ${dataVar}.data.${key}).toBe('string');\n`;
                        } else if (value === 'number') {
                            validation += `      expect(typeof ${dataVar}.data.${key}).toBe('number');\n`;
                        } else if (value === 'boolean') {
                            validation += `      expect(typeof ${dataVar}.data.${key}).toBe('boolean');\n`;
                        } else if (Array.isArray(value)) {
                            validation += `      expect(Array.isArray(${dataVar}.data.${key})).toBe(true);\n`;
                        } else if (typeof value === 'object' && value !== null) {
                            validation += `      expect(typeof ${dataVar}.data.${key}).toBe('object');\n`;
                        }
                    });
                }
            } else if (expectedBody.errors !== undefined) {
                validation += `      expect(${dataVar}).toHaveProperty('errors');\n`;
                validation += `      expect(Array.isArray(${dataVar}.errors)).toBe(true);\n`;
                validation += `      expect(${dataVar}.errors.length).toBeGreaterThan(0);\n`;
            }
        } else {
            // Generic validation when no specific expectation
            validation += `      // Verify GraphQL response has either data or errors\n`;
            validation += `      expect(${dataVar}.data !== undefined || ${dataVar}.errors !== undefined).toBe(true);\n`;
        }
        
        return validation.trimEnd();
    }

    _generatePlaywrightHelpers(testPlan, options) {
        const isTS = options.language === 'typescript';
        
        if (isTS) {
            // TypeScript version with types and interfaces
            return `// API Test Helpers
// Generated by Automation Quality MCP Server
// Language: TypeScript

import { APIResponse, APIRequestContext } from '@playwright/test';

interface RequestConfig {
  method: string;
  url: string;
  headers?: Record<string, string>;
  data?: any;
  params?: Record<string, string>;
}

export class ApiTestHelper {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async authenticate(): Promise<void> {
    // TODO: Implement authentication logic based on your API
    // This is a placeholder - customize based on your auth mechanism
    try {
      const response = await this.makeRequest({
        method: 'POST',
        url: '/auth/login',
        data: {
          email: process.env.TEST_EMAIL || 'test@example.com',
          password: process.env.TEST_PASSWORD || 'password123'
        }
      });
      
      if (response.ok()) {
        const data = await response.json();
        this.authToken = data.token || data.access_token;
      }
    } catch (error: any) {
      console.warn('Authentication failed:', error.message);
    }
  }

  async makeRequest(config: RequestConfig, templateData: Record<string, any> = {}): Promise<APIResponse> {
    const { method, url, headers = {}, data, params } = config;
    
    // Replace template variables
    let processedUrl = url;
    let processedData = data;
    let processedHeaders = { ...headers };
    
    if (templateData && Object.keys(templateData).length > 0) {
      processedUrl = this.replaceTemplateVars(url, templateData);
      if (data) {
        processedData = JSON.parse(this.replaceTemplateVars(JSON.stringify(data), templateData));
      }
      Object.keys(processedHeaders).forEach(key => {
        processedHeaders[key] = this.replaceTemplateVars(processedHeaders[key], templateData);
      });
    }

    // Add authentication if available
    if (this.authToken) {
      processedHeaders['Authorization'] = \`Bearer \${this.authToken}\`;
    }

    // Make the request
    const requestOptions: any = {
      method: method.toUpperCase(),
      headers: {
        'Content-Type': 'application/json',
        ...processedHeaders
      }
    };

    if (processedData) {
      requestOptions.data = processedData;
    }

    if (params) {
      requestOptions.params = params;
    }

    const fullUrl = processedUrl.startsWith('http') ? processedUrl : \`\${this.baseUrl}\${processedUrl}\`;
    
    const playwright = require('@playwright/test');
    const context = await playwright.request.newContext();
    
    // Use the appropriate HTTP method on the context
    const response = await context[requestOptions.method.toLowerCase()](fullUrl, requestOptions);
    
    return response;
  }

  replaceTemplateVars(text: string, data: Record<string, any>): string {
    let result = text;
    Object.entries(data).forEach(([key, value]) => {
      const regex = new RegExp(\`{{\\\\s*\${key}\\\\s*}}\`, 'g');
      result = result.replace(regex, String(value));
    });
    return result;
  }

  async cleanup(): Promise<void> {
    // TODO: Implement cleanup logic
    // e.g., delete test data, logout, etc.
  }
}`;
        } else {
            // JavaScript version (original)
            return `// API Test Helpers
// Generated by Automation Quality MCP Server
// Language: JavaScript

class ApiTestHelper {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.authToken = null;
  }

  async authenticate() {
    // TODO: Implement authentication logic based on your API
    // This is a placeholder - customize based on your auth mechanism
    try {
      const response = await this.makeRequest({
        method: 'POST',
        url: '/auth/login',
        data: {
          email: process.env.TEST_EMAIL || 'test@example.com',
          password: process.env.TEST_PASSWORD || 'password123'
        }
      });
      
      if (response.ok()) {
        const data = await response.json();
        this.authToken = data.token || data.access_token;
      }
    } catch (error) {
      console.warn('Authentication failed:', error.message);
    }
  }

  async makeRequest(config, templateData = {}) {
    const { method, url, headers = {}, data, params } = config;
    
    // Replace template variables
    let processedUrl = url;
    let processedData = data;
    let processedHeaders = { ...headers };
    
    if (templateData && Object.keys(templateData).length > 0) {
      processedUrl = this.replaceTemplateVars(url, templateData);
      if (data) {
        processedData = JSON.parse(this.replaceTemplateVars(JSON.stringify(data), templateData));
      }
      Object.keys(processedHeaders).forEach(key => {
        processedHeaders[key] = this.replaceTemplateVars(processedHeaders[key], templateData);
      });
    }

    // Add authentication if available
    if (this.authToken) {
      processedHeaders['Authorization'] = \`Bearer \${this.authToken}\`;
    }

    // Make the request
    const requestOptions = {
      method: method.toUpperCase(),
      headers: {
        'Content-Type': 'application/json',
        ...processedHeaders
      }
    };

    if (processedData) {
      requestOptions.data = processedData;
    }

    if (params) {
      requestOptions.params = params;
    }

    const fullUrl = processedUrl.startsWith('http') ? processedUrl : \`\${this.baseUrl}\${processedUrl}\`;
    
    const playwright = require('@playwright/test');
    const context = await playwright.request.newContext();
    
    // Use the appropriate HTTP method on the context
    const response = await context[requestOptions.method.toLowerCase()](fullUrl, requestOptions);
    
    return response;
  }

  replaceTemplateVars(text, data) {
    let result = text;
    Object.entries(data).forEach(([key, value]) => {
      const regex = new RegExp(\`{{\\\\s*\${key}\\\\s*}}\`, 'g');
      result = result.replace(regex, value);
    });
    return result;
  }

  async cleanup() {
    // TODO: Implement cleanup logic
    // e.g., delete test data, logout, etc.
  }
}

module.exports = { ApiTestHelper };`;
        }
    }

    async _generatePostmanCollection(testPlan, options) {
        const collection = {
            info: {
                name: testPlan.title,
                description: testPlan.description,
                schema: "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                _postman_id: this._generateUUID(),
                _postman_variable_scope: "environment"
            },
            item: [],
            event: [
                {
                    listen: "prerequest",
                    script: {
                        type: "text/javascript",
                        exec: [
                            "// Auto-generated pre-request script",
                            "pm.globals.set('timestamp', Date.now());"
                        ]
                    }
                }
            ],
            variable: [
                {
                    key: "baseUrl",
                    value: testPlan.baseUrl,
                    type: "string"
                }
            ]
        };

        // Convert each section to Postman folder
        testPlan.sections.forEach(section => {
            const folder = {
                name: section.title,
                description: section.description,
                item: []
            };

            section.scenarios.forEach(scenario => {
                if (scenario.chain) {
                    // Handle chained requests
                    scenario.chain.forEach(step => {
                        folder.item.push(this._createPostmanRequest(step, testPlan.baseUrl));
                    });
                } else {
                    folder.item.push(this._createPostmanRequest(scenario, testPlan.baseUrl));
                }
            });

            collection.item.push(folder);
        });

        const outputPath = path.join(options.outputDir, `${this._sanitizeFileName(testPlan.title)}.postman_collection.json`);
        fs.writeFileSync(outputPath, JSON.stringify(collection, null, 2));
        
        return { path: outputPath, type: 'postman-collection' };
    }

    _createPostmanRequest(scenario, baseUrl) {
        const request = {
            name: scenario.title || scenario.name,
            request: {
                method: scenario.method,
                header: [],
                url: {
                    raw: `{{baseUrl}}${scenario.endpoint}`,
                    host: ["{{baseUrl}}"],
                    path: scenario.endpoint.split('/').filter(p => p)
                }
            },
            event: []
        };

        // Add headers
        if (scenario.headers && Object.keys(scenario.headers).length > 0) {
            Object.entries(scenario.headers).forEach(([key, value]) => {
                request.request.header.push({
                    key: key,
                    value: value,
                    type: "text"
                });
            });
        }

        // Add query parameters
        if (scenario.query && Object.keys(scenario.query).length > 0) {
            request.request.url.query = Object.entries(scenario.query).map(([key, value]) => ({
                key: key,
                value: value
            }));
        }

        // Add request body
        if (scenario.data) {
            request.request.body = {
                mode: "raw",
                raw: JSON.stringify(scenario.data, null, 2),
                options: {
                    raw: {
                        language: "json"
                    }
                }
            };
        }

        // Add test script
        if (scenario.expect) {
            const testScript = this._generatePostmanTestScript(scenario.expect, scenario.extract);
            if (testScript.length > 0) {
                request.event.push({
                    listen: "test",
                    script: {
                        type: "text/javascript",
                        exec: testScript
                    }
                });
            }
        }

        return request;
    }

    _generatePostmanTestScript(expect, extract) {
        const tests = [];
        
        if (expect.status) {
            tests.push(`pm.test("Status code is ${expect.status}", function () {`);
            tests.push(`    pm.response.to.have.status(${expect.status});`);
            tests.push(`});`);
            tests.push("");
        }

        if (expect.body) {
            tests.push(`pm.test("Response body validation", function () {`);
            tests.push(`    const responseJson = pm.response.json();`);
            
            Object.entries(expect.body).forEach(([key, value]) => {
                if (typeof value === 'string' && (value === 'string' || value === 'number')) {
                    tests.push(`    pm.expect(typeof responseJson.${key}).to.eql('${value}');`);
                } else {
                    tests.push(`    pm.expect(responseJson).to.have.property('${key}');`);
                }
            });
            
            tests.push(`});`);
            tests.push("");
        }

        if (extract) {
            tests.push(`pm.test("Extract variables", function () {`);
            tests.push(`    const responseJson = pm.response.json();`);
            
            Object.entries(extract).forEach(([varName, field]) => {
                tests.push(`    pm.globals.set('${varName}', responseJson.${field});`);
            });
            
            tests.push(`});`);
        }

        return tests;
    }

    async _generateJestTests(testPlan, options) {
        const files = [];
        const isTS = options.language === 'typescript';
        const ext = isTS ? '.test.ts' : '.test.js';
        const utilExt = isTS ? '.ts' : '.js';
        
        // Generate main test file (Jest tests are typically in a single file)
        const mainTestFile = path.join(options.outputDir, `api${ext}`);
        const mainTestContent = this._generateJestMainTest(testPlan, options);
        fs.writeFileSync(mainTestFile, mainTestContent);
        files.push({ path: mainTestFile, type: 'jest-test', language: options.language });

        // Generate test utilities - but only if they don't already exist
        // This prevents overwriting user customizations when generating additional sections
        const utilsFile = path.join(options.outputDir, `test-utils${utilExt}`);
        const tsUtilsFile = path.join(options.outputDir, 'test-utils.ts');
        const jsUtilsFile = path.join(options.outputDir, 'test-utils.js');
        
        // Check if utils file exists (check both TS and JS to handle language switching)
        if (!fs.existsSync(tsUtilsFile) && !fs.existsSync(jsUtilsFile)) {
            // Safe to create - no existing utils file
            const utilsContent = this._generateJestUtils(testPlan, options);
            fs.writeFileSync(utilsFile, utilsContent);
            files.push({ 
                path: utilsFile, 
                type: 'jest-utils', 
                language: options.language,
                created: true
            });
        } else {
            // Utils file already exists - skip to preserve user customizations
            console.error(`ℹ️  Skipping ${path.basename(utilsFile)} - file already exists (preserving user customizations)`);
            files.push({ 
                path: fs.existsSync(utilsFile) ? utilsFile : (fs.existsSync(tsUtilsFile) ? tsUtilsFile : jsUtilsFile),
                type: 'jest-utils', 
                language: options.language,
                skipped: true,
                reason: 'File already exists - preserving user customizations'
            });
        }

        return files;
    }

    _generateJestMainTest(testPlan, options) {
        const isTS = options.language === 'typescript';
        const imports = isTS
            ? `import axios from 'axios';
import { ApiTestUtils } from './test-utils';`
            : `const axios = require('axios');
const { ApiTestUtils } = require('./test-utils');`;

        const typeAnnotation = isTS ? ': ApiTestUtils' : '';

        return `// Generated Jest API Tests for: ${testPlan.title}
// Generated by Automation Quality MCP Server
// Session ID: ${options.sessionId}
// Language: ${options.language}

${imports}

describe('${testPlan.title} API Tests', () => {
  let apiUtils${typeAnnotation};
  const baseUrl = '${testPlan.baseUrl}';

  beforeAll(async () => {
    apiUtils = new ApiTestUtils(baseUrl);
    ${options.includeAuth ? 'await apiUtils.authenticate();' : ''}
    console.log('Test suite initialized');
  });

  afterAll(async () => {
    await apiUtils.cleanup();
    console.log('Test suite completed');
  });

  ${testPlan.sections.map(section => `
  describe('${section.title}', () => {
    ${section.scenarios.map(scenario => `
    test('${scenario.title}', async () => {
      ${this._generateJestScenarioTest(scenario, options)}
    });`).join('\n')}
  });`).join('\n')}
});`;
    }

    _generateJestScenarioTest(scenario, options) {
        let testCode = '';

        if (scenario.chain) {
            // Handle chained requests
            testCode += '// Chained API requests\n';
            testCode += '      const results = {};\n\n';
            
            scenario.chain.forEach((step, index) => {
                testCode += `      // Step ${index + 1}: ${step.name}\n`;
                testCode += `      const ${step.name}Response = await apiUtils.makeRequest({\n`;
                testCode += `        method: '${step.method}',\n`;
                testCode += `        url: '${step.endpoint}',\n`;
                if (step.headers) testCode += `        headers: ${JSON.stringify(step.headers, null, 8)},\n`;
                if (step.data) testCode += `        data: ${JSON.stringify(step.data, null, 8)},\n`;
                testCode += `      }, results);\n\n`;
                
                if (step.expect) {
                    testCode += `      expect(${step.name}Response.status).toBe(${step.expect.status});\n`;
                    if (step.expect.body) {
                        testCode += `      ${this._generateJestBodyValidation(`${step.name}Response.data`, step.expect.body)}\n`;
                    }
                }
                
                if (step.extract) {
                    Object.entries(step.extract).forEach(([key, field]) => {
                        testCode += `      results['${step.name}.${key}'] = ${step.name}Response.data.${field};\n`;
                    });
                }
                testCode += '\n';
            });
        } else if (scenario.isGraphQL) {
            // NEW: Handle GraphQL requests
            const endpoint = scenario.endpoint || '/graphql';
            
            testCode += `      // GraphQL Request\n`;
            testCode += `      const response = await apiUtils.makeRequest({\n`;
            testCode += `        method: 'POST',\n`;
            testCode += `        url: '${endpoint}',\n`;
            testCode += `        headers: ${JSON.stringify(scenario.headers, null, 8)},\n`;
            testCode += `        data: {\n`;
            testCode += `          query: \`${scenario.graphql.query.replace(/`/g, '\\`')}\`,\n`;
            if (scenario.graphql.variables && Object.keys(scenario.graphql.variables).length > 0) {
                testCode += `          variables: ${JSON.stringify(scenario.graphql.variables, null, 10)}\n`;
            }
            testCode += `        }\n`;
            testCode += `      });\n\n`;

            // Add validations for GraphQL
            if (scenario.expect.status) {
                testCode += `      expect(response.status).toBe(${scenario.expect.status});\n`;
            }
            
            if (scenario.expect.body) {
                testCode += `      ${this._generateGraphQLJestValidation('response.data', scenario.expect.body)}\n`;
            }
        } else {
            // Single REST request
            testCode += `      const response = await apiUtils.makeRequest({\n`;
            testCode += `        method: '${scenario.method}',\n`;
            testCode += `        url: '${scenario.endpoint}',\n`;
            if (Object.keys(scenario.headers).length > 0) {
                testCode += `        headers: ${JSON.stringify(scenario.headers, null, 8)},\n`;
            }
            if (Object.keys(scenario.query).length > 0) {
                testCode += `        params: ${JSON.stringify(scenario.query, null, 8)},\n`;
            }
            if (scenario.data) {
                testCode += `        data: ${JSON.stringify(scenario.data, null, 8)},\n`;
            }
            testCode += `      });\n\n`;

            // Add validations
            if (scenario.expect.status) {
                testCode += `      expect(response.status).toBe(${scenario.expect.status});\n`;
            }
            
            if (scenario.expect.body) {
                testCode += `      ${this._generateJestBodyValidation('response.data', scenario.expect.body)}\n`;
            }
        }

        return testCode;
    }

    _generateJestBodyValidation(dataVar, expectedBody) {
        let validation = '';
        
        if (typeof expectedBody === 'object') {
            Object.entries(expectedBody).forEach(([key, value]) => {
                if (typeof value === 'string' && value !== 'string' && value !== 'number') {
                    validation += `      expect(${dataVar}.${key}).toBe(${JSON.stringify(value)});\n`;
                } else if (value === 'string') {
                    validation += `      expect(typeof ${dataVar}.${key}).toBe('string');\n`;
                } else if (value === 'number') {
                    validation += `      expect(typeof ${dataVar}.${key}).toBe('number');\n`;
                } else {
                    validation += `      expect(${dataVar}).toHaveProperty('${key}');\n`;
                }
            });
        }
        
        return validation;
    }

    _generateGraphQLJestValidation(dataVar, expectedBody) {
        let validation = '';
        
        // GraphQL responses have either data or errors
        validation += `      // GraphQL response structure validation\n`;
        validation += `      expect(${dataVar}).toBeDefined();\n`;
        
        // Check if we're expecting success (data) or error (errors)
        if (expectedBody && typeof expectedBody === 'object') {
            if (expectedBody.data !== undefined) {
                validation += `      expect(${dataVar}).toHaveProperty('data');\n`;
                validation += `      expect(${dataVar}.errors).toBeUndefined();\n`;
                
                // Validate data structure
                if (typeof expectedBody.data === 'object' && expectedBody.data !== null) {
                    Object.entries(expectedBody.data).forEach(([key, value]) => {
                        validation += `      expect(${dataVar}.data).toHaveProperty('${key}');\n`;
                        
                        // Type checks for nested values
                        if (value === 'string') {
                            validation += `      expect(typeof ${dataVar}.data.${key}).toBe('string');\n`;
                        } else if (value === 'number') {
                            validation += `      expect(typeof ${dataVar}.data.${key}).toBe('number');\n`;
                        } else if (value === 'boolean') {
                            validation += `      expect(typeof ${dataVar}.data.${key}).toBe('boolean');\n`;
                        } else if (Array.isArray(value)) {
                            validation += `      expect(Array.isArray(${dataVar}.data.${key})).toBe(true);\n`;
                        } else if (typeof value === 'object' && value !== null) {
                            validation += `      expect(typeof ${dataVar}.data.${key}).toBe('object');\n`;
                        }
                    });
                }
            } else if (expectedBody.errors !== undefined) {
                validation += `      expect(${dataVar}).toHaveProperty('errors');\n`;
                validation += `      expect(Array.isArray(${dataVar}.errors)).toBe(true);\n`;
                validation += `      expect(${dataVar}.errors.length).toBeGreaterThan(0);\n`;
            }
        } else {
            // Generic validation when no specific expectation
            validation += `      // Verify GraphQL response has either data or errors\n`;
            validation += `      expect(${dataVar}.data !== undefined || ${dataVar}.errors !== undefined).toBe(true);\n`;
        }
        
        return validation;
    }

    _generateJestUtils(testPlan, options) {
        const isTS = options.language === 'typescript';
        
        if (isTS) {
            // TypeScript version
            return `// Jest API Test Utilities
// Generated by Automation Quality MCP Server
// Language: TypeScript

import axios, { AxiosInstance, AxiosResponse } from 'axios';

interface RequestConfig {
  method: string;
  url: string;
  headers?: Record<string, string>;
  data?: any;
  params?: Record<string, string>;
}

export class ApiTestUtils {
  private baseUrl: string;
  private authToken: string | null = null;
  private client: AxiosInstance;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  async authenticate(): Promise<void> {
    // TODO: Implement authentication logic based on your API
    // This is a placeholder - customize based on your auth mechanism
    try {
      const response = await this.client.post('/auth/login', {
        email: process.env.TEST_EMAIL || 'test@example.com',
        password: process.env.TEST_PASSWORD || 'password123'
      });
      
      this.authToken = response.data.token || response.data.access_token;
      
      if (this.authToken) {
        this.client.defaults.headers.common['Authorization'] = \`Bearer \${this.authToken}\`;
      }
    } catch (error: any) {
      console.warn('Authentication failed:', error.message);
    }
  }

  async makeRequest(config: RequestConfig, templateData: Record<string, any> = {}): Promise<AxiosResponse> {
    const { method, url, headers = {}, data, params } = config;
    
    // Replace template variables
    let processedUrl = url;
    let processedData = data;
    let processedHeaders = { ...headers };
    
    if (templateData && Object.keys(templateData).length > 0) {
      processedUrl = this.replaceTemplateVars(url, templateData);
      if (data) {
        processedData = JSON.parse(this.replaceTemplateVars(JSON.stringify(data), templateData));
      }
      Object.keys(processedHeaders).forEach(key => {
        processedHeaders[key] = this.replaceTemplateVars(processedHeaders[key], templateData);
      });
    }

    try {
      const response = await this.client.request({
        method: method.toLowerCase(),
        url: processedUrl,
        headers: processedHeaders,
        data: processedData,
        params: params
      });
      
      return response;
    } catch (error: any) {
      if (error.response) {
        // Return error response for validation
        return error.response;
      }
      throw error;
    }
  }

  replaceTemplateVars(text: string, data: Record<string, any>): string {
    let result = text;
    Object.entries(data).forEach(([key, value]) => {
      const regex = new RegExp(\`{{\\\\s*\${key}\\\\s*}}\`, 'g');
      result = result.replace(regex, String(value));
    });
    return result;
  }

  async cleanup(): Promise<void> {
    // TODO: Implement cleanup logic
    // e.g., delete test data, logout, etc.
    if (this.authToken) {
      try {
        await this.client.post('/auth/logout');
      } catch (error: any) {
        console.warn('Logout failed:', error.message);
      }
    }
  }
}`;
        } else {
            // JavaScript version
            return `// Jest API Test Utilities
// Generated by Automation Quality MCP Server
// Language: JavaScript

const axios = require('axios');

class ApiTestUtils {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
    this.authToken = null;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  async authenticate() {
    // TODO: Implement authentication logic based on your API
    // This is a placeholder - customize based on your auth mechanism
    try {
      const response = await this.client.post('/auth/login', {
        email: process.env.TEST_EMAIL || 'test@example.com',
        password: process.env.TEST_PASSWORD || 'password123'
      });
      
      this.authToken = response.data.token || response.data.access_token;
      
      if (this.authToken) {
        this.client.defaults.headers.common['Authorization'] = \`Bearer \${this.authToken}\`;
      }
    } catch (error) {
      console.warn('Authentication failed:', error.message);
    }
  }

  async makeRequest(config, templateData = {}) {
    const { method, url, headers = {}, data, params } = config;
    
    // Replace template variables
    let processedUrl = url;
    let processedData = data;
    let processedHeaders = { ...headers };
    
    if (templateData && Object.keys(templateData).length > 0) {
      processedUrl = this.replaceTemplateVars(url, templateData);
      if (data) {
        processedData = JSON.parse(this.replaceTemplateVars(JSON.stringify(data), templateData));
      }
      Object.keys(processedHeaders).forEach(key => {
        processedHeaders[key] = this.replaceTemplateVars(processedHeaders[key], templateData);
      });
    }

    try {
      const response = await this.client.request({
        method: method.toLowerCase(),
        url: processedUrl,
        headers: processedHeaders,
        data: processedData,
        params: params
      });
      
      return response;
    } catch (error) {
      if (error.response) {
        // Return error response for validation
        return error.response;
      }
      throw error;
    }
  }

  replaceTemplateVars(text, data) {
    let result = text;
    Object.entries(data).forEach(([key, value]) => {
      const regex = new RegExp(\`{{\\\\s*\${key}\\\\s*}}\`, 'g');
      result = result.replace(regex, value);
    });
    return result;
  }

  async cleanup() {
    // TODO: Implement cleanup logic
    // e.g., delete test data, logout, etc.
    if (this.authToken) {
      try {
        await this.client.post('/auth/logout');
      } catch (error) {
        console.warn('Logout failed:', error.message);
      }
    }
  }
}

module.exports = { ApiTestUtils };`;
        }
    }

    _sanitizeFileName(name) {
        return name.toLowerCase()
                   .replace(/[^a-z0-9\s-]/g, '')
                   .replace(/\s+/g, '-')
                   .replace(/-+/g, '-')
                   .replace(/^-|-$/g, '');
    }

    _generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    _generateTypeScriptSetupInstructions(options) {
        const isPlaywright = options.outputFormat === 'playwright' || options.outputFormat === 'all';
        const isJest = options.outputFormat === 'jest' || options.outputFormat === 'all';
        
        const markdown = `# TypeScript Setup Guide

Your tests have been generated in TypeScript. Follow these steps to set up TypeScript in your project.

## Step 1: Install TypeScript and Dependencies

${isPlaywright ? `For Playwright tests:
\`\`\`bash
npm install -D typescript @types/node @playwright/test
\`\`\`
` : ''}${isJest ? `For Jest tests:
\`\`\`bash
npm install -D typescript @types/node @types/jest ts-jest jest
\`\`\`
` : ''}
## Step 2: Create TypeScript Configuration

Create a \`tsconfig.json\` file in your project root:

\`\`\`bash
npx tsc --init
\`\`\`

Or use this recommended configuration:

\`\`\`json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "types": [${isPlaywright ? '"@playwright/test"' : ''}${isPlaywright && isJest ? ', ' : ''}${isJest ? '"jest", "node"' : ''}],
    "esModuleInterop": true,
    "skipLibCheck": true,
    "strict": true,
    "resolveJsonModule": true,
    "outDir": "./dist",
    "rootDir": "./"
  },
  "include": ["${options.outputDir}/**/*"]
}
\`\`\`

${isJest ? `## Step 3: Configure Jest for TypeScript

Create or update \`jest.config.js\`:

\`\`\`javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/*.spec.ts'],
  moduleFileExtensions: ['ts', 'js', 'json'],
};
\`\`\`
` : ''}
## ${isJest ? 'Step 4' : 'Step 3'}: Run Your Tests

${isPlaywright ? `Run Playwright tests:
\`\`\`bash
npx playwright test ${options.outputDir}
\`\`\`
` : ''}${isJest ? `Run Jest tests:
\`\`\`bash
npx jest ${options.outputDir}
\`\`\`
` : ''}
## Need Help?

- TypeScript Documentation: https://www.typescriptlang.org/docs/
${isPlaywright ? '- Playwright TypeScript Guide: https://playwright.dev/docs/test-typescript' : ''}
${isJest ? '- Jest TypeScript Guide: https://jestjs.io/docs/getting-started#using-typescript' : ''}

---

Generated by Automation Quality MCP Server
`;

        return {
            console: `
📝 TypeScript Configuration Required

Your tests have been generated in TypeScript. To run them, please:

1. Install dependencies:
   ${isPlaywright ? 'npm install -D typescript @types/node @playwright/test' : ''}
   ${isJest ? 'npm install -D typescript @types/node @types/jest ts-jest jest' : ''}

2. Create tsconfig.json: npx tsc --init

3. Run tests:
   ${isPlaywright ? `npx playwright test ${options.outputDir}` : ''}
   ${isJest ? `npx jest ${options.outputDir}` : ''}

📄 Detailed setup instructions saved to: ${options.outputDir}/SETUP.md
`,
            markdown: markdown,
            steps: [
                {
                    step: 1,
                    description: "Install TypeScript and type definitions",
                    commands: isPlaywright && isJest ? [
                        "npm install -D typescript @types/node @playwright/test @types/jest ts-jest jest"
                    ] : isPlaywright ? [
                        "npm install -D typescript @types/node @playwright/test"
                    ] : [
                        "npm install -D typescript @types/node @types/jest ts-jest jest"
                    ]
                },
                {
                    step: 2,
                    description: "Create tsconfig.json",
                    command: "npx tsc --init"
                },
                {
                    step: 3,
                    description: "Run the tests",
                    commands: []
                }
            ],
            tsconfigTemplate: {
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "commonjs",
                    "lib": ["ES2020"],
                    "types": isPlaywright && isJest ? ["@playwright/test", "jest", "node"] : isPlaywright ? ["@playwright/test"] : ["jest", "node"],
                    "esModuleInterop": true,
                    "skipLibCheck": true,
                    "strict": true,
                    "resolveJsonModule": true,
                    "outDir": "./dist",
                    "rootDir": "./"
                },
                "include": [`${options.outputDir}/**/*`]
            }
        };
    }
}

module.exports = ApiGeneratorTool;
