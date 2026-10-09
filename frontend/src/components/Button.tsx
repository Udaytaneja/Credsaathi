import { forwardRef } from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'trust' | 'ghost' | 'danger';
  size?: 'md' | 'lg';
  full?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = '', variant = 'primary', size = 'md', full = false, loading = false, disabled, icon, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={`btn btn-${variant} ${size === 'lg' ? 'btn-lg' : ''} ${full ? 'full' : ''} ${className}`}
        {...props}
      >
        {loading ? (
          <Loader2 className="animate-spin" size={16} />
        ) : icon ? (
          <span className="btn-icon">{icon}</span>
        ) : null}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
export default Button;
