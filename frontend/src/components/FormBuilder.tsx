'use client';

import React, { useState } from 'react';

interface FormField {
  name: string;
  label: string;
  type: 'number' | 'text' | 'select';
  min?: number;
  max?: number;
  step?: number;
  options?: { value: string; label: string }[];
  defaultValue?: number | string;
  group?: string;
  hint?: string;
  icon?: React.ReactNode;
}

interface FormBuilderProps {
  fields: FormField[];
  onSubmit: (data: Record<string, any>) => Promise<void>;
  buttonLabel?: string;
  loading?: boolean;
}

export default function FormBuilder({
  fields,
  onSubmit,
  buttonLabel = 'Submit',
  loading = false,
}: FormBuilderProps) {
  const [formData, setFormData] = useState<Record<string, any>>(
    fields.reduce((acc, field) => ({ ...acc, [field.name]: field.defaultValue ?? '' }), {})
  );
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: e.target.type === 'number' ? parseFloat(value) || 0 : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await onSubmit(formData);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const groupedFields = fields.reduce<Record<string, FormField[]>>((acc, field) => {
    const group = field.group || 'General';
    if (!acc[group]) acc[group] = [];
    acc[group].push(field);
    return acc;
  }, {});

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {Object.entries(groupedFields).map(([groupName, groupFields]) => (
        <div key={groupName}>
          {Object.keys(groupedFields).length > 1 && (
            <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--text-muted)] mb-3">
              {groupName}
            </h3>
          )}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {groupFields.map((field) => (
              <div key={field.name} className="space-y-1">
                <label className="block text-[0.75rem] font-semibold text-[var(--text-secondary)]">
                  {field.label}
                </label>
                {field.type === 'select' ? (
                  <select
                    name={field.name}
                    value={formData[field.name]}
                    onChange={handleChange}
                    className="text-sm"
                  >
                    {field.options?.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={field.type}
                    name={field.name}
                    value={formData[field.name]}
                    onChange={handleChange}
                    min={field.min}
                    max={field.max}
                    step={field.step}
                    className="text-sm"
                  />
                )}
                {field.hint && (
                  <p className="text-[0.6875rem] text-[var(--text-muted)]">{field.hint}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      {error && (
        <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#de3831" strokeWidth="2" strokeLinecap="round" className="mt-0.5 flex-shrink-0">
            <circle cx="12" cy="12" r="10" />
            <path d="M15 9l-6 6M9 9l6 6" />
          </svg>
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading || loading}
        className="btn btn-primary btn-lg w-full"
      >
        {(isLoading || loading) ? (
          <>
            <span className="spinner" />
            Processing...
          </>
        ) : (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
            {buttonLabel}
          </>
        )}
      </button>
    </form>
  );
}
