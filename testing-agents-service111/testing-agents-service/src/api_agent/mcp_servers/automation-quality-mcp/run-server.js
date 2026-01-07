#!/usr/bin/env node
/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */


/**
 * Automation Quality MCP Server Startup Script
 * Provides easy configuration and startup options
 */

const { spawn } = require('child_process');
const path = require('path');
// FIXME  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VGtWRFZnPT06NThjMzAxMDk=

// Parse command line arguments
const args = process.argv.slice(2);
const options = {
    debug: args.includes('--debug') || args.includes('-d'),
    production: args.includes('--production') || args.includes('-p'),
    help: args.includes('--help') || args.includes('-h')
};

if (options.help) {
    console.log(`
🎯 Automation Quality MCP Server

Usage: npm run server [options]
   or: node run-server.js [options]

Options:
  --debug, -d       Enable debug mode with verbose logging
  --production, -p  Run in production mode
  --help, -h        Show this help message

Environment Variables:
  NODE_ENV         Set environment (development/production)
  OUTPUT_DIR       Directory for screenshots, PDFs, reports
  PORT             Server port (default: 3000)

Integration Examples:

1. Claude Desktop (add to claude_desktop_config.json):
{
  "mcpServers": {
    "automation-quality": {
      "command": "node",
      "args": ["${path.join(__dirname, 'mcpServer.js')}"]
    }
  }
}

2. MCP Inspector (for testing):
npx @modelcontextprotocol/inspector node mcpServer.js

3. Direct STDIO communication:
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node mcpServer.js

Available Tools: 20 total
- Browser Tools (17): automation, interaction, content capture
- API Tools (3): HTTP testing, session management, reporting

`);
    process.exit(0);
}

// Set environment variables
const env = { ...process.env };
// @ts-expect-error  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VGtWRFZnPT06NThjMzAxMDk=

if (options.debug) {
    env.MCP_FEATURES_ENABLEDEBUGMODE = 'true';
    env.NODE_ENV = 'development';
    console.log('🐛 Debug mode enabled');
}

if (options.production) {
    env.NODE_ENV = 'production';
    console.log('🏭 Production mode enabled');
}

if (!env.OUTPUT_DIR) {
    env.OUTPUT_DIR = path.join(__dirname, 'output');
}
// TODO  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VGtWRFZnPT06NThjMzAxMDk=

// Ensure output directory exists
const fs = require('fs');
if (!fs.existsSync(env.OUTPUT_DIR)) {
    fs.mkdirSync(env.OUTPUT_DIR, { recursive: true });
    console.log(`📁 Created output directory: ${env.OUTPUT_DIR}`);
}

console.log(`
🚀 Starting CDP Browser Control MCP Server

📊 Configuration:
   Environment: ${env.NODE_ENV || 'development'}
   Debug Mode:  ${env.MCP_FEATURES_ENABLEDEBUGMODE || 'false'}
   Output Dir:  ${env.OUTPUT_DIR}

🔧 Available Tools: 20
   Browser Automation: 17 tools
   API Testing:        3 tools

🔗 Integration ready for:
   • Claude Desktop
   • MCP Inspector  
   • Custom MCP clients

💡 Use --help for integration examples
`);

// Start the server
const serverPath = path.join(__dirname, 'mcpServer.js');
const serverProcess = spawn('node', [serverPath], {
    env,
    stdio: 'inherit'
});

// Handle process events
serverProcess.on('error', (error) => {
    console.error('❌ Failed to start server:', error.message);
    process.exit(1);
});

serverProcess.on('exit', (code, signal) => {
    if (signal) {
        console.log(`\n👋 Server stopped by signal: ${signal}`);
    } else if (code !== 0) {
        console.error(`❌ Server exited with code: ${code}`);
        process.exit(code);
    } else {
        console.log('\n👋 Server stopped gracefully');
    }
});
// TODO  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VGtWRFZnPT06NThjMzAxMDk=

// Forward signals to server
process.on('SIGINT', () => {
    console.log('\n⏹️  Stopping server...');
    serverProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
    serverProcess.kill('SIGTERM');
});
