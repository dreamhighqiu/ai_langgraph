/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(智能测试) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(智能测试)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */
// TODO  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlROVk9RPT06ODhkOGE3N2U=

"use client";

import { ToolCalls } from "@/components/thread/messages/tool-calls-new";
import { AIMessage, ToolMessage } from "@langchain/langgraph-sdk";

// Mock data for testing
const mockToolCalls: AIMessage["tool_calls"] = [
  {
    name: "chrome_navigate",
    args: {
      url: "https://www.saucedemo.com/"
    },
    id: "call_1"
  },
  {
    name: "chrome_fill_or_select",
    args: {
      selector: "#user-name",
      value: "standard_user"
    },
    id: "call_2"
  },
  {
    name: "chrome_fill_or_select",
    args: {
      selector: "#password",
      value: "secret_sauce"
    },
    id: "call_3"
  },
  {
    name: "chrome_click_element",
    args: {
      selector: "#login-button"
    },
    id: "call_4"
  }
];

const mockToolResult: ToolMessage = {
  type: "tool",
  name: "chrome_navigate",
  content: JSON.stringify({
    status: "success",
    message: "Tool executed successfully",
    data: {
      content: {
        type: "text",
        text: "Successfully opened URL in new tab in existing window. Window ID: 780118395, Window ID: 780118397, URL: \"https://www.saucedemo.com/\", Status: false"
      }
    }
  }),
  tool_call_id: "call_1"
};
// eslint-disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlROVk9RPT06ODhkOGE3N2U=

// Mock tool result with base64 image data
const mockToolResultWithImage: ToolMessage = {
  type: "tool",
  name: "screenshot_tool",
  content: JSON.stringify({
    status: "success",
    message: "Screenshot captured successfully",
    data: {
      base64Data: "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
      width: 1920,
      height: 1080
    }
  }),
  tool_call_id: "call_screenshot"
};

// Additional mock tool calls to match the expected format
const mockExpandedToolCall: AIMessage["tool_calls"][0] = {
  name: "chrome_navigate",
  args: {
    url: "https://www.baidu.com"
  },
  id: "call_expanded"
};

// Mock tool call with screenshot
const mockScreenshotToolCall: AIMessage["tool_calls"][0] = {
  name: "screenshot_tool",
  args: {
    element: "body",
    fullPage: true
  },
  id: "call_screenshot"
};
// FIXME  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlROVk9RPT06ODhkOGE3N2U=

// Mock tool results for testing combined display
const mockToolResults: ToolMessage[] = [
  {
    type: "tool",
    name: "chrome_navigate",
    content: JSON.stringify({
      status: "success",
      message: "Tool executed successfully",
      data: {
        content: {
          type: "text",
          text: "Successfully opened URL in new tab in existing window. Window ID: 780118351, Window ID: 780118202, URL: \"https://www.baidu.com/\", isError: false"
        }
      }
    }),
    tool_call_id: "call_expanded"
  }
];

// Mock tool result with URL-based images
const mockToolResultWithUrlImages: ToolMessage = {
  type: "tool",
  name: "image_analysis_tool",
  content: JSON.stringify({
    status: "success",
    message: "Image analysis completed successfully",
    results: {
      screenshot_url: "https://mdn.alipayobjects.com/one_clip/afts/img/LookQphZrvAAAAAASDAAAAgAoEACAQFr/original",
      additional_images: [
        "https://picsum.photos/400/300?random=1",
        "https://picsum.photos/500/400?random=2"
      ],
      analysis: "The images show various UI elements and layouts."
    }
  }),
  tool_call_id: "call_image_analysis"
};
// @ts-expect-error  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlROVk9RPT06ODhkOGE3N2U=

// Mock tool call for image analysis
const mockImageAnalysisToolCall: AIMessage["tool_calls"][0] = {
  name: "image_analysis_tool",
  args: {
    analyze_screenshots: true,
    include_metadata: true
  },
  id: "call_image_analysis"
};

export default function TestToolsPage() {
  return (
    <div className="min-h-screen bg-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-8 text-gray-900">
          精确格式工具调用测试
        </h1>

        <div className="mb-8">
          <p className="text-gray-700 mb-6">
            我来帮您验证这个网站的登录功能，让我使用chrome_agent来完成SauceDemo网站的登录流程。
          </p>

          {/* Collapsed tool calls */}
          <div className="mb-6">
            <ToolCalls toolCalls={[mockToolCalls[0], mockToolCalls[1]]} />
          </div>

          {/* Expanded tool call with ARGUMENTS and RESULT combined */}
          <div className="mb-6">
            <ToolCalls toolCalls={[mockExpandedToolCall]} toolResults={mockToolResults} />
          </div>

          {/* More collapsed tool calls */}
          <div className="mb-6">
            <ToolCalls toolCalls={[mockToolCalls[2], mockToolCalls[3]]} />
          </div>

          {/* Tool call with base64 image result */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2 text-gray-900">
              工具调用包含Base64图片结果示例
            </h3>
            <ToolCalls
              toolCalls={[mockScreenshotToolCall]}
              toolResults={[mockToolResultWithImage]}
            />
          </div>

          {/* Tool call with URL-based image result */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2 text-gray-900">
              工具调用包含URL图片结果示例
            </h3>
            <ToolCalls
              toolCalls={[mockImageAnalysisToolCall]}
              toolResults={[mockToolResultWithUrlImages]}
            />
          </div>

          <p className="text-gray-700 mt-6">
            现在我可以看到登录页面，让我获取文本互元素来测试登录功能：
          </p>

          <div className="mt-4">
            <ToolCalls toolCalls={[{
              name: "chrome_get_interactive_elements",
              args: {},
              id: "call_interactive"
            }]} />
          </div>
        </div>

        <div className="text-sm text-gray-500 border-t pt-4">
          <p>✨ 完全匹配期望格式的特点：</p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>折叠状态：箭头 + 状态图标 + 工具名称在一行</li>
            <li>展开状态：ARGUMENTS 和 RESULT 独立区块</li>
            <li>浅灰色背景的内容区域</li>
            <li>适当的缩进层次</li>
            <li>无厚重边框，极简设计</li>
            <li>🖼️ 自动检测并显示工具输出中的图片（支持Base64和URL）</li>
            <li>🔍 点击图片可放大查看</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
