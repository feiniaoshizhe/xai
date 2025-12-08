"use client";

import { CopilotKit } from "@copilotkit/react-core";

export function CopilotProvider({ children }: { children: React.ReactNode }) {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="flight_chart_agent">
      {children}
    </CopilotKit>
  );
}

// 可选：清除本地保存的 thread（当前未持久化 threadId，但保留接口以备后用）
export function clearChatHistory() {
  localStorage.removeItem("chat_thread_id");
  window.location.reload();
}
