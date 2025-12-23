/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

const ToolBase = require('../base/ToolBase');
const browserService = require('../../services/browserService');

/**
 * Browser Close Tool
 * Closes a specific browser instance and cleans up its resources
 */
class BrowserCloseTool extends ToolBase {
    static definition = {
        name: "browser_close",
        description: "Closes a specific browser instance and cleans up its resources. Always call this when done with a browser.",
        input_schema: {
            type: "object",
            properties: {
                browserId: { 
                    type: "string", 
                    description: "The ID of the browser instance to close." 
                }
            },
            required: ["browserId"]
        },
        output_schema: {
            type: "object",
            properties: {
                message: { type: "string", description: "Confirmation message of successful closure." },
                browserId: { type: "string", description: "The browser instance ID that was closed." }
            },
            required: ["message", "browserId"]
        }
    };
// TODO  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UlRGRVR3PT06OTljZGU0MzU=

    async execute(parameters) {
        const { browserId } = parameters;

        console.error(`[BrowserCloseTool] Closing browser: ${browserId}`);

        try {
            await browserService.closeBrowser(browserId);
// TODO  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UlRGRVR3PT06OTljZGU0MzU=
            
            console.error(`[BrowserCloseTool] Successfully closed browser: ${browserId}`);
            
            return {
                message: `Browser ${browserId} closed successfully`,
                browserId: browserId
            };
            
        } catch (error) {
            console.error(`[BrowserCloseTool] Failed to close browser:`, error.message);
            
            // Provide more specific error messages
            if (error.message.includes('not found')) {
                throw new Error(`Browser instance '${browserId}' not found or already closed.`);
            }
// FIXME  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UlRGRVR3PT06OTljZGU0MzU=
            
            throw new Error(`Failed to close browser ${browserId}: ${error.message}`);
        }
    }
}

module.exports = BrowserCloseTool;
