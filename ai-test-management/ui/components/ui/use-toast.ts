import { toast as sonnerToast } from "sonner";

export type ToastVariant = "default" | "destructive";

export interface ToastInput {
  title?: string;
  description?: string;
  variant?: ToastVariant;
}

function showToast({ title, description, variant }: ToastInput) {
  const resolvedTitle = title?.trim() || "";
  const resolvedDescription = description?.trim();

  const show = variant === "destructive" ? sonnerToast.error : sonnerToast;

  if (resolvedTitle) {
    show(resolvedTitle, resolvedDescription ? { description: resolvedDescription } : undefined);
    return;
  }

  if (resolvedDescription) {
    show(resolvedDescription);
  }
}

export function useToast() {
  return { toast: showToast };
}

