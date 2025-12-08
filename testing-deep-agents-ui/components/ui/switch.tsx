/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

"use client";
// NOTE  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UjFkcVN3PT06MThiOWU5YTY=

import * as React from "react";
import * as SwitchPrimitive from "@radix-ui/react-switch";
// TODO  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UjFkcVN3PT06MThiOWU5YTY=

import { cn } from "@/lib/utils";

function Switch({
  className,
  ...props
}: React.ComponentProps<typeof SwitchPrimitive.Root>) {
  return (
    <SwitchPrimitive.Root
      data-slot="switch"
      style={{
        display: "inline-flex",
        height: "20px",
        width: "36px",
        alignItems: "center",
        borderRadius: "9999px",
        border: "1px solid #d1d5db",
        backgroundColor: "var(--color-border)",
        cursor: "pointer",
        transition: "background-color 0.2s",
      }}
      data-state-styles={{
        checked: {
          backgroundColor: "var(--color-primary)",
        },
      }}
      className={cn(
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:!bg-[var(--color-primary)]",
        className
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb
        data-slot="switch-thumb"
        style={{
          display: "block",
          width: "16px",
          height: "16px",
          borderRadius: "9999px",
          backgroundColor: "white",
          boxShadow: "0 2px 4px rgba(0, 0, 0, 0.2)",
          transition: "transform 0.2s",
          transform: "translateX(1px)",
        }}
        className="data-[state=checked]:!translate-x-[17px]"
      />
    </SwitchPrimitive.Root>
  );
}

export { Switch };
// FIXME  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UjFkcVN3PT06MThiOWU5YTY=
