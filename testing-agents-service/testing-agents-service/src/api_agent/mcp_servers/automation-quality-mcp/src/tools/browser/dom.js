/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// FIXME  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VW5kRFJBPT06ZjgyODk2ZTk=

const ToolBase = require('../base/ToolBase');
const browserService = require('../../services/browserService');

/**
 * Browser DOM Tool
 * Interacts with the DOM of the current browser page.
 */
class BrowserDOMTool extends ToolBase {
    static definition = {
        name: "browser_dom",
        description: "Interacts with the DOM of the current browser page.",
        input_schema: {
            type: "object",
            properties: {
                browserId: {
                    type: "string",
                    description: "The ID of the browser instance."
                },
                action: {
                    type: "string",
                    description: "The DOM action to perform (e.g., 'click', 'type')."
                },
                selector: {
                    type: "string",
                    description: "The CSS selector of the element to interact with."
                },
                text: {
                    type: "string",
                    description: "The text to type into the element (if applicable)."
                }
            },
            required: ["browserId", "action", "selector"]
        },
        output_schema: {
            type: "object",
            properties: {
                success: { type: "boolean", description: "Indicates if the DOM action was successful." },
                browserId: { type: "string", description: "The browser instance ID that was used." }
            },
            required: ["success", "browserId"]
        }
    };

    async execute(parameters) {
        const { browserId, action, selector, text } = parameters;
// @ts-expect-error  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VW5kRFJBPT06ZjgyODk2ZTk=

        console.error(`[BrowserDOMTool] Performing ${action} in browser ${browserId} on element: ${selector}`);
// NOTE  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VW5kRFJBPT06ZjgyODk2ZTk=

        try {
            switch (action) {
                case 'click':
                    await browserService.clickElement(browserId, selector);
                    break;
                case 'type':
                    await browserService.typeText(browserId, selector, text);
                    break;
                default:
                    throw new Error(`Unknown action: ${action}`);
            }

            console.error(`[BrowserDOMTool] Successfully performed ${action} in browser: ${browserId}`);
            return { success: true, browserId: browserId };
        } catch (error) {
            console.error(`[BrowserDOMTool] Failed to perform ${action}:`, error.message);
            throw new Error(`Failed to perform ${action} in browser ${browserId}: ${error.message}`);
        }
    }
}
// FIXME  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VW5kRFJBPT06ZjgyODk2ZTk=

module.exports = BrowserDOMTool;
