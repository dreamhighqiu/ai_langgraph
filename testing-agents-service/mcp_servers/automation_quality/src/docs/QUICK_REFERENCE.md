# 🚀 API Agents Quick Reference

## 📋 Quick Prompts for GitHub Copilot

### 🌐 API Planner Agent

**Schema Analysis:**
```
Use the API Planner agent to analyze my OpenAPI schema at [URL] and create a comprehensive test plan with security testing.
```

**Manual Exploration:**
```
I need an API test plan for my [API_TYPE] API with endpoints [LIST_ENDPOINTS]. Include authentication, error handling, and edge cases.
```

**Custom Categories:**
```
Create an API test plan focusing on [functional/security/performance/integration] testing for my API at [BASE_URL].
```

### 🌐 API Generator Agent

**Complete Generation:**
```
Use the API Generator agent to create [jest/playwright/postman/all] tests from my test plan at [PATH]. Include authentication setup.
```

**Framework Specific:**
```
Generate [FRAMEWORK] tests from my API test plan with proper error handling and session management.
```

**Batch Generation:**
```
Generate all test formats (Jest, Playwright, Postman) from my test plan for CI/CD integration.
```

### 🌐 API Healer Agent

**Auto-Healing:**
```
Use the API Healer agent to fix my failing tests in [PATH]. Create backups and focus on [auth/endpoint/assertion] issues.
```

**Analysis First:**
```
Analyze my failing API tests in [PATH] before applying fixes. I want to understand what's broken.
```

**Bulk Healing:**
```
Heal all API tests in my [DIRECTORY] after API changes. Use all healing strategies and provide a detailed report.
```

## 🔄 Complete Workflows

**New API Testing:**
```
I have a new API with schema at [URL]. Please:
1. Use API Planner to create a test plan
2. Use API Generator to create Jest and Postman tests  
3. Help me set up test execution
```

**Legacy Test Fixing:**
```
My API tests in [PATH] are broken after API updates. Please:
1. Use API Healer to analyze failures
2. Automatically fix what's possible
3. Report what needs manual attention
```

**Complete Test Suite:**
```
Build a complete testing solution for my [DESCRIPTION] API:
1. Plan comprehensive test scenarios
2. Generate executable tests in multiple formats
3. Set up automated healing for maintenance
```

## 🎯 One-Liner Prompts

| Task | Prompt |
|------|--------|
| **Quick Schema Analysis** | `Analyze my OpenAPI schema at [URL] and create a test plan` |
| **Generate Jest Tests** | `Generate Jest tests from my test plan with authentication setup` |
| **Fix Failing Tests** | `Use API Healer to fix my failing tests in [PATH] automatically` |
| **Create Postman Collection** | `Generate a Postman collection from my API test plan` |
| **Security Testing Plan** | `Create an API security test plan for my REST API at [URL]` |
| **Integration Tests** | `Generate integration tests that chain multiple API calls` |
| **Auth Issues** | `Fix authentication failures in my API tests automatically` |
| **All Formats** | `Generate Jest, Playwright, and Postman tests from my plan` |

## 🔧 Variables to Replace

- `[URL]` - Your API schema URL or base URL
- `[PATH]` - File path to your test plan or test files
- `[FRAMEWORK]` - jest, playwright, postman
- `[API_TYPE]` - REST, GraphQL, etc.
- `[LIST_ENDPOINTS]` - Comma-separated list of endpoints
- `[BASE_URL]` - Your API's base URL
- `[DIRECTORY]` - Directory containing test files
- `[DESCRIPTION]` - Brief description of your API

## 📱 Mobile-Friendly Quick Commands

**Plan:** `Create API test plan for [YOUR_API]`
**Generate:** `Generate [FORMAT] tests from plan`  
**Heal:** `Fix failing tests in [PATH]`
**All:** `Complete API testing solution for [API]`
