import React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'navy';
  className?: string;
  style?: React.CSSProperties;
  icon?: React.ReactNode;
}

export default function Badge({ children, tone = 'neutral', className = '', style, icon }: BadgeProps) {
  return (
    <span className={`badge badge-${tone} ${className}`} style={style}>
      {icon && <span className="badge-icon mr-1">{icon}</span>}
      {children}
    </span>
  );
}
