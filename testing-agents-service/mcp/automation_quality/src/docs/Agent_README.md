# 🌐 API Testing Agents - User Guide

Welcome to the **Automation Quality API Testing Agents**! These powerful AI agents help you plan, generate, and heal API tests automatically, similar to Playwright's agents but specifically designed for comprehensive API testing.

## 🎯 Overview

The API Testing Agents provide a complete workflow for API quality assurance:

1. **🌐 API Planner Agent** - Analyzes API schemas and creates comprehensive test plans
2. **🌐 API Generator Agent** - Generates executable tests (Playwright, Jest, Postman)
3. **🌐 API Healer Agent** - Debugs and fixes failing API tests automatically

## 🚀 Getting Started

### Prerequisites
- **GitHub Copilot** with MCP server support
- **Node.js 14+** for running generated tests
- **API documentation** (OpenAPI/Swagger preferred) or API endpoint access

### Quick Setup
1. Ensure the Automation Quality MCP Server is configured in your environment
2. Start a conversation with GitHub Copilot
3. Use the agent prompts below to activate the appropriate agent

---

## 🌐 API Planner Agent

**Purpose**: Analyze API schemas and create comprehensive test plans covering functional, security, and edge case testing.

### When to Use the API Planner Agent

#### Scenario 1: You have an OpenAPI/Swagger schema
```
I need to create a comprehensive test plan for my REST API. I have the OpenAPI schema at https://petstore.swagger.io/v2/swagger.json - can you analyze it and generate a detailed test plan covering all endpoints, authentication, and edge cases?
```

#### Scenario 2: You have API documentation but no schema
```
I have a user management API at https://api.myapp.com with endpoints for registration, login, user CRUD operations, and admin functions. Can you help me create a comprehensive test plan that covers happy paths, error scenarios, and security testing?
```

#### Scenario 3: GraphQL API planning
```
I have a GraphQL API with user, product, and order operations. Can you help me create a test plan that covers queries, mutations, authentication, and data validation scenarios?
```

### Example Agent Prompts

**Basic Schema Analysis:**
```
Please use the API Planner agent to analyze my OpenAPI schema and create a test plan. The schema is at https://api.example.com/docs/swagger.json and I want to include security testing and error handling scenarios.
```

**Custom Test Categories:**
```
I need an API test plan for my e-commerce API. Please focus on functional testing, security testing, and integration scenarios. The API base URL is https://shop-api.example.com and I have the schema content ready to share.
```

**Manual API Exploration:**
```
I don't have an API schema but need to create a test plan for my authentication API. The endpoints are /login, /register, /refresh-token, and /logout. Can you help me explore these endpoints and create a comprehensive test plan?
```

### Expected Outputs
- **Comprehensive test plan** in markdown format
- **Endpoint analysis** with request/response examples
- **Security test scenarios** (SQL injection, XSS, auth bypasses)
- **Edge case coverage** (boundary conditions, error handling)
- **Integration test workflows** with request chaining

---

## 🌐 API Generator Agent

**Purpose**: Convert test plans into executable tests in multiple formats (Playwright, Jest, Postman collections).

### When to Use the API Generator Agent

#### Scenario 1: Generate from existing test plan
```
I have an API test plan in ./docs/api-test-plan.md. Can you generate executable Jest tests and Postman collections from this plan? I want to include authentication setup and use https://api.myapp.com as the base URL.
```

#### Scenario 2: Generate specific test format
```
Please use the API Generator agent to create Playwright tests from my test plan. I need the tests to include proper authentication handling and session management for my REST API testing.
```

#### Scenario 3: Batch generation for CI/CD
```
I need to generate all test formats (Jest, Playwright, and Postman) from my API test plan for our CI/CD pipeline. The tests should include setup/teardown and be ready for automated execution.
```

### Example Agent Prompts

**Complete Test Suite Generation:**
```
Please use the API Generator agent to create a complete test suite from my test plan. Generate Jest tests, Playwright tests, and Postman collections. Include authentication setup and organize the tests for easy maintenance.
```

**Framework-Specific Generation:**
```
I need Jest API tests generated from my test plan with proper axios configuration, error handling, and session management. The base URL should be configurable via environment variables.
```

**Integration with Existing Tests:**
```
Can you generate Playwright API tests that integrate with my existing test structure? I want to add these to my current test suite without conflicts.
```

### Expected Outputs
- **Executable test files** in requested formats
- **Test utilities and helpers** for authentication and data management
- **Configuration files** for test runners
- **Setup/teardown scripts** for test environment management
- **Documentation** for running and maintaining tests

---

## 🌐 API Healer Agent

**Purpose**: Debug and automatically fix failing API tests using intelligent analysis and healing strategies.

### When to Use the API Healer Agent

#### Scenario 1: Tests failing after API changes
```
My API tests in ./tests/api-tests.spec.js are failing after our latest API deployment. Can you use the API Healer agent to analyze the failures and fix the tests automatically? I want to keep backups of the original files.
```

#### Scenario 2: Authentication issues
```
My Jest tests are failing with 401 errors - it seems like our authentication method changed. Can you help heal these tests and update the auth configuration?
```

