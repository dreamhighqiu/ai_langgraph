/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// eslint-disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YjJoa1F3PT06ZDc2NGQyMzc=

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);
const copyFile = promisify(fs.copyFile);
const stat = promisify(fs.stat);
const readdir = promisify(fs.readdir);

/**
 * Agent Installer - Handles installation of chatmode files and MCP configuration
 */
class AgentInstaller {
    constructor(options = {}) {
        this.verbose = options.verbose || false;
        this.targetDir = options.targetDir || process.cwd();
        this.sourceDir = options.sourceDir || path.join(__dirname, '..', '..');
    }

    /**
     * Main installation function
     */
    async install() {
        console.log('🚀 Installing Automation Quality Agents...\n');

        try {
            // Step 1: Install chatmode files
            await this.installChatmodeFiles();
            
            // Step 2: Setup MCP configuration
            await this.setupMCPConfiguration();
            
            // Step 3: Show completion message
            this.showCompletionMessage();
            
        } catch (error) {
            console.error('❌ Installation failed:', error.message);
            if (this.verbose) {
                console.error('Stack trace:', error.stack);
            }
            throw error;
        }
    }

    /**
     * Install chatmode files to .github/chatmodes/
     */
    async installChatmodeFiles() {
        console.log('📁 Installing chatmode files...');
        
        const sourceChatmodesDir = path.join(this.sourceDir, 'src', 'chatmodes');
        const targetChatmodesDir = path.join(this.targetDir, '.github', 'chatmodes');
        
        // Create target directory if it doesn't exist
        try {
            await mkdir(targetChatmodesDir, { recursive: true });
        } catch (error) {
            if (error.code !== 'EEXIST') {
                throw new Error(`Failed to create .github/chatmodes directory: ${error.message}`);
            }
        }
        
        // Get list of chatmode files
        let chatmodeFiles;
        try {
            const allFiles = await readdir(sourceChatmodesDir);
            chatmodeFiles = allFiles.filter(file => file.endsWith('.chatmode.md'));
        } catch (error) {
            throw new Error(`Failed to read source chatmodes directory: ${error.message}`);
        }
        
        if (chatmodeFiles.length === 0) {
            console.log('   ⚠️  No chatmode files found to install');
            return;
        }
        
        // Copy each chatmode file
        for (const file of chatmodeFiles) {
            const sourcePath = path.join(sourceChatmodesDir, file);
            const targetPath = path.join(targetChatmodesDir, file);
            
            try {
                await copyFile(sourcePath, targetPath);
                console.log(`   ✅ ${file}`);
            } catch (error) {
                console.error(`   ❌ Failed to copy ${file}: ${error.message}`);
                throw error;
            }
        }
        
        console.log('');
    }

    /**
     * Setup MCP configuration in .vscode/mcp.json
     */
    async setupMCPConfiguration() {
        console.log('⚙️  Setting up MCP configuration...');
        
        const vscodeDir = path.join(this.targetDir, '.vscode');
        const mcpConfigPath = path.join(vscodeDir, 'mcp.json');
// TODO  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YjJoa1F3PT06ZDc2NGQyMzc=
        
        // Create .vscode directory if it doesn't exist
        try {
            await mkdir(vscodeDir, { recursive: true });
        } catch (error) {
            if (error.code !== 'EEXIST') {
                throw new Error(`Failed to create .vscode directory: ${error.message}`);
            }
        }
        
        // Check if mcp.json already exists
        let existingConfig = null;
        let configExists = false;
        
        try {
            await stat(mcpConfigPath);
            configExists = true;
            console.log('   📋 Found existing .vscode/mcp.json');
            
            const configContent = await readFile(mcpConfigPath, 'utf8');
            existingConfig = JSON.parse(configContent);
            
        } catch (error) {
            if (error.code === 'ENOENT') {
                console.log('   📋 Creating new .vscode/mcp.json');
                configExists = false;
            } else if (error instanceof SyntaxError) {
                throw new Error(`Existing mcp.json is malformed: ${error.message}`);
            } else {
                throw new Error(`Failed to read existing mcp.json: ${error.message}`);
            }
        }
// eslint-disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YjJoa1F3PT06ZDc2NGQyMzc=
        
        // Create new server configuration
        const newServerConfig = {
            type: "stdio",
            command: "npx",
            args: ["@Automation-quality/mcp-server@latest"],
            cwd: "${workspaceFolder}",
            env: {
                OUTPUT_DIR: "./api-test-reports"
            }
        };
        
        let finalConfig;
        
        if (configExists && existingConfig) {
            // Handle existing configuration
            await this.handleExistingMCPConfig(existingConfig, newServerConfig, mcpConfigPath);
            return;
        } else {
            // Create new configuration
            finalConfig = {
                servers: {
                    "Automation-quality": newServerConfig
                },
                inputs: []
            };
        }
        
        // Write the configuration
        try {
            await writeFile(mcpConfigPath, JSON.stringify(finalConfig, null, 2), 'utf8');
            console.log('   ✅ MCP configuration created');
        } catch (error) {
            throw new Error(`Failed to write mcp.json: ${error.message}`);
        }
        
        console.log('');
    }

