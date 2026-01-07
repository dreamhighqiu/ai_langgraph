/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// TODO  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UVhkQ1V3PT06NTU0NWJlMmQ=

/**
 * Validation Rules for Generated Test Code
 * 
 * These rules validate generated test code before writing to files.
 * Catches common issues and triggers healing if needed.
 */
// @ts-expect-error  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UVhkQ1V3PT06NTU0NWJlMmQ=

module.exports = {
  /**
   * Validate Playwright test code
   */
  playwright: {
    /**
     * Check if code has required imports
     */
    hasRequiredImports: (code, language) => {
      if (language === 'typescript') {
        return code.includes('import { test, expect }') || code.includes("import { test, expect }");
      }
      return code.includes('require(') || !code.includes('import');
    },

    /**
     * Check if code uses proper async/await
     */
    hasProperAsync: (code) => {
      if (code.includes('request.')) {
        return code.includes('await request.');
      }
      return true;
    },

    /**
     * Check if code has proper URL construction
     */
    hasProperUrlConstruction: (code) => {
      // Should use template literals with ${baseUrl}, not string concatenation
      const hasTemplateUrl = code.includes('`${baseUrl}') || code.includes("'http");
      const hasWrongUrl = code.includes("'${baseUrl}"); // This is the escaping bug!
      
      return hasTemplateUrl && !hasWrongUrl;
    },

    /**
     * Check if code has assertions
     */
    hasAssertions: (code) => {
      return code.includes('expect(') && code.includes('.toBe(');
    },

    /**
     * Check for common syntax errors
     */
    noSyntaxErrors: (code) => {
      // Basic checks - full validation would require parsing
      const balancedBraces = (code.match(/\{/g) || []).length === (code.match(/\}/g) || []).length;
      const balancedParens = (code.match(/\(/g) || []).length === (code.match(/\)/g) || []).length;
      const balancedBrackets = (code.match(/\[/g) || []).length === (code.match(/\]/g) || []).length;
      
      return balancedBraces && balancedParens && balancedBrackets;
    },

    /**
     * Check if GraphQL request is properly structured
     */
    hasGraphQLRequestStructure: (code) => {
      // If code contains GraphQL query, check structure
      if (code.includes('query:') || code.includes('mutation:') || code.includes('subscription:')) {
        const hasQueryField = code.includes('query:') || code.includes('mutation:');
        const hasDataObject = code.includes('data: {') && hasQueryField;
        return hasQueryField && hasDataObject;
      }
      return true; // Not GraphQL, skip
    },

    /**
     * Check if GraphQL response validation is present
     */
    hasGraphQLResponseValidation: (code) => {
      // If it's a GraphQL test, must validate data or errors
      if (code.includes('query:') || code.includes('mutation:')) {
        const hasDataCheck = code.includes('.toHaveProperty(\'data\')');
        const hasErrorsCheck = code.includes('.toHaveProperty(\'errors\')');
        return hasDataCheck || hasErrorsCheck;
      }
      return true; // Not GraphQL
    },

    /**
     * Run all validations
     */
    validateAll: (code, language, isGraphQL) => {
      const issues = [];
      
      // Note: We're validating generated TEST BODY code, not full files
      // So we don't check for imports in the body
      
      if (!module.exports.playwright.hasProperAsync(code)) {
        issues.push({
          severity: 'error',
          message: 'Missing await keyword for async API calls',
          fix: 'Add await before request.* calls'
        });
      }
      
      if (!module.exports.playwright.hasProperUrlConstruction(code)) {
        issues.push({
          severity: 'critical',
          message: 'Incorrect URL construction - template literal escaping issue',
          fix: 'Use backticks for template literals: `${baseUrl}/endpoint` not \'${baseUrl}/endpoint\''
        });
      }
      
      if (!module.exports.playwright.hasAssertions(code)) {
        issues.push({
          severity: 'warning',
          message: 'No assertions found in test',
          fix: 'Add expect() assertions to validate response'
        });
      }
      
      if (!module.exports.playwright.noSyntaxErrors(code)) {
        issues.push({
          severity: 'error',
          message: 'Possible syntax error - unbalanced brackets/braces/parens',
          fix: 'Check code for balanced brackets, braces, and parentheses'
        });
      }
      
      // NEW: GraphQL-specific validations
      if (isGraphQL) {
        if (!module.exports.playwright.hasGraphQLRequestStructure(code)) {
          issues.push({
            severity: 'error',
            message: 'GraphQL request structure incorrect',
            fix: 'Use: data: { query: "...", variables: {...} }'
          });
        }
        
        if (!module.exports.playwright.hasGraphQLResponseValidation(code)) {
          issues.push({
            severity: 'warning',
            message: 'Missing GraphQL response validation',
            fix: 'Add: expect(responseData).toHaveProperty(\'data\') or .toHaveProperty(\'errors\')'
          });
        }
      }
      
      return {
        valid: issues.filter(i => i.severity === 'error' || i.severity === 'critical').length === 0,
        issues: issues
      };
    }
  },

  /**
   * Validate Jest test code
   */
  jest: {
    /**
     * Check if code uses API utils correctly
     */
    hasProperApiCall: (code) => {
      return code.includes('apiUtils.makeRequest') && code.includes('await');
    },

    /**
     * Check if code has assertions
     */
    hasAssertions: (code) => {
      return code.includes('expect(');
    },

    /**
     * Check for common syntax errors
     */
    noSyntaxErrors: (code) => {
      const balancedBraces = (code.match(/\{/g) || []).length === (code.match(/\}/g) || []).length;
      const balancedParens = (code.match(/\(/g) || []).length === (code.match(/\)/g) || []).length;
      const balancedBrackets = (code.match(/\[/g) || []).length === (code.match(/\]/g) || []).length;
      
      return balancedBraces && balancedParens && balancedBrackets;
    },

    /**
     * Check if GraphQL request is properly structured (Jest/axios style)
     */
    hasGraphQLRequestStructure: (code) => {
      if (code.includes('query:') || code.includes('mutation:') || code.includes('subscription:')) {
        const hasQueryField = code.includes('query:') || code.includes('mutation:');
        const hasDataObject = code.includes('data: {') && hasQueryField;
        return hasQueryField && hasDataObject;
      }
      return true;
    },

    /**
     * Check if GraphQL response validation is present (Jest style)
     */
    hasGraphQLResponseValidation: (code) => {
      if (code.includes('query:') || code.includes('mutation:')) {
        const hasDataCheck = code.includes('.toHaveProperty(\'data\')');
        const hasErrorsCheck = code.includes('.toHaveProperty(\'errors\')');
        return hasDataCheck || hasErrorsCheck;
      }
      return true;
    },

    /**
     * Run all validations
     */
    validateAll: (code, language, isGraphQL) => {
      const issues = [];
      
      if (!module.exports.jest.hasProperApiCall(code)) {
        issues.push({
          severity: 'error',
          message: 'Missing or incorrect API call using apiUtils.makeRequest',
          fix: 'Use await apiUtils.makeRequest({ method, url, ... })'
        });
      }
      
      if (!module.exports.jest.hasAssertions(code)) {
        issues.push({
          severity: 'warning',
          message: 'No assertions found in test',
          fix: 'Add expect() assertions to validate response'
        });
      }
      
      if (!module.exports.jest.noSyntaxErrors(code)) {
        issues.push({
          severity: 'error',
          message: 'Possible syntax error - unbalanced brackets/braces/parens',
          fix: 'Check code for balanced brackets, braces, and parentheses'
        });
      }
      
      // NEW: GraphQL-specific validations for Jest
      if (isGraphQL) {
        if (!module.exports.jest.hasGraphQLRequestStructure(code)) {
          issues.push({
            severity: 'error',
            message: 'GraphQL request structure incorrect',
            fix: 'Use: data: { query: "...", variables: {...} } in makeRequest()'
          });
        }
        
        if (!module.exports.jest.hasGraphQLResponseValidation(code)) {
          issues.push({
            severity: 'warning',
            message: 'Missing GraphQL response validation',
            fix: 'Add: expect(response.data).toHaveProperty(\'data\') or .toHaveProperty(\'errors\')'
          });
        }
      }
      
      return {
        valid: issues.filter(i => i.severity === 'error' || i.severity === 'critical').length === 0,
        issues: issues
      };
    }
  },

  /**
   * Validate Postman collection structure
   */
  postman: {
    /**
     * Validate collection has required fields
     */
    hasRequiredFields: (collection) => {
      return collection.info && 
             collection.info.name && 
             collection.info.schema &&
             Array.isArray(collection.item);
    },

    /**
     * Validate request structure
     */
    hasValidRequests: (collection) => {
      if (!collection.item || collection.item.length === 0) return false;
      
      // Check first item as sample
      const firstItem = collection.item[0];
      if (firstItem.item && Array.isArray(firstItem.item)) {
        // It's a folder, check its items
        return firstItem.item.every(req => req.name && req.request);
      }
      
      return firstItem.name && firstItem.request;
    },

    /**
     * Run all validations
     */
    validateAll: (collection) => {
      const issues = [];
      
      if (!module.exports.postman.hasRequiredFields(collection)) {
        issues.push({
          severity: 'error',
          message: 'Missing required collection fields (info, name, schema, item)',
          fix: 'Ensure collection has proper Postman v2.1 structure'
        });
      }
      
      if (!module.exports.postman.hasValidRequests(collection)) {
        issues.push({
          severity: 'error',
          message: 'Invalid request structure in collection',
          fix: 'Ensure each request has name and request object'
        });
      }
      
      return {
        valid: issues.filter(i => i.severity === 'error' || i.severity === 'critical').length === 0,
        issues: issues
      };
    }
  },

  /**
   * Get validator for output format
   */
  getValidator: (format) => {
    switch(format) {
      case 'playwright':
        return module.exports.playwright;
      case 'jest':
        return module.exports.jest;
      case 'postman':
        return module.exports.postman;
      default:
        throw new Error(`Unknown format: ${format}`);
    }
  }
};
