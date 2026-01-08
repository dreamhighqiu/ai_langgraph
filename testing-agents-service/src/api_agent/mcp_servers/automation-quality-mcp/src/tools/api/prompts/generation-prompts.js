
// FIXME  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZW5WVE5BPT06NDlkYmIxNjk=

/**
 * Code Generation Prompts for API Test Generator
 * 
 * This module contains all prompts used for AI-based test code generation.
 * Separated for easy iteration, versioning, and prompt engineering.
 */

module.exports = {
  /**
   * Playwright test generation prompts
   */
  playwright: {
    system: `You are an expert Playwright test engineer. Generate clean, idiomatic, production-ready Playwright API tests.

CRITICAL - File Generation Rules:
- Generate ONLY the ONE requested test file
- DO NOT create any additional files (README, SUMMARY, GUIDE, NOTES, etc.)
- DO NOT create documentation files unless explicitly requested
- DO NOT create helper files unless explicitly requested
- Output ONLY the test code for the specified file

Requirements:
- Use Playwright's request fixture directly (no wrappers)
- Use proper TypeScript types when language=typescript
- Include proper async/await patterns
- Use template literals for URL construction with \${baseUrl}
- Generate proper assertions with expect()
- Handle both single and chained requests
- Include proper error handling
- Add descriptive comments for complex logic

Code Style:
- 2-space indentation
- Single quotes for strings (except template literals)
- Semicolons at end of statements
- Clear variable naming
- Proper spacing and formatting`,

    /**
     * Generate a section test file with multiple scenarios
     */
    generateTest: (context) => {
      const { testPlanTitle, baseUrl, sectionTitle, scenarios, language, isTypeScript, sessionId } = context;
      
      let prompt = `Generate a complete Playwright test file for this section:

**Test Plan:** ${testPlanTitle}
**Section:** ${sectionTitle}
**Base URL:** ${baseUrl}
**Language:** ${language}
**Session ID:** ${sessionId}

**Scenarios to test:**
`;

      scenarios.forEach((scenario, idx) => {
        prompt += `
${idx + 1}. **${scenario.title}**
   - Method: ${scenario.method}
   - Endpoint: ${scenario.endpoint}
   - Expected Status: ${scenario.expectedStatus || 200}
`;
        
        if (scenario.requestBody) {
          prompt += `   - Request Body: ${JSON.stringify(scenario.requestBody, null, 2).substring(0, 200)}...
`;
        }
        
        if (scenario.expectedBody) {
          prompt += `   - Expected Body Fields: ${Object.keys(scenario.expectedBody).join(', ')}
`;
        }

        if (scenario.steps && scenario.steps.length > 0) {
          prompt += `   - Multi-step test with ${scenario.steps.length} sequential requests
`;
        }
      });

      prompt += `
**Instructions:**
1. Generate a COMPLETE test file including imports and test structure
2. ${isTypeScript ? 'Use TypeScript with proper types' : 'Use JavaScript'}
3. Import from '@playwright/test' for Playwright
4. Create test.describe() for the section: "${sectionTitle}"
5. Create one test() for each scenario above
6. Use \`const baseUrl = '${baseUrl}';\` at the top of describe block
7. Use Playwright's \`request\` fixture directly (no helper classes)
8. Construct URLs as template literals: \`\${baseUrl}/endpoint\`
9. Include proper assertions for status codes and response body structure
10. For multi-step tests, chain requests and pass data between steps
11. Add error handling where appropriate
12. Include comments for complex logic

**CRITICAL - Output Restrictions:**
- Generate ONLY this ONE test file: ${sectionTitle}
- DO NOT generate README, SUMMARY, GUIDE, or any other files
- DO NOT suggest creating additional files
- DO NOT include file creation instructions
- Return ONLY the test file code as plain text

**File structure:**
\`\`\`
// Header comment
import/require statements
test.describe('${sectionTitle}', () => {
  const baseUrl = '${baseUrl}';
  
  test('scenario 1', async ({ request }) => {
    // test code
  });
  
  test('scenario 2', async ({ request }) => {
    // test code
  });
});
\`\`\`

Return the COMPLETE file content for THIS FILE ONLY.`;

      return prompt;
    },

    /**
     * Generate main test file that runs all sections
     */
    generateMainTest: (context) => {
      const { testPlanTitle, baseUrl, sections, language, isTypeScript, sessionId } = context;
      
      let prompt = `Generate a main Playwright test file that orchestrates all test sections:

**Test Plan:** ${testPlanTitle}
**Base URL:** ${baseUrl}
**Language:** ${language}
**Session ID:** ${sessionId}

**Sections:**
`;

      sections.forEach((section, idx) => {
        prompt += `${idx + 1}. ${section.title} (${section.scenarioCount} scenarios)
`;
      });

      prompt += `
**Instructions:**
1. Generate a COMPLETE main test file
2. ${isTypeScript ? 'Use TypeScript' : 'Use JavaScript'}
3. Import from '@playwright/test'
4. Create one main test.describe() for "${testPlanTitle}"
5. Set \`const baseUrl = '${baseUrl}';\`
6. Import or reference individual section test files
7. Keep it simple - this is just an orchestration file
8. Add a comment noting individual sections are in separate files

**CRITICAL - Output Restrictions:**
- Generate ONLY this ONE main test file
- DO NOT generate README, SUMMARY, GUIDE, or any other files
- DO NOT create section files (they're generated separately)
- Return ONLY the main test file code

Return the COMPLETE main file content for THIS FILE ONLY.`;

      return prompt;
    }
  },

  /**
   * Jest test generation prompts
   */
  jest: {
    system: `You are an expert Jest test engineer. Generate clean, idiomatic, production-ready Jest API tests using axios.

CRITICAL - File Generation Rules:
- Generate ONLY the ONE requested test file
- DO NOT create any additional files (README, SUMMARY, GUIDE, NOTES, etc.)
- DO NOT create documentation files unless explicitly requested
- Output ONLY the test code for the specified file

Requirements:
- Use axios for API calls
- Use proper TypeScript types when language=typescript
- Include proper async/await patterns
- Generate proper assertions with expect()
- Handle both single and chained requests
- Include proper error handling

Code Style:
- 2-space indentation
- Single quotes for strings (except template literals)
- Semicolons at end of statements
- Clear variable naming`,

    /**
     * Generate a section test file with multiple scenarios
     */
    generateTest: (context) => {
      const { testPlanTitle, baseUrl, sectionTitle, scenarios, language, isTypeScript, sessionId } = context;
      
      let prompt = `Generate a complete Jest test file for this section:

**Test Plan:** ${testPlanTitle}
**Section:** ${sectionTitle}
**Base URL:** ${baseUrl}
**Language:** ${language}
**Session ID:** ${sessionId}

**Scenarios to test:**
`;

      scenarios.forEach((scenario, idx) => {
        prompt += `
${idx + 1}. **${scenario.title}**
   - Method: ${scenario.method}
   - Endpoint: ${scenario.endpoint}
   - Expected Status: ${scenario.expectedStatus || 200}
`;
        
        if (scenario.requestBody) {
          prompt += `   - Request Body: ${JSON.stringify(scenario.requestBody, null, 2).substring(0, 200)}...
`;
        }
        
        if (scenario.expectedBody) {
          prompt += `   - Expected Body Fields: ${Object.keys(scenario.expectedBody).join(', ')}
`;
        }

        if (scenario.steps && scenario.steps.length > 0) {
          prompt += `   - Multi-step test with ${scenario.steps.length} sequential requests
`;
        }
      });

      prompt += `
**Instructions:**
1. Generate a COMPLETE test file including imports and test structure
2. ${isTypeScript ? 'Use TypeScript with proper types' : 'Use JavaScript'}
3. Import axios for HTTP requests
4. Create describe() for the section: "${sectionTitle}"
5. Create one test() for each scenario above
6. Use \`const baseUrl = '${baseUrl}';\` at the top
7. Use axios methods (axios.get, axios.post, etc.)
8. Construct URLs as template literals: \`\${baseUrl}/endpoint\`
9. Include proper assertions with Jest's expect()
10. For multi-step tests, chain requests and pass data between steps
11. Add error handling where appropriate

**CRITICAL - Output Restrictions:**
- Generate ONLY this ONE test file
- DO NOT generate README, SUMMARY, GUIDE, or any other files
- DO NOT suggest creating additional files
- Return ONLY the test file code as plain text

**File structure:**
\`\`\`
// Header comment
import/require statements
describe('${sectionTitle}', () => {
  const baseUrl = '${baseUrl}';
  
  test('scenario 1', async () => {
    // test code
  });
// TODO  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZW5WVE5BPT06NDlkYmIxNjk=
  
  test('scenario 2', async () => {
    // test code
  });
});
\`\`\`

Return the COMPLETE file content for THIS FILE ONLY.`;

      return prompt;
    },

    /**
     * Generate main test file
     */
    generateMainTest: (context) => {
      const { testPlanTitle, baseUrl, sections, language, isTypeScript, sessionId } = context;
      
      let prompt = `Generate a main Jest test file that orchestrates all test sections:

**Test Plan:** ${testPlanTitle}
**Base URL:** ${baseUrl}
**Language:** ${language}
**Session ID:** ${sessionId}

**Sections:**
`;

      sections.forEach((section, idx) => {
        prompt += `${idx + 1}. ${section.title} (${section.scenarioCount} scenarios)
`;
      });

      prompt += `
**Instructions:**
1. Generate a COMPLETE main test file
2. ${isTypeScript ? 'Use TypeScript' : 'Use JavaScript'}
3. Import axios
4. Create one main describe() for "${testPlanTitle}"
5. Set \`const baseUrl = '${baseUrl}';\`
6. Add a comment noting individual sections are in separate files

**CRITICAL - Output Restrictions:**
- Generate ONLY this ONE main test file
- DO NOT generate README, SUMMARY, GUIDE, or any other files
- Return ONLY the main test file code

Return the COMPLETE main file content for THIS FILE ONLY.`;

      return prompt;
    }
  },

  /**
   * Legacy scenario-level prompts (kept for backward compatibility)
   */
  playwrightScenario: {
    system: `You are an expert Playwright test engineer for REST and GraphQL APIs. Generate clean, idiomatic, production-ready Playwright API tests.

Requirements:
- Support both REST and GraphQL API testing
- For REST APIs: Use appropriate HTTP methods (GET, POST, PUT, DELETE, etc.)
- For GraphQL APIs: Always use POST method to /graphql (or specified) endpoint
- For GraphQL APIs: Format request body with 'query' and 'variables' fields
- For GraphQL APIs: Validate response has 'data' (success) or 'errors' (failure)
- Use Playwright's request fixture directly (no wrappers)
- Use proper TypeScript types when language=typescript
- Include proper async/await patterns
- Use template literals for URL construction with \${baseUrl}
- Generate proper assertions with expect()
- Handle both single and chained requests
- Include proper error handling
- Add descriptive comments for complex logic

Code Style:
- 2-space indentation
- Single quotes for strings (except template literals)
- Semicolons at end of statements
- Clear variable naming
- Proper spacing and formatting`,

    user: (context) => {
      const { scenario, baseUrl, language, options } = context;
      
      let prompt = `Generate a Playwright test for this scenario:

**Test Details:**
- Title: "${scenario.title}"
- API Type: ${scenario.isGraphQL ? 'GraphQL' : 'REST'}
- Method: ${scenario.method}
- Endpoint: ${scenario.endpoint}
- Base URL: ${baseUrl}
- Language: ${language}

`;

      // NEW: GraphQL-specific section
      if (scenario.isGraphQL && scenario.graphql) {
        prompt += `**GraphQL Query:**
\`\`\`graphql
${scenario.graphql.query}
\`\`\`

`;
        if (scenario.graphql.variables && Object.keys(scenario.graphql.variables).length > 0) {
          prompt += `**GraphQL Variables:**
\`\`\`json
${JSON.stringify(scenario.graphql.variables, null, 2)}
\`\`\`

`;
        }
        
        prompt += `**GraphQL Request Instructions:**
- Use POST method to endpoint: ${scenario.endpoint || '/graphql'}
- Send request body with this structure:
  \`\`\`javascript
  {
    query: \`<query string>\`,
    variables: <variables object>
  }
  \`\`\`
- Validate GraphQL response structure:
  - Success case: expect(responseData).toHaveProperty('data')
  - Error case: expect(responseData).toHaveProperty('errors')

`;
      } else {
        // EXISTING: REST-specific sections
        // Add request details
        if (scenario.data && Object.keys(scenario.data).length > 0) {
          prompt += `**Request Body:**
\`\`\`json
${JSON.stringify(scenario.data, null, 2)}
\`\`\`

`;
        }
// @ts-expect-error  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZW5WVE5BPT06NDlkYmIxNjk=

        if (scenario.headers && Object.keys(scenario.headers).length > 0) {
          prompt += `**Headers:**
\`\`\`json
${JSON.stringify(scenario.headers, null, 2)}
\`\`\`

`;
        }

        if (scenario.query && Object.keys(scenario.query).length > 0) {
          prompt += `**Query Parameters:**
\`\`\`json
${JSON.stringify(scenario.query, null, 2)}
\`\`\`

`;
        }

        if (scenario.pathParams && Object.keys(scenario.pathParams).length > 0) {
          prompt += `**Path Parameters:**
\`\`\`json
${JSON.stringify(scenario.pathParams, null, 2)}
\`\`\`

`;
        }
      }

      // Add expectations
      if (scenario.expect) {
        prompt += `**Expected Response:**
- Status Code: ${scenario.expect.status || 200}
`;
        if (scenario.expect.body) {
          prompt += `- Response Body Structure:
\`\`\`json
${JSON.stringify(scenario.expect.body, null, 2)}
\`\`\`
`;
        }
      }

      // Add chained requests if present
      if (scenario.chain && scenario.chain.length > 0) {
        prompt += `\n**Chained Requests:**
This is a multi-step test with ${scenario.chain.length} sequential API calls.
`;
        scenario.chain.forEach((step, index) => {
          prompt += `
Step ${index + 1}: ${step.name}
- Method: ${step.method}
- Endpoint: ${step.endpoint}
`;
          if (step.extract) {
            prompt += `- Extract: ${JSON.stringify(step.extract)}
`;
          }
        });
      }

      prompt += `
**Instructions:**
1. Generate ONLY the test body code (the code inside the test() function)
2. Start at the correct indentation level (6 spaces for test body)
`;

      if (scenario.isGraphQL) {
        prompt += `3. Use \`await request.post()\` for GraphQL (always POST)
4. Construct URL as: \`\${baseUrl}${scenario.endpoint || '/graphql'}\`
5. Include request body with 'query' and 'variables' fields
6. Add GraphQL-specific assertions (check for 'data' or 'errors' properties)
`;
      } else {
        prompt += `3. Use \`await request.${scenario.method.toLowerCase()}()\` for the API call
4. Construct URL as: \`\${baseUrl}${scenario.endpoint}\`
5. Include all request options (headers, params, data)
6. Add proper assertions for status code and response body
`;
      }

      prompt += `7. For TypeScript, use proper types
8. For chained requests, store results and use them in subsequent calls

DO NOT include:
- test.describe() wrapper
- test() function declaration
- import statements
- Extra blank lines at start/end

Return ONLY the test body code, properly indented.`;

      return prompt;
    }
  },

  /**
   * Generate a complete Jest test for a single scenario
   */
  jestScenario: {
    system: `You are an expert Jest test engineer for REST and GraphQL APIs. Generate clean, idiomatic, production-ready Jest API tests using axios.

Requirements:
- Support both REST and GraphQL API testing
- For REST APIs: Use appropriate HTTP methods (GET, POST, PUT, DELETE, etc.)
- For GraphQL APIs: Always use POST method to /graphql (or specified) endpoint
- For GraphQL APIs: Format request body with 'query' and 'variables' fields
- For GraphQL APIs: Validate response has 'data' (success) or 'errors' (failure)
- Use axios for API calls
- Use proper TypeScript types when language=typescript
- Include proper async/await patterns
- Generate proper assertions with expect()
- Handle both single and chained requests
- Include proper error handling
- Add descriptive comments for complex logic

Code Style:
- 2-space indentation
- Single quotes for strings
- Semicolons at end of statements
- Clear variable naming
- Proper spacing and formatting`,

    user: (context) => {
      const { scenario, baseUrl, language, options } = context;
      
      let prompt = `Generate a Jest/axios test for this scenario:

**Test Details:**
- Title: "${scenario.title}"
- API Type: ${scenario.isGraphQL ? 'GraphQL' : 'REST'}
- Method: ${scenario.method}
- Endpoint: ${scenario.endpoint}
- Base URL: ${baseUrl}
- Language: ${language}

`;

      // NEW: GraphQL-specific section
      if (scenario.isGraphQL && scenario.graphql) {
        prompt += `**GraphQL Query:**
\`\`\`graphql
${scenario.graphql.query}
\`\`\`

`;
        if (scenario.graphql.variables && Object.keys(scenario.graphql.variables).length > 0) {
          prompt += `**GraphQL Variables:**
\`\`\`json
${JSON.stringify(scenario.graphql.variables, null, 2)}
\`\`\`

`;
        }
        
        prompt += `**GraphQL Request Instructions:**
- Use POST method to endpoint: ${scenario.endpoint || '/graphql'}
- Send request body with this structure:
  \`\`\`javascript
  {
    query: \`<query string>\`,
    variables: <variables object>
  }
  \`\`\`
- Validate GraphQL response structure:
  - Success case: expect(response.data).toHaveProperty('data')
  - Error case: expect(response.data).toHaveProperty('errors')

`;
      } else {
        // EXISTING: REST-specific sections
        // Add request details (similar to Playwright)
        if (scenario.data && Object.keys(scenario.data).length > 0) {
          prompt += `**Request Body:**
\`\`\`json
${JSON.stringify(scenario.data, null, 2)}
\`\`\`

`;
        }

        if (scenario.headers && Object.keys(scenario.headers).length > 0) {
          prompt += `**Headers:**
\`\`\`json
${JSON.stringify(scenario.headers, null, 2)}
\`\`\`

`;
        }

        if (scenario.query && Object.keys(scenario.query).length > 0) {
          prompt += `**Query Parameters:**
\`\`\`json
${JSON.stringify(scenario.query, null, 2)}
\`\`\`

`;
        }
      }

      // Add expectations
      if (scenario.expect) {
        prompt += `**Expected Response:**
- Status Code: ${scenario.expect.status || 200}
`;
        if (scenario.expect.body) {
          prompt += `- Response Body Structure:
\`\`\`json
${JSON.stringify(scenario.expect.body, null, 2)}
\`\`\`
`;
        }
      }

      prompt += `
**Instructions:**
1. Generate ONLY the test body code (the code inside the test() function)
2. Start at the correct indentation level (6 spaces for test body)
`;

      if (scenario.isGraphQL) {
        prompt += `3. Use \`await apiUtils.makeRequest()\` with method: 'POST'
4. Set URL to: '${scenario.endpoint || '/graphql'}'
5. Include request data with 'query' and 'variables' fields
6. Add GraphQL-specific assertions (check for 'data' or 'errors' properties in response.data)
`;
      } else {
        prompt += `3. Use \`await apiUtils.makeRequest()\` helper for API calls
4. Include all request options (method, url, headers, params, data)
5. Add proper assertions for status code and response body
`;
      }

      prompt += `6. For TypeScript, use proper types
7. Handle errors appropriately

DO NOT include:
- describe() wrapper
- test() function declaration
- import statements
- Extra blank lines at start/end

Return ONLY the test body code, properly indented.`;

      return prompt;
    }
  },

  /**
   * Generate Postman test scripts
   */
  postmanTestScript: {
    system: `You are a Postman automation expert. Generate clear, effective Postman test scripts.

Requirements:
- Use pm.test() for assertions
- Use pm.response for response validation
- Use pm.expect() for assertions
- Include proper error messages
- Add descriptive test names`,

    user: (context) => {
      const { expect, extract } = context;
      
      let prompt = `Generate Postman test script for this validation:

`;
// FIXME  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZW5WVE5BPT06NDlkYmIxNjk=

      if (expect && expect.status) {
        prompt += `**Expected Status:** ${expect.status}
`;
      }

      if (expect && expect.body) {
        prompt += `**Expected Response Body:**
\`\`\`json
${JSON.stringify(expect.body, null, 2)}
\`\`\`
`;
      }

      if (extract) {
        prompt += `**Extract Variables:**
${Object.entries(extract).map(([key, field]) => `- ${key} from ${field}`).join('\n')}
`;
      }

      prompt += `
**Instructions:**
1. Generate test script as array of strings
2. Each line should be a separate array element
3. Include status code validation
4. Include response body validation
5. Extract and store variables if specified

Return JavaScript array of test script lines.`;

      return prompt;
    }
  }
};
