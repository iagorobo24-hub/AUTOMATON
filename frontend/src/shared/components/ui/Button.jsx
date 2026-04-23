import { cn } from "@/lib/utils";

export function Button({ className, variant = "default", ...props }) {
  const variants = {
    emerald: "bg-[#10b981] text-[#0e1511] hover:opacity-90",
    outline: "border border-[#3c4a42] text-[#10b981] hover:bg-[#3c4a42]/20",
    default: "bg-[#3c4a42] text-white hover:bg-[#3c4a42]/80"
  };
  
  return (
    <button 
      className={cn("px-4 py-2 text-sm font-medium transition-all active:scale-95", variants[variant], className)} 
      {...props} 
    />
  );
}
