/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

/**
 * Prompt Orchestrator
 * 
 * Coordinates the Planning → Generation → Validation → Healing workflow
 * for AI-based test code generation.
 */

const generationPrompts = require('./generation-prompts');
const validationRules = require('./validation-rules');
const healingPrompts = require('./healing-prompts');

class PromptOrchestrator {
  constructor(options = {}) {
    this.maxHealingAttempts = options.maxHealingAttempts || 3;
    this.language = options.language || 'typescript';
    this.outputFormat = options.outputFormat || 'playwright';
    this.verbose = options.verbose || false;
  }

  /**
   * Generate test code with validation and healing
   * 
   * Workflow:
   * 1. Generate code using AI
   * 2. Validate generated code
   * 3. If invalid, heal and retry (up to maxHealingAttempts)
   * 4. Return validated code or fallback
   */
  async generateTestCode(context, aiGenerator) {
    const { scenario, baseUrl } = context;
    
    this.log(`📝 Generating ${this.outputFormat} test for: ${scenario.title}`);
    
    // Step 1: Generate initial code
    let generatedCode = await this._generateCode(context, aiGenerator);
    
    // Step 1.5: Validate single file output (SAFETY NET)
    // Some helpful AI models try to create README, SUMMARY, etc.
    generatedCode = this._validateSingleFileOutput(generatedCode, context.targetFile);
    
    // Step 2: Validate
    let validation = this._validateCode(generatedCode, context);
    
    // Step 3: Heal if needed (up to maxHealingAttempts)
    let healingAttempt = 0;
    while (!validation.valid && healingAttempt < this.maxHealingAttempts) {
      healingAttempt++;
      this.log(`🔧 Healing attempt ${healingAttempt}/${this.maxHealingAttempts}...`);
      this.log(`   Issues: ${validation.issues.map(i => i.message).join(', ')}`);
// NOTE  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VlhST1VBPT06MmNlMWFhOTQ=
      
      generatedCode = await this._healCode(generatedCode, validation.issues, context, aiGenerator);
      validation = this._validateCode(generatedCode, context);
      
      if (validation.valid) {
        this.log(`✅ Code healed successfully!`);
      }
    }
    
    // Step 4: Return result
    if (!validation.valid) {
      this.log(`⚠️  Warning: Code still has issues after ${healingAttempt} healing attempts`);
      this.log(`   Remaining issues: ${validation.issues.map(i => i.message).join(', ')}`);
    }
    
    return {
      code: generatedCode,
      valid: validation.valid,
      issues: validation.issues,
      healingAttempts: healingAttempt,
      metadata: {
        scenario: scenario.title,
        format: this.outputFormat,
        language: this.language
      }
    };
  }

  /**
   * Generate code using AI
   */
  async _generateCode(context, aiGenerator) {
    const promptConfig = this._getGenerationPrompt();
    
    const systemPrompt = promptConfig.system;
    const userPrompt = promptConfig.user({
      ...context,
      language: this.language,
      options: { format: this.outputFormat }
    });
// eslint-disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VlhST1VBPT06MmNlMWFhOTQ=
    
    this.log(`💭 Sending generation prompt to AI...`);
    
    // Call AI generator (this would be GitHub Copilot API, OpenAI, etc.)
    const code = await aiGenerator.generate(systemPrompt, userPrompt);
    
    return code.trim();
  }

  /**
   * Validate generated code
   */
  _validateCode(code, context) {
    this.log(`🔍 Validating generated code...`);
    
    const isGraphQL = context?.scenario?.isGraphQL || false;
    const validator = validationRules.getValidator(this.outputFormat);
    const validation = validator.validateAll(code, this.language, isGraphQL);
    
    if (validation.valid) {
      this.log(`✅ Code validation passed!`);
    } else {
      this.log(`❌ Code validation failed with ${validation.issues.length} issues`);
    }
    
    return validation;
  }
// @ts-expect-error  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VlhST1VBPT06MmNlMWFhOTQ=

  /**
   * Heal code issues using AI
   */
  async _healCode(originalCode, issues, context, aiGenerator) {
    const healingConfig = this._getHealingPrompt();
    
    const systemPrompt = healingConfig.system;
    const userPrompt = healingConfig.user({
      originalCode,
      issues,
      scenario: context.scenario,
      format: this.outputFormat,
      language: this.language
    });
    
    this.log(`🏥 Sending healing prompt to AI...`);
    
    // Call AI generator for healing
    const healedCode = await aiGenerator.generate(systemPrompt, userPrompt);
    
    return healedCode.trim();
  }

  /**
   * Get generation prompt for current format
   */
  _getGenerationPrompt() {
    switch(this.outputFormat) {
      case 'playwright':
        return generationPrompts.playwrightScenario;
      case 'jest':
        return generationPrompts.jestScenario;
      case 'postman':
        return generationPrompts.postmanTestScript;
      default:
        throw new Error(`Unknown output format: ${this.outputFormat}`);
    }
  }

  /**
   * Get healing prompt for current format
   */
  _getHealingPrompt() {
    switch(this.outputFormat) {
      case 'playwright':
        return healingPrompts.playwrightHealing;
      case 'jest':
        return healingPrompts.jestHealing;
      default:
        return healingPrompts.genericHealing;
    }
  }

  /**
   * Log helper
   */
  log(message) {
    if (this.verbose) {
      console.error(message);
    }
  }

