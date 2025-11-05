/**
 * 评审反馈展示组件
 * 用于展示 JSON 格式的评审反馈数据
 */

"use client";

import React, { useMemo } from "react";
import { AlertCircle, CheckCircle, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ReviewFeedback {
  passed: boolean;
  feedback: string;
}

interface ReviewFeedbackProps {
  content: string;
}

/**
 * 尝试从内容中解析 JSON 格式的评审反馈
 */
function parseReviewFeedback(content: string): ReviewFeedback | null {
  try {
    // 尝试直接解析 JSON
    const data = JSON.parse(content);
    
    if (data && typeof data === 'object' && ('passed' in data || 'feedback' in data)) {
      return {
        passed: data.passed ?? false,
        feedback: data.feedback ?? '',
      };
    }
    
    return null;
  } catch {
    // 尝试从文本中提取 JSON
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        const data = JSON.parse(jsonMatch[0]);
        if (data && typeof data === 'object' && ('passed' in data || 'feedback' in data)) {
          return {
            passed: data.passed ?? false,
            feedback: data.feedback ?? '',
          };
        }
      } catch {
        return null;
      }
    }
    return null;
  }
}

/**
 * 解析反馈文本，提取问题列表
 */
function parseFeedbackText(text: string): string[] {
  // 按 \n 分割，过滤空行
  const lines = text.split('\\n').filter(line => line.trim());
  
  // 如果没有分割符，尝试按句号分割
  if (lines.length <= 1) {
    return text.split('。').filter(line => line.trim()).map(line => line.trim() + '。');
  }
  
  return lines;
}

/**
 * 提取问题中的用例 ID
 */
function extractTestCaseIds(text: string): string[] {
  const matches = text.match(/TC\d+/g) || [];
  return [...new Set(matches)]; // 去重
}

/**
 * 评审反馈展示组件
 */
export function ReviewFeedback({ content }: ReviewFeedbackProps) {
  const feedback = useMemo(() => parseReviewFeedback(content), [content]);

  if (!feedback) {
    return null;
  }

  const feedbackLines = parseFeedbackText(feedback.feedback);
  const allTestCaseIds = feedbackLines.flatMap(line => extractTestCaseIds(line));

  return (
    <div className="space-y-4 my-4">
      {/* 状态卡片 */}
      <div
        className={cn(
          "rounded-lg border-2 p-4",
          feedback.passed
            ? "border-green-200 bg-green-50"
            : "border-red-200 bg-red-50"
        )}
      >
        <div className="flex items-center gap-3">
          {feedback.passed ? (
            <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
          ) : (
            <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
          )}
          <div>
            <h3
              className={cn(
                "font-semibold text-lg",
                feedback.passed ? "text-green-900" : "text-red-900"
              )}
            >
              {feedback.passed ? "✅ 评审通过" : "❌ 评审未通过"}
            </h3>
            <p
              className={cn(
                "text-sm mt-1",
                feedback.passed ? "text-green-700" : "text-red-700"
              )}
            >
              {feedback.passed
                ? "测试用例符合要求，已准备保存"
                : "测试用例存在问题，需要改进"}
            </p>
          </div>
        </div>
      </div>

      {/* 反馈详情 */}
      {!feedback.passed && feedbackLines.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-500" />
            反馈详情
          </h4>

          <div className="space-y-2">
            {feedbackLines.map((line, index) => {
              const testCaseIds = extractTestCaseIds(line);
              return (
                <div key={index} className="flex gap-3">
                  <div className="flex-shrink-0 mt-1">
                    <div className="flex items-center justify-center h-5 w-5 rounded-full bg-orange-100">
                      <span className="text-xs font-semibold text-orange-600">
                        {index + 1}
                      </span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {line}
                    </p>
                    {testCaseIds.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {testCaseIds.map(id => (
                          <span
                            key={id}
                            className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded"
                          >
                            {id}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 涉及的用例统计 */}
      {allTestCaseIds.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h4 className="font-semibold text-gray-900 mb-3">涉及的用例</h4>
          <div className="flex flex-wrap gap-2">
            {allTestCaseIds.map(id => (
              <span
                key={id}
                className="inline-block px-3 py-1 text-sm font-medium bg-blue-100 text-blue-700 rounded-full"
              >
                {id}
              </span>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            共 {allTestCaseIds.length} 个用例需要改进
          </p>
        </div>
      )}

      {/* 建议 */}
      {!feedback.passed && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
          <h4 className="font-semibold text-blue-900 mb-2">💡 建议</h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>根据反馈逐一改进测试用例</li>
            <li>确保每个用例都有清晰的前置条件</li>
            <li>测试步骤要具体明确，可直接执行</li>
            <li>预期结果要详细完整，包括界面、数据、提示信息</li>
            <li>场景覆盖要全面（正常、边界、异常、安全）</li>
          </ul>
        </div>
      )}
    </div>
  );
}

