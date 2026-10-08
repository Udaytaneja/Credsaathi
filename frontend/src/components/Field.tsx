import { forwardRef } from 'react';

export interface FieldProps extends React.InputHTMLAttributes<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement> {
  label: string;
  hint?: string;
  error?: string;
  required?: boolean;
  affix?: string;
  fieldType?: 'input' | 'select' | 'textarea';
  options?: { value: string; label: string }[];
}

export const Field = forwardRef<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement, FieldProps>(
  ({ label, hint, error, required, affix, fieldType = 'input', options, className = '', id, children, ...props }, ref) => {
    const inputId = id || label.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className={`field ${error ? 'has-error' : ''} ${className}`}>
        <label htmlFor={inputId}>
          <span>{label}</span>
          {required && <em>*</em>}
        </label>
        
        {affix ? (
          <div className="input-affix">
            <b>{affix}</b>
            <input
              id={inputId}
              ref={ref as React.Ref<HTMLInputElement>}
              {...(props as React.InputHTMLAttributes<HTMLInputElement>)}
            />
          </div>
        ) : fieldType === 'select' ? (
          <select
            id={inputId}
            ref={ref as React.Ref<HTMLSelectElement>}
            {...(props as React.SelectHTMLAttributes<HTMLSelectElement>)}
          >
            {options
              ? options.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))
              : children}
          </select>
        ) : fieldType === 'textarea' ? (
          <textarea
            id={inputId}
            ref={ref as React.Ref<HTMLTextAreaElement>}
            {...(props as React.TextareaHTMLAttributes<HTMLTextAreaElement>)}
          />
        ) : (
          <input
            id={inputId}
            ref={ref as React.Ref<HTMLInputElement>}
            {...(props as React.InputHTMLAttributes<HTMLInputElement>)}
          />
        )}

        {hint && !error && <small className="hint-text">{hint}</small>}
        {error && <small className="error-text" role="alert">{error}</small>}
      </div>
    );
  }
);

Field.displayName = 'Field';
export default Field;
