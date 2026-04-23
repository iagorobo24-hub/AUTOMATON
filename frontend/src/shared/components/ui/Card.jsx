import { cn } from "@/lib/utils";

export function Card({ className, ...props }) {
  return (
    <div 
      className={cn("bg-[#1a211d] border border-[#3c4a42] rounded-none", className)} 
      {...props} 
    />
  );
}