    /**
     * Handle existing MCP configuration
     */
    async handleExistingMCPConfig(existingConfig, newServerConfig, mcpConfigPath) {
        // Ensure servers object exists
        if (!existingConfig.servers) {
            existingConfig.servers = {};
        }
        
        // Check if Automation-quality server already exists
        if (existingConfig.servers['Automation-quality']) {
            console.log('   🔍 Found existing "Automation-quality" server configuration');
            
            const existingServer = existingConfig.servers['Automation-quality'];
            console.log('   Current configuration:');
            console.log('   ', JSON.stringify(existingServer, null, 4));
            console.log('   \n   Proposed configuration:');
            console.log('   ', JSON.stringify(newServerConfig, null, 4));
            
            // For now, we'll update automatically with backup
            // In a real implementation, you might want to prompt the user
            console.log('   💾 Creating backup and updating configuration...');
// TODO  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YjJoa1F3PT06ZDc2NGQyMzc=
            
            // Create backup
            const backupPath = `${mcpConfigPath}.backup.${new Date().toISOString().replace(/[:.]/g, '-')}`;
            await writeFile(backupPath, JSON.stringify(existingConfig, null, 2), 'utf8');
            console.log(`   📄 Backup created: ${path.basename(backupPath)}`);
        }
        
        // Update configuration
        const updatedConfig = {
            ...existingConfig,
            servers: {
                ...existingConfig.servers,
                'Automation-quality': newServerConfig
            },
            inputs: existingConfig.inputs || []
        };
        
        // Write updated configuration
        try {
            await writeFile(mcpConfigPath, JSON.stringify(updatedConfig, null, 2), 'utf8');
            console.log('   ✅ MCP configuration updated');
        } catch (error) {
            throw new Error(`Failed to update mcp.json: ${error.message}`);
        }
    }

    /**
     * Show completion message with next steps
     */
    showCompletionMessage() {
        console.log('🎉 Installation complete!\n');
        
        console.log('📁 Chatmode files installed to:');
        console.log('   → .github/chatmodes/🌐 api-planner.chatmode.md');
        console.log('   → .github/chatmodes/🌐 api-generator.chatmode.md');
        console.log('   → .github/chatmodes/🌐 api-healer.chatmode.md\n');
        
        console.log('⚙️  MCP configuration updated:');
        console.log('   → .vscode/mcp.json (Automation-quality server added/updated)\n');
        
        console.log('🚀 Next steps:');
        console.log('   1. Restart VS Code to reload MCP configuration');
        console.log('   2. Use agents in GitHub Copilot Chat:');
        console.log('      • @🌐 api-planner - Create comprehensive API test plans');
        console.log('      • @🌐 api-generator - Generate executable API tests');
        console.log('      • @🌐 api-healer - Debug and fix failing API tests');
        console.log('   3. Start with: "@🌐 api-planner help me create a test plan"\n');
        
        console.log('📚 For more information, visit: https://github.com/uppadhyayraj/Automation-quality-mcp-server');
    }

    /**
     * Rollback installation (future feature)
     */
    async rollback() {
        console.log('🔄 Rollback functionality will be implemented in a future version');
        // TODO: Implement rollback functionality
    }
}

module.exports = AgentInstaller;
