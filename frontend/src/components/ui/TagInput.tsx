import React, { useState } from 'react';
import { X } from 'lucide-react';

interface TagInputProps {
  label?: string;
  placeholder?: string;
  value: string[];
  onChange: (tags: string[]) => void;
  suggestions?: string[];
  maxTags?: number;
  error?: string;
}

export function TagInput({
  label,
  placeholder = 'Type and press Enter',
  value,
  onChange,
  suggestions = [],
  maxTags,
  error,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);

  const filteredSuggestions = suggestions.filter(
    (s) =>
      s.toLowerCase().includes(inputValue.toLowerCase()) &&
      !value.includes(s)
  );

  const addTag = (tag: string) => {
    const trimmedTag = tag.trim();
    if (trimmedTag && !value.includes(trimmedTag)) {
      if (!maxTags || value.length < maxTags) {
        onChange([...value, trimmedTag]);
      }
    }
    setInputValue('');
    setShowSuggestions(false);
  };

  const removeTag = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue) {
      e.preventDefault();
      addTag(inputValue);
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      removeTag(value[value.length - 1]);
    }
  };

  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-text-primary mb-1.5">
          {label}
        </label>
      )}
      <div
        className={`
          w-full min-h-[46px] px-3 py-2 rounded-lg border bg-surface
          focus-within:ring-2 focus-within:ring-primary/50 focus-within:border-primary
          transition-all duration-200
          ${error ? 'border-error' : 'border-gray-200'}
        `}
      >
        <div className="flex flex-wrap gap-2">
          {value.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 px-2.5 py-1 bg-primary/10 text-primary rounded-full text-sm"
            >
              {tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="hover:bg-primary/20 rounded-full p-0.5"
              >
                <X size={14} />
              </button>
            </span>
          ))}
          <input
            type="text"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              setShowSuggestions(true);
            }}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder={value.length === 0 ? placeholder : ''}
            className="flex-1 min-w-[120px] outline-none bg-transparent text-text-primary placeholder:text-text-secondary/60"
          />
        </div>
      </div>
      
      {/* Suggestions dropdown */}
      {showSuggestions && filteredSuggestions.length > 0 && (
        <div className="relative">
          <div className="absolute z-10 w-full mt-1 bg-surface border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
            {filteredSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => addTag(suggestion)}
                className="w-full px-4 py-2 text-left hover:bg-primary/5 text-text-primary"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {error && <p className="mt-1.5 text-sm text-error">{error}</p>}
    </div>
  );
}

interface QuickSelectChipsProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  label?: string;
}

export function QuickSelectChips({
  options,
  selected,
  onChange,
  label,
}: QuickSelectChipsProps) {
  const toggleOption = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter((s) => s !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-text-primary mb-2">
          {label}
        </label>
      )}
      <div className="flex flex-wrap gap-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => toggleOption(option)}
            className={`
              px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
              ${
                selected.includes(option)
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-text-secondary hover:bg-gray-200'
              }
            `}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
