

const ToolBase = require('../base/ToolBase');
const fs = require('fs');
const path = require('path');

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
        boolean: () => ({ optional: () => ({}) })
    };
}
// eslint-disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WlRoa1NBPT06NTJkZGM1YzM=

// Input schema for the API project setup tool
const apiProjectSetupInputSchema = z.object({
    outputDir: z.string().optional(),
    promptUser: z.boolean().optional()
});

/**
 * API Project Setup Tool - Detect project configuration for API test generation
 * 
 * This tool performs smart detection of project configuration (TypeScript, Playwright, Jest)
 * and prompts users when configuration is ambiguous or missing.
 * 
 * Detection Logic (Option C - Smart Detection):
 * 1. Has playwright.config.ts → Playwright + TypeScript
 * 2. Has playwright.config.js → Playwright + JavaScript
 * 3. Has jest.config.ts → Jest + TypeScript
 * 4. Has jest.config.js → Jest + JavaScript
 * 5. Has tsconfig.json only → Ask framework, use TypeScript
 * 6. No config → Ask both framework and language
 */
class ApiProjectSetupTool extends ToolBase {
    static definition = {
        name: "api_project_setup",
        description: "Detect project configuration and setup preferences for API test generation. MUST be called BEFORE api_generator to determine framework (Playwright/Jest/Postman) and language (TypeScript/JavaScript). Uses smart detection: auto-detects from config files when possible, prompts user only when needed.",
        input_schema: {
            type: "object",
            properties: {
                outputDir: {
                    type: "string",
                    description: "Directory where tests will be generated (default: ./tests). Used to locate project root for config detection."
                },
                promptUser: {
                    type: "boolean",
                    description: "If true, always prompt user for preferences even if config detected. Use for overriding auto-detection. (default: false)"
                }
            }
        }
    };

    constructor() {
        super();
    }

    async execute(parameters) {
        try {
            const params = apiProjectSetupInputSchema.parse(parameters);
            
            const outputDir = params.outputDir || './tests';
            const forcePrompt = params.promptUser || false;
            
            // Detect project configuration
            const detection = this._detectProjectConfiguration(outputDir);
            
            // If user wants to override auto-detection, force prompts
            if (forcePrompt) {
                return this._buildUserPromptResponse(detection, true);
            }
            
            // Apply Smart Detection Logic (Option C)
            const result = this._applySmartDetection(detection);
            
            return result;

        } catch (error) {
            return {
                success: false,
                error: error.message,
                details: error.stack
            };
        }
    }
// NOTE  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WlRoa1NBPT06NTJkZGM1YzM=

    /**
     * Detect project configuration by scanning for config files
     */
    _detectProjectConfiguration(outputDir) {
        const projectRoot = path.resolve(outputDir, '..');
        
        // Check for config files
        const configFiles = {
            tsconfig: fs.existsSync(path.join(projectRoot, 'tsconfig.json')),
            playwrightTS: fs.existsSync(path.join(projectRoot, 'playwright.config.ts')),
            playwrightJS: fs.existsSync(path.join(projectRoot, 'playwright.config.js')),
            jestTS: fs.existsSync(path.join(projectRoot, 'jest.config.ts')),
            jestJS: fs.existsSync(path.join(projectRoot, 'jest.config.js')),
            packageJson: fs.existsSync(path.join(projectRoot, 'package.json'))
        };
        
        // Check package.json for TypeScript dependency
        let hasTypeScriptDep = false;
        let hasPlaywrightDep = false;
        let hasJestDep = false;
        
        if (configFiles.packageJson) {
            try {
                const packageJson = JSON.parse(fs.readFileSync(path.join(projectRoot, 'package.json'), 'utf8'));
                const allDeps = {
                    ...(packageJson.dependencies || {}),
                    ...(packageJson.devDependencies || {})
                };
                
                hasTypeScriptDep = !!allDeps.typescript;
                hasPlaywrightDep = !!allDeps['@playwright/test'];
                hasJestDep = !!allDeps.jest;
            } catch (err) {
                // Ignore parse errors
            }
        }
        
        return {
            projectRoot,
            configFiles,
            hasTypeScript: configFiles.tsconfig || hasTypeScriptDep,
            hasPlaywrightConfig: configFiles.playwrightTS || configFiles.playwrightJS,
            hasJestConfig: configFiles.jestTS || configFiles.jestJS,
            hasPlaywrightDep,
            hasJestDep,
            detectedFiles: Object.entries(configFiles)
                .filter(([key, exists]) => exists && key !== 'packageJson')
                .map(([key]) => this._getConfigFileName(key))
        };
    }

