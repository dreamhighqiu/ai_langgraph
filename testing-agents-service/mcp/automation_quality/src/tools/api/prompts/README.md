# Prompt Orchestration System

This directory contains the prompt orchestration system for AI-based test code generation.

## Architecture

```
┌─────────────────────────────────────────────┐
│         ORCHESTRATION PIPELINE              │
└─────────────────────────────────────────────┘

1️⃣ PLANNING (Structured - Code)
   ├─ Parse test plan markdown
   ├─ Extract scenarios & context
   └─ Build structured data

2️⃣ GENERATION (AI-Driven)
   ├─ Load generation prompts
   ├─ Construct context
   ├─ Call AI (GitHub Copilot API)
   └─ Return generated code

3️⃣ VALIDATION (Automated - Code)
   ├─ Check syntax & structure
   ├─ Validate patterns & conventions
   └─ Report issues

4️⃣ HEALING (AI-Driven - If Needed)
   ├─ Load healing prompts
   ├─ Include issue details
   ├─ Call AI to fix issues
   └─ Return fixed code

5️⃣ OUTPUT
   ├─ Write validated test files
   └─ Report generation status
```

## Files

### `generation-prompts.js`
Contains all prompts for generating test code.

**Exports:**
- `playwrightScenario` - Generate Playwright API tests
- `jestScenario` - Generate Jest/axios tests
- `postmanTestScript` - Generate Postman test scripts

**Usage:**
```javascript
const prompts = require('./generation-prompts');

const context = {
  scenario: { title, method, endpoint, data, expect },
  baseUrl: 'https://api.example.com',
  language: 'typescript',
  options: { format: 'playwright' }
};

const systemPrompt = prompts.playwrightScenario.system;
const userPrompt = prompts.playwrightScenario.user(context);
```

### `validation-rules.js`
Validates generated code against quality rules.

**Exports:**
- `playwright` - Playwright validation rules
- `jest` - Jest validation rules
- `postman` - Postman validation rules
- `getValidator(format)` - Get validator for format

**Usage:**
```javascript
const validation = require('./validation-rules');

const validator = validation.getValidator('playwright');
const result = validator.validateAll(code, 'typescript');

if (!result.valid) {
  console.log('Issues:', result.issues);
}
```

**Validation Checks:**
- ✅ Proper async/await usage
- ✅ Correct URL construction (no template literal escaping bugs!)
- ✅ Required assertions present
- ✅ Syntax correctness (balanced brackets/braces)
- ✅ Framework-specific patterns

### `healing-prompts.js`
Prompts for fixing validation issues.

**Exports:**
- `playwrightHealing` - Fix Playwright test issues
- `jestHealing` - Fix Jest test issues
- `genericHealing` - Fix any code issues

**Usage:**
```javascript
const healing = require('./healing-prompts');

const context = {
  originalCode: '...',
  issues: [{ severity, message, fix }],
  scenario: { ... }
};

const systemPrompt = healing.playwrightHealing.system;
const userPrompt = healing.playwrightHealing.user(context);
```

### `orchestrator.js`
Main orchestrator class that coordinates the workflow.

**Usage:**
```javascript
const PromptOrchestrator = require('./orchestrator');

const orchestrator = new PromptOrchestrator({
  maxHealingAttempts: 3,
  language: 'typescript',
  outputFormat: 'playwright',
  verbose: true
});

// Generate single test scenario
const result = await orchestrator.generateTestCode(
  { scenario, baseUrl },
  aiGenerator
);

// Generate complete test file
const fileContent = orchestrator.generateTestFile(
  testBodies,
  testPlan,
  { format, language, sessionId }
);
```

**Key Methods:**
- `generateTestCode(context, aiGenerator)` - Generate & validate single test
- `generateTestFile(testBodies, testPlan, options)` - Generate complete file
- Internal: `_generateCode()`, `_validateCode()`, `_healCode()`

## Workflow Example