#### Scenario 3: Bulk test healing
```
I have multiple test files that are broken after API schema changes. Can you use the API Healer to fix all tests in my ./tests/ directory and provide a report of what was changed?
```

### Example Agent Prompts

**Automated Healing:**
```
Please use the API Healer agent to fix my failing API tests. The test files are in ./tests/ and I want automatic healing with backup creation. Focus on authentication and endpoint issues.
```

**Analysis Before Fixing:**
```
My API tests are failing and I need to understand why before applying fixes. Can you analyze the test failures first and then suggest healing strategies?
```

**Targeted Healing:**
```
I have specific authentication failures in my tests. Please use the API Healer to focus on auth-repair and endpoint-fix strategies only.
```

### Expected Outputs
- **Detailed failure analysis** with categorized error types
- **Automatically fixed test files** with applied healing strategies
- **Backup files** of original tests before modifications
- **Healing report** showing what was changed and why
- **Recommendations** for preventing similar issues

---

## 🔄 Complete Workflow Examples

### Workflow 1: From Schema to Working Tests
```
I have a new API with OpenAPI schema at https://api.newproject.com/docs/swagger.json. 

1. First, please use the API Planner agent to analyze the schema and create a comprehensive test plan
2. Then use the API Generator agent to create Jest and Postman tests from the plan
3. Finally, help me set up the test environment and run the tests

I want full coverage including security testing and edge cases.
```

### Workflow 2: Fixing Legacy Tests
```
I inherited a project with broken API tests in ./legacy-tests/. The API has evolved but the tests weren't updated.

1. Use the API Healer agent to analyze what's broken
2. Automatically fix the tests where possible
3. For unfixable issues, help me understand what manual changes are needed
4. Generate a report of all changes made

Please create backups before making any changes.
```

### Workflow 3: Building Test Suite from Scratch
```
I need to build a complete API test suite for my microservices architecture. I have 3 services with different authentication methods.

1. Help me plan comprehensive test scenarios for each service
2. Generate tests that work together for integration testing
3. Set up proper test data management and cleanup
4. Create a maintenance strategy for keeping tests updated

The services are: user-service, order-service, and payment-service.
```

## 🛠️ Advanced Usage Tips

### 1. Combining Agents Effectively
```
Can you create a complete API testing solution by:
1. Using the API Planner to analyze my OpenAPI schema
2. Generating comprehensive test suites with the API Generator
3. Setting up automated healing with the API Healer for CI/CD
```

### 2. Custom Configuration
```
I need tests generated with specific configurations:
- Custom authentication headers
- Environment-specific base URLs
- Special error handling for rate limiting
- Integration with my existing test framework

Can you help customize the generated tests?
```

### 3. Maintenance and Updates
```
My API evolves frequently. Can you help me set up a process where:
1. Schema changes trigger automatic test plan updates
2. Tests are regenerated when needed
3. Healing runs automatically in CI/CD
4. I get reports on what changed and why
```

## 🎯 Best Practices

### For API Planner Agent:
- **Provide complete schemas** when available for best results
- **Specify security requirements** explicitly
- **Include business logic context** for better test scenarios
- **Request specific test categories** if you have preferences

### For API Generator Agent:
- **Choose appropriate test format** for your use case
- **Specify authentication details** early in the process
- **Include environment configuration** requirements
- **Request helper utilities** for complex scenarios

### For API Healer Agent:
- **Always enable backups** when healing tests
- **Start with analysis-only mode** for critical tests
- **Specify healing strategies** if you know the issue type
- **Review healing reports** to understand changes

## 🔧 Troubleshooting

### Common Issues and Solutions

**Agent Not Responding:**
```
The API Planner agent isn't working - can you help me troubleshoot? I'm trying to analyze an OpenAPI schema but getting errors.
```

**Tests Not Generating Properly:**
```
The generated tests from the API Generator don't match my test plan. Can you help me understand what went wrong and regenerate them correctly?
```

**Healing Not Working:**
```
The API Healer made changes but my tests are still failing. Can you analyze what additional fixes are needed?
```

## 📚 Additional Resources

### Related Tools
- Use `api_request` for manual API testing and validation
- Use `api_session_status` to monitor test execution
- Use `api_session_report` to generate detailed test reports

### Integration Examples
```
Can you show me how to integrate these generated tests with:
1. GitHub Actions for CI/CD
2. Jest for local development
3. Postman for manual testing
4. Playwright for browser-based API testing
```

---

## 🤝 Getting Help

If you need assistance with any of these agents:

1. **Be specific** about your API type, authentication, and requirements
2. **Provide context** about your existing test setup
3. **Share error messages** when things don't work as expected
4. **Ask for explanations** of generated code or healing decisions

**Example Help Request:**
```
I'm new to API testing and have a REST API with JWT authentication. Can you walk me through using all three agents to create a complete testing solution? I want to understand each step and the generated code.
```

Remember: These agents are designed to work together seamlessly. Start with planning, move to generation, and use healing to maintain your tests as your API evolves!
