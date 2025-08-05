import React from "react";

interface BadgeProps {
  className: string;
  children: React.ReactNode;
}

const Badge: React.FC<BadgeProps> = ({ className, children }) => {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-sm font-medium ${className}`}>
      {children}
    </span>
  );
};

export default Badge;