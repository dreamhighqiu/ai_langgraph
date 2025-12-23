

import { cn } from "@/lib/utils";
// eslint-disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0V4bmVnPT06MjY5NGU5YzA=

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
// @ts-expect-error  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T0V4bmVnPT06MjY5NGU5YzA=

export { Skeleton };