  /**
   * Generate full test file (with imports and structure)
   */
  generateTestFile(testBodies, testPlan, options = {}) {
    const { format, language, sessionId } = options;
    
    switch(format) {
      case 'playwright':
        return this._generatePlaywrightFile(testBodies, testPlan, language, sessionId);
      case 'jest':
        return this._generateJestFile(testBodies, testPlan, language, sessionId);
      default:
        throw new Error(`Unknown format: ${format}`);
    }
  }

  /**
   * Generate complete Playwright test file
   */
  _generatePlaywrightFile(testBodies, testPlan, language, sessionId) {
    const isTS = language === 'typescript';
    const imports = isTS 
      ? `import { test, expect } from '@playwright/test';`
      : `const { test, expect } = require('@playwright/test');`;

    const testCases = testPlan.sections.flatMap((section, sectionIndex) => 
      section.scenarios.map((scenario, scenarioIndex) => {
        const testBody = testBodies[`${sectionIndex}-${scenarioIndex}`];
        return `
  test('${scenario.title}', async ({ request }) => {
${testBody}
  });`;
      }).join('\n')
    );

    return `// Generated API Tests for: ${testPlan.title}
// Generated by Automation Quality MCP Server (AI-Generated)
// Session ID: ${sessionId}
// Language: ${language}

${imports}

test.describe('${testPlan.title} - API Tests', () => {
  const baseUrl = '${testPlan.baseUrl}';
${testCases}
});`;
  }

  /**
   * Generate complete Jest test file
   */
  _generateJestFile(testBodies, testPlan, language, sessionId) {
    const isTS = language === 'typescript';
    const imports = isTS
      ? `import axios from 'axios';\nimport { ApiTestUtils } from './test-utils';`
      : `const axios = require('axios');\nconst { ApiTestUtils } = require('./test-utils');`;
    
    const typeAnnotation = isTS ? ': ApiTestUtils' : '';

    const testCases = testPlan.sections.flatMap((section, sectionIndex) => 
      section.scenarios.map((scenario, scenarioIndex) => {
        const testBody = testBodies[`${sectionIndex}-${scenarioIndex}`];
        return `
    test('${scenario.title}', async () => {
${testBody}
    });`;
      }).join('\n')
    );

    return `// Generated Jest API Tests for: ${testPlan.title}
// Generated by Automation Quality MCP Server (AI-Generated)
// Session ID: ${sessionId}
// Language: ${language}

${imports}

describe('${testPlan.title} API Tests', () => {
  let apiUtils${typeAnnotation};
  const baseUrl = '${testPlan.baseUrl}';

  beforeAll(async () => {
    apiUtils = new ApiTestUtils(baseUrl);
    console.log('Test suite initialized');
  });

  afterAll(async () => {
    await apiUtils.cleanup();
    console.log('Test suite completed');
  });

  describe('Test Scenarios', () => {${testCases}
  });
});`;
  }

  /**
   * Validate that AI generated ONLY the requested file
   * Some helpful models try to create READMEs, summaries, etc.
   * This is a safety net in case prompts are ignored.
   * 
   * @param {string} generatedCode - The generated code from AI
   * @param {string} targetFileName - The expected file name
   * @returns {string} - Filtered code with only the test file
   */
  _validateSingleFileOutput(generatedCode, targetFileName) {
    // Check for multiple file indicators
    const multiFilePatterns = [
      /(?:create|generate|add)\s+(?:a\s+)?(?:README|SUMMARY|GUIDE|NOTES)/i,
      /(?:also|additionally),?\s+(?:create|generate|write)/i,
      /^#+\s+(?:README|SUMMARY|Quick Reference|Guide)/m,
      /File:\s+[A-Z_-]+\.md/i,
      /```[a-z]*\s*\n#+\s+(?:README|Summary)/i,
      /\*\*File:\*\*\s+(?:README|SUMMARY|GUIDE)/i
    ];

    for (const pattern of multiFilePatterns) {
      if (pattern.test(generatedCode)) {
        this.log(`⚠️  Warning: AI attempted to create additional files - filtering...`);
        // Extract just the test code, ignore suggestions
        return this._extractTestCodeOnly(generatedCode);
      }
    }

    return generatedCode;
  }

  /**
   * Extract only the actual test code from AI output
   * Remove any file creation suggestions or documentation
   * 
   * @param {string} output - The full AI output
   * @returns {string} - Extracted test code only
   */
  _extractTestCodeOnly(output) {
    // Look for code fence or actual code
    const codeFenceMatch = output.match(/```(?:typescript|javascript|ts|js)?\n([\s\S]+?)```/);
    if (codeFenceMatch) {
      this.log(`✅ Extracted test code from code fence`);
      return codeFenceMatch[1];
    }
    
    // Try to find the test code by looking for test.describe or describe
    const testDescribeMatch = output.match(/((?:test\.)?describe\(['"`][\s\S]+?\n\}\);)/);
    if (testDescribeMatch) {
      this.log(`✅ Extracted test code by pattern matching`);
      return testDescribeMatch[1];
    }
// NOTE  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VlhST1VBPT06MmNlMWFhOTQ=
    
    // If no extraction possible, return as-is but warn
    this.log(`⚠️  Could not extract test code - returning full output`);
    return output;
  }
}

module.exports = PromptOrchestrator;
