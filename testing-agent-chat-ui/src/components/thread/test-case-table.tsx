/**
 * 测试用例表格组件
 * 用于展示 JSON 格式的测试用例数据
 */

"use client";

import React, { useState, useMemo } from "react";
import { ChevronDown, ChevronUp, Download } from "lucide-react";
import { cn } from "@/lib/utils";

interface TestCase {
  case_id: string;
  case_name: string;
  priority: string;
  precondition: string;
  test_steps: string;
  expected_result: string;
  category: string;
}

interface TestCaseTableProps {
  content: string;
}

/**
 * 尝试从内容中解析 JSON 格式的测试用例
 */
function parseTestCases(content: string): TestCase[] {
  try {
    // 尝试直接解析 JSON
    const data = JSON.parse(content);
    
    if (Array.isArray(data)) {
      return data;
    }
    
    if (data && typeof data === 'object' && 'test_cases' in data) {
      return Array.isArray(data.test_cases) ? data.test_cases : [];
    }
    
    return [];
  } catch {
    // 如果直接解析失败，尝试从文本中提取 JSON
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        const data = JSON.parse(jsonMatch[0]);
        if (data && typeof data === 'object' && 'test_cases' in data) {
          return Array.isArray(data.test_cases) ? data.test_cases : [];
        }
        if (Array.isArray(data)) {
          return data;
        }
      } catch {
        // 继续
      }
    }
    return [];
  }
}

/**
 * 展开行组件
 */
function ExpandableRow({ testCase }: { testCase: TestCase }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <>
      <tr className="border-b hover:bg-muted/50 transition-colors">
        <td className="px-4 py-3 text-sm font-medium">{testCase.case_id}</td>
        <td className="px-4 py-3 text-sm">{testCase.case_name}</td>
        <td className="px-4 py-3 text-sm">
          <span
            className={cn(
              "px-2 py-1 rounded text-xs font-semibold",
              testCase.priority === "P0"
                ? "bg-red-100 text-red-800"
                : testCase.priority === "P1"
                  ? "bg-orange-100 text-orange-800"
                  : "bg-yellow-100 text-yellow-800"
            )}
          >
            {testCase.priority}
          </span>
        </td>
        <td className="px-4 py-3 text-sm">
          <span
            className={cn(
              "px-2 py-1 rounded text-xs font-semibold",
              testCase.category === "正常场景"
                ? "bg-green-100 text-green-800"
                : testCase.category === "边界场景"
                  ? "bg-blue-100 text-blue-800"
                  : testCase.category === "异常场景"
                    ? "bg-red-100 text-red-800"
                    : "bg-purple-100 text-purple-800"
            )}
          >
            {testCase.category}
          </span>
        </td>
        <td className="px-4 py-3 text-center">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="inline-flex items-center justify-center w-8 h-8 rounded hover:bg-muted transition-colors"
          >
            {isExpanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
        </td>
      </tr>

      {isExpanded && (
        <tr className="bg-muted/30 border-b">
          <td colSpan={5} className="px-4 py-4">
            <div className="space-y-3">
              <div>
                <h4 className="font-semibold text-sm mb-1">前置条件</h4>
                <p className="text-sm whitespace-pre-wrap text-muted-foreground">
                  {testCase.precondition}
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-sm mb-1">测试步骤</h4>
                <p className="text-sm whitespace-pre-wrap text-muted-foreground">
                  {testCase.test_steps}
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-sm mb-1">预期结果</h4>
                <p className="text-sm whitespace-pre-wrap text-muted-foreground">
                  {testCase.expected_result}
                </p>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

/**
 * 测试用例表格组件
 */
export function TestCaseTable({ content }: TestCaseTableProps) {
  const testCases = useMemo(() => parseTestCases(content), [content]);

  if (testCases.length === 0) {
    return null;
  }

  // 统计信息
  const stats = {
    total: testCases.length,
    p0: testCases.filter((tc) => tc.priority === "P0").length,
    p1: testCases.filter((tc) => tc.priority === "P1").length,
    p2: testCases.filter((tc) => tc.priority === "P2").length,
  };

  return (
    <div className="w-full space-y-4">
      {/* 统计信息 */}
      <div className="grid grid-cols-4 gap-2">
        <div className="bg-muted rounded-lg p-3">
          <div className="text-2xl font-bold">{stats.total}</div>
          <div className="text-xs text-muted-foreground">总用例数</div>
        </div>
        <div className="bg-red-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-red-600">{stats.p0}</div>
          <div className="text-xs text-red-600">P0 用例</div>
        </div>
        <div className="bg-orange-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-orange-600">{stats.p1}</div>
          <div className="text-xs text-orange-600">P1 用例</div>
        </div>
        <div className="bg-yellow-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-yellow-600">{stats.p2}</div>
          <div className="text-xs text-yellow-600">P2 用例</div>
        </div>
      </div>

      {/* 表格 */}
      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full">
          <thead>
            <tr className="bg-muted border-b">
              <th className="px-4 py-3 text-left text-sm font-semibold">用例ID</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">用例名称</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">优先级</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">分类</th>
              <th className="px-4 py-3 text-center text-sm font-semibold">详情</th>
            </tr>
          </thead>
          <tbody>
            {testCases.map((testCase) => (
              <ExpandableRow key={testCase.case_id} testCase={testCase} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

