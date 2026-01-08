
// NOTE  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YUhCdVFRPT06OGM3YTU1MGQ=

import { cn } from "@/lib/utils";

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  );
}
// FIXME  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YUhCdVFRPT06OGM3YTU1MGQ=

export { Skeleton };
