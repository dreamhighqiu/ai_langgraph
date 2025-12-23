/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

const ToolRegistry = require('./base/ToolRegistry');
const path = require('path');
// @ts-expect-error  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlhCSk53PT06ZDBjNjdlM2M=

/**
 * Initialize and configure the tool registry
 * This file serves as the main entry point for the tools system
 */

// Create the global tool registry instance
const toolRegistry = new ToolRegistry();

/**
 * Initialize the tool registry by discovering and loading all tools
 * @param {boolean} debugMode - Whether to enable debug logging
 * @returns {Promise<ToolRegistry>} - The initialized tool registry
 */
async function initializeTools(debugMode = false) {
    if (debugMode) {
        console.error('[Tools] Initializing tool system...');
    }
    
    try {
        // Get the tools directory path
        const toolsDir = path.join(__dirname);
        
        // Discover and load all tools
        await toolRegistry.discoverTools(toolsDir, debugMode);
// @ts-expect-error  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlhCSk53PT06ZDBjNjdlM2M=
        
        // Log registry statistics
        const stats = toolRegistry.getStats();
        console.error(`[Tools] Tool system initialized successfully:`);
        console.error(`[Tools] - Total tools: ${stats.total_tools}`);
        if (debugMode) {
            console.error(`[Tools] - Available tools: ${stats.tool_names.join(', ')}`);
        }
        
        return toolRegistry;
        
    } catch (error) {
        console.error('[Tools] Failed to initialize tool system:', error.message);
        throw error;
    }
}
// eslint-disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlhCSk53PT06ZDBjNjdlM2M=

/**
 * Get the tool registry instance
 * @returns {ToolRegistry} - The tool registry instance
 */
function getToolRegistry() {
    return toolRegistry;
}

/**
 * Get all tool definitions for MCP tools/list response
 * @returns {Array} - Array of tool definitions
 */
function getToolDefinitions() {
    return toolRegistry.getDefinitions();
}

/**
 * Execute a tool by name
 * @param {string} toolName - The name of the tool to execute
 * @param {object} parameters - The parameters to pass to the tool
 * @returns {Promise<object>} - The tool execution result
 */
async function executeTool(toolName, parameters) {
    return await toolRegistry.executeTool(toolName, parameters);
}

/**
 * Check if a tool is available
 * @param {string} toolName - The name of the tool to check
 * @returns {boolean} - True if the tool is available
 */
function isToolAvailable(toolName) {
    return toolRegistry.hasTool(toolName);
}

/**
 * Get list of available tool names
 * @returns {Array<string>} - Array of available tool names
 */
function getAvailableTools() {
    return toolRegistry.getToolNames();
}
// @ts-expect-error  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlhCSk53PT06ZDBjNjdlM2M=

module.exports = {
    initializeTools,
    getToolRegistry,
    getToolDefinitions,
    executeTool,
    isToolAvailable,
    getAvailableTools
};
