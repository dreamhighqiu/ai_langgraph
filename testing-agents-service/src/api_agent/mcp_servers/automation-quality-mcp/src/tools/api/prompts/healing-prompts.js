

/**
 * Healing Prompts - Fix issues in generated code
 * 
 * These prompts are used to fix validation errors in generated code.
 * Applied when validation fails, with specific feedback about issues.
 */

module.exports = {
  /**
   * Heal Playwright test code issues
   */
  playwrightHealing: {
    system: `You are a code fixing expert for REST and GraphQL API tests. Fix the issues in the generated Playwright test code while maintaining functionality.

Requirements:
- Support both REST and GraphQL API testing patterns
- For GraphQL: POST method with { query: "...", variables: {...} } body
- For GraphQL: Validate response has 'data' or 'errors' property
- Fix ONLY the reported issues
- Maintain all existing functionality
- Keep the same code structure
- Use proper indentation (6 spaces for test body)
- Return ONLY the fixed code, no explanations
- DO NOT create any additional files
- DO NOT generate README, SUMMARY, or documentation`,

    user: (context) => {
      const { originalCode, issues, scenario } = context;
// eslint-disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZGtONWJRPT06OWM2OGZjMmY=
      
      let prompt = `Fix the following issues in this Playwright test code:

**Original Code:**
\`\`\`typescript
${originalCode}
\`\`\`

**Issues Found:**
${issues.map((issue, i) => `${i + 1}. [${issue.severity.toUpperCase()}] ${issue.message}
   Fix: ${issue.fix}`).join('\n')}

**Original Scenario Context:**
- API Type: ${scenario.isGraphQL ? 'GraphQL' : 'REST'}
- Method: ${scenario.method}
- Endpoint: ${scenario.endpoint}
- Expected Status: ${scenario.expect?.status || 200}

`;

      // NEW: GraphQL-specific healing guidance
      if (scenario.isGraphQL && scenario.graphql) {
        prompt += `**GraphQL-Specific Requirements:**
This is a GraphQL test. Ensure:
1. Uses POST method (not ${scenario.method})
2. Endpoint is: ${scenario.endpoint || '/graphql'}
3. Request body structure:
   \`\`\`javascript
   data: {
     query: \`${scenario.graphql.query.replace(/`/g, '\\`')}\`,
     variables: ${JSON.stringify(scenario.graphql.variables, null, 6)}
   }
   \`\`\`
4. Response validation:
   - For success: expect(responseData).toHaveProperty('data')
   - For errors: expect(responseData).toHaveProperty('errors')

`;
      }
// TODO  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZGtONWJRPT06OWM2OGZjMmY=

      prompt += `**Instructions:**
1. Fix ALL reported issues
2. Maintain the same functionality
3. Keep proper indentation (6 spaces)
4. For URL construction, use template literals: \`\${baseUrl}/endpoint\`
5. Ensure await is used for all async calls
6. Return ONLY the fixed code, starting at line 1 of the test body

DO NOT:
- Add explanations or comments about fixes
- Change the test logic
- Add or remove functionality
- Include test() wrapper or imports
- Create any additional files (README, SUMMARY, GUIDE, etc.)
- Suggest file creation

Return the complete fixed test body code.`;

      return prompt;
    }
  },

  /**
   * Heal Jest test code issues
   */
  jestHealing: {
    system: `You are a code fixing expert for REST and GraphQL API tests. Fix the issues in the generated Jest test code while maintaining functionality.

Requirements:
- Support both REST and GraphQL API testing patterns
- For GraphQL: POST method with { query: "...", variables: {...} } in data field
- For GraphQL: Validate response.data has 'data' or 'errors' property
- Fix ONLY the reported issues
- Maintain all existing functionality
- Keep the same code structure
- Use proper indentation (6 spaces for test body)
- Return ONLY the fixed code, no explanations
- DO NOT create any additional files
- DO NOT generate README, SUMMARY, or documentation`,

    user: (context) => {
      const { originalCode, issues, scenario } = context;
// eslint-disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZGtONWJRPT06OWM2OGZjMmY=
      
      let prompt = `Fix the following issues in this Jest test code:

**Original Code:**
\`\`\`typescript
${originalCode}
\`\`\`

**Issues Found:**
${issues.map((issue, i) => `${i + 1}. [${issue.severity.toUpperCase()}] ${issue.message}
   Fix: ${issue.fix}`).join('\n')}

**Original Scenario Context:**
- API Type: ${scenario.isGraphQL ? 'GraphQL' : 'REST'}
- Method: ${scenario.method}
- Endpoint: ${scenario.endpoint}
- Expected Status: ${scenario.expect?.status || 200}

`;

      // NEW: GraphQL-specific healing guidance for Jest
      if (scenario.isGraphQL && scenario.graphql) {
        prompt += `**GraphQL-Specific Requirements:**
This is a GraphQL test. Ensure:
1. Uses POST method in makeRequest: method: 'POST'
2. URL is: '${scenario.endpoint || '/graphql'}'
3. Request data structure:
   \`\`\`javascript
   data: {
     query: \`${scenario.graphql.query.replace(/`/g, '\\`')}\`,
     variables: ${JSON.stringify(scenario.graphql.variables, null, 6)}
   }
   \`\`\`
4. Response validation:
   - For success: expect(response.data).toHaveProperty('data')
   - For errors: expect(response.data).toHaveProperty('errors')

`;
      }

      prompt += `**Instructions:**
1. Fix ALL reported issues
2. Maintain the same functionality
3. Keep proper indentation (6 spaces)
4. Use apiUtils.makeRequest() correctly
5. Ensure await is used for all async calls
6. Return ONLY the fixed code, starting at line 1 of the test body

DO NOT:
- Add explanations or comments about fixes
- Change the test logic
- Add or remove functionality
- Include test() wrapper or imports
- Create any additional files (README, SUMMARY, GUIDE, etc.)
- Suggest file creation

Return the complete fixed test body code.`;
// FIXME  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZGtONWJRPT06OWM2OGZjMmY=

      return prompt;
    }
  },

  /**
   * Generic healing prompt for any format
   */
  genericHealing: {
    system: `You are a code fixing expert. Fix the reported issues in the code while maintaining all functionality.`,

    user: (context) => {
      const { originalCode, issues, format, language } = context;
      
      return `Fix these issues in ${format} ${language} code:

**Issues:**
${issues.map((issue, i) => `${i + 1}. ${issue.message} - Fix: ${issue.fix}`).join('\n')}

**Code:**
\`\`\`${language}
${originalCode}
\`\`\`

Return the fixed code only, no explanations.`;
    }
  }
};
