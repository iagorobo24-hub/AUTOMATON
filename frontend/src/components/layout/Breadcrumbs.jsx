import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

const Breadcrumbs = ({ items, className }) => {
  if (!items || items.length <= 1) return null;

  return (
    <nav className={cn("flex items-center space-x-1 text-sm text-muted-foreground", className)}>
      {items.map((item, index) => (
        <div key={index} className="flex items-center">
          {index > 0 && (
            <ChevronRight className="w-4 h-4 mx-2 text-muted-foreground/50" />
          )}
          {item.href ? (
            <a
              href={item.href}
              className="hover:text-foreground transition-colors"
              onClick={(e) => {
                if (item.onClick) {
                  e.preventDefault();
                  item.onClick();
                }
              }}
            >
              {item.label}
            </a>
          ) : (
            <span className="text-foreground font-medium">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
};

export default Breadcrumbs;