    /**
     * Apply Smart Detection Logic (Option C)
     */
    _applySmartDetection(detection) {
        const { configFiles } = detection;
        
        // Scenario 1: Playwright with TypeScript
        if (configFiles.playwrightTS) {
            return this._buildAutoDetectedResponse(detection, 'playwright', 'typescript', 
                'Detected Playwright project with TypeScript configuration');
        }
// eslint-disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WlRoa1NBPT06NTJkZGM1YzM=
        
        // Scenario 2: Playwright with JavaScript
        if (configFiles.playwrightJS) {
            return this._buildAutoDetectedResponse(detection, 'playwright', 'javascript', 
                'Detected Playwright project with JavaScript configuration');
        }
        
        // Scenario 3: Jest with TypeScript
        if (configFiles.jestTS) {
            return this._buildAutoDetectedResponse(detection, 'jest', 'typescript', 
                'Detected Jest project with TypeScript configuration');
        }
        
        // Scenario 4: Jest with JavaScript
        if (configFiles.jestJS) {
            return this._buildAutoDetectedResponse(detection, 'jest', 'javascript', 
                'Detected Jest project with JavaScript configuration');
        }
        
        // Scenario 5: Only TypeScript config (no framework config)
        if (configFiles.tsconfig && !detection.hasPlaywrightConfig && !detection.hasJestConfig) {
            return this._buildUserPromptResponse(detection, true, false);
        }
        
        // Scenario 6: No config files (empty folder) - Ask both framework and language
        if (!detection.hasTypeScript && !detection.hasPlaywrightConfig && !detection.hasJestConfig) {
            return this._buildUserPromptResponse(detection, true, true);
        }
        
        // Fallback: Has some config but ambiguous - ask user
        return this._buildUserPromptResponse(detection, true, true);
    }

    /**
     * Build auto-detected response (no user input needed)
     */
    _buildAutoDetectedResponse(detection, framework, language, message) {
        return {
            success: true,
            autoDetected: true,
            config: {
                framework: framework,
                language: language,
                hasTypeScript: language === 'typescript',
                hasPlaywrightConfig: framework === 'playwright',
                hasJestConfig: framework === 'jest',
                configFiles: detection.detectedFiles
            },
            message: message,
            detectedFiles: detection.detectedFiles,
            nextStep: `Call api_generator with outputFormat: '${framework}' and language: '${language}'`
        };
    }

    /**
     * Build user prompt response (needs user input)
     */
    _buildUserPromptResponse(detection, askFramework = true, askLanguage = true) {
        const prompts = [];
        
        // Framework prompt
        if (askFramework) {
            prompts.push({
                name: "framework",
                question: "Which test framework would you like to use?",
                choices: [
                    { 
                        value: "playwright", 
                        label: "Playwright", 
                        description: "Recommended for API testing with request fixture" 
                    },
                    { 
                        value: "jest", 
                        label: "Jest", 
                        description: "Popular testing framework with axios for API calls" 
                    },
                    { 
                        value: "postman", 
                        label: "Postman Collection", 
                        description: "Generate Postman collection JSON format" 
                    },
                    { 
                        value: "all", 
                        label: "All Formats", 
                        description: "Generate tests in all supported formats" 
                    }
                ],
                default: "playwright"
            });
        }
        
        // Language prompt
        if (askLanguage) {
            prompts.push({
                name: "language",
                question: "Which language would you like to use?",
                choices: [
                    { 
                        value: "typescript", 
                        label: "TypeScript", 
                        description: "Recommended for better type safety and IDE support" 
                    },
                    { 
                        value: "javascript", 
                        label: "JavaScript", 
                        description: "Simpler setup, no compilation needed" 
                    }
                ],
                default: "typescript"
            });
        }
// TODO  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WlRoa1NBPT06NTJkZGM1YzM=
        
        return {
            success: true,
            needsUserInput: true,
            detected: {
                hasTypeScript: detection.hasTypeScript,
                hasPlaywrightConfig: detection.hasPlaywrightConfig,
                hasJestConfig: detection.hasJestConfig,
                configFiles: detection.detectedFiles
            },
            prompts: prompts,
            message: this._buildPromptMessage(detection, askFramework, askLanguage),
            nextStep: "Get user preferences, then call api_generator with chosen framework and language"
        };
    }

    /**
     * Build appropriate message based on what's being asked
     */
    _buildPromptMessage(detection, askFramework, askLanguage) {
        if (detection.detectedFiles.length === 0) {
            return "No project configuration detected. Please specify your preferences for test generation.";
        }
        
        if (!askFramework && askLanguage) {
            return `Detected TypeScript configuration (${detection.detectedFiles.join(', ')}). Please choose a test framework.`;
        }
        
        return `Found partial configuration (${detection.detectedFiles.join(', ')}). Please specify your preferences.`;
    }

    /**
     * Get human-readable config file name from key
     */
    _getConfigFileName(key) {
        const mapping = {
            'tsconfig': 'tsconfig.json',
            'playwrightTS': 'playwright.config.ts',
            'playwrightJS': 'playwright.config.js',
            'jestTS': 'jest.config.ts',
            'jestJS': 'jest.config.js'
        };
        return mapping[key] || key;
    }
}

module.exports = ApiProjectSetupTool;
