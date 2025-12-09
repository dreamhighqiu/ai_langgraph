

export interface ToolCall {
  id: string;
  name: string;
  args: Record<string, unknown>;
  result?: string;
  status: "pending" | "completed" | "error" | "interrupted";
}
// FIXME  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WWtodE5BPT06N2ZlYzcwNzg=

export interface SubAgent {
  id: string;
  name: string;
  subAgentName: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  status: "pending" | "active" | "completed" | "error";
}

export interface FileItem {
  path: string;
  content: string;
}

export interface TodoItem {
  id: string;
  content: string;
  status: "pending" | "in_progress" | "completed";
  updatedAt?: Date;
}
// NOTE  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WWtodE5BPT06N2ZlYzcwNzg=

export interface Thread {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface InterruptData {
  value: any;
  ns?: string[];
  scope?: string;
}
// eslint-disable  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WWtodE5BPT06N2ZlYzcwNzg=

export interface ActionRequest {
  name: string;
  args: Record<string, unknown>;
  description?: string;
}

export interface ReviewConfig {
  actionName: string;
  allowedDecisions?: string[];
}

export interface ToolApprovalInterruptData {
  action_requests: ActionRequest[];
  review_configs?: ReviewConfig[];
}