```javascript
// 1. Create orchestrator
const orchestrator = new PromptOrchestrator({
  language: 'typescript',
  outputFormat: 'playwright',
  maxHealingAttempts: 3,
  verbose: true
});

// 2. Generate test for each scenario
const testBodies = {};
for (const [sectionIdx, section] of testPlan.sections.entries()) {
  for (const [scenarioIdx, scenario] of section.scenarios.entries()) {
    const context = {
      scenario,
      baseUrl: testPlan.baseUrl
    };
    
    // AI generates → validates → heals if needed
    const result = await orchestrator.generateTestCode(context, aiGenerator);
    
    testBodies[`${sectionIdx}-${scenarioIdx}`] = result.code;
    
    if (!result.valid) {
      console.warn(`⚠️  Test has issues:`, result.issues);
    }
  }
}

// 3. Generate complete file
const fileContent = orchestrator.generateTestFile(testBodies, testPlan, {
  format: 'playwright',
  language: 'typescript',
  sessionId: 'test-123'
});

// 4. Write file
fs.writeFileSync('tests/api-tests.spec.ts', fileContent);
```

## Benefits

### 🎯 **Separation of Concerns**
- **Planning** = Deterministic logic (code handles this)
- **Generation** = Creative task (AI handles this)
- **Validation** = Quality gates (code handles this)
- **Healing** = Error correction (AI handles this)

### 🔄 **Self-Correcting**
- Validation catches issues automatically
- Healing fixes them without manual intervention
- Up to 3 attempts to get perfect code
- Graceful degradation if healing fails

### 📝 **Easy Prompt Engineering**
- All prompts in one place
- Easy to iterate and improve
- Version control for prompts
- A/B testing different strategies

### 🚀 **Future-Proof**
- Swap AI providers easily
- Add new output formats quickly
- Extend validation rules
- Improve prompts without code changes

## Prompt Engineering Tips

### For Generation Prompts
1. **Be Specific**: Clear requirements and examples
2. **Include Context**: Provide all necessary data
3. **Set Constraints**: Specify what NOT to do
4. **Use Examples**: Show desired output format
5. **Iterate**: Test and refine based on results

### For Healing Prompts
1. **Include Original Code**: Show what needs fixing
2. **List Specific Issues**: Enumerate all problems
3. **Provide Fixes**: Suggest how to fix each issue
4. **Maintain Context**: Reference original scenario
5. **Keep It Focused**: Fix only reported issues

## Extending the System

### Add New Output Format
1. Add generation prompt in `generation-prompts.js`
2. Add validation rules in `validation-rules.js`
3. Add healing prompt in `healing-prompts.js`
4. Update orchestrator's `_getGenerationPrompt()` and `_getHealingPrompt()`
5. Add file generation in `generateTestFile()`

### Add New Validation Rule
1. Open `validation-rules.js`
2. Add new validation function to appropriate format
3. Update `validateAll()` to include new check
4. Test with sample code

### Improve Prompts
1. Edit prompt in respective file
2. Test with real scenarios
3. Compare before/after quality
4. Iterate based on results

## AI Generator Interface

The orchestrator expects an AI generator with this interface:

```javascript
class AIGenerator {
  /**
   * Generate code from prompts
   * @param {string} systemPrompt - System/role prompt
   * @param {string} userPrompt - User request prompt
   * @returns {Promise<string>} - Generated code
   */
  async generate(systemPrompt, userPrompt) {
    // Call AI API (GitHub Copilot, OpenAI, etc.)
    // Return generated code as string
  }
}
```

## Configuration

**Orchestrator Options:**
- `maxHealingAttempts` (default: 3) - Max healing retries
- `language` (default: 'typescript') - Target language
- `outputFormat` (default: 'playwright') - Test format
- `verbose` (default: false) - Enable logging

## Future Enhancements

- [ ] Add LLM-specific prompt optimizations
- [ ] Support streaming responses
- [ ] Add prompt caching for performance
- [ ] Implement prompt versioning
- [ ] Add metrics and analytics
- [ ] Support custom validation rules
- [ ] Add prompt templates for common patterns
- [ ] Implement prompt AB testing framework

---

**Generated by:** Automation Quality MCP Server
**Architecture:** Prompt Orchestration (Planning → Generation → Validation → Healing)
