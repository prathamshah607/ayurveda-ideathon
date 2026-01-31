import React, { useCallback, useState } from 'react';
import { Upload, Camera, X, Eye } from 'lucide-react';
import { Button } from './Button';

interface ImageUploadProps {
  label: string;
  icon?: React.ReactNode;
  onImageSelect: (file: File) => void;
  onRemove?: () => void;
  previewUrl?: string;
  lastUploadDate?: string;
  analysisStatus?: 'pending' | 'complete' | 'none';
  onViewAnalysis?: () => void;
  accept?: string;
  maxSizeMB?: number;
}

export function ImageUpload({
  label,
  icon,
  onImageSelect,
  onRemove,
  previewUrl,
  lastUploadDate,
  analysisStatus = 'none',
  onViewAnalysis,
  accept = 'image/jpeg,image/png',
  maxSizeMB = 5,
}: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      setError(null);
      
      // Validate file type
      const validTypes = accept.split(',').map((t) => t.trim());
      if (!validTypes.some((type) => file.type.match(type.replace('*', '.*')))) {
        setError('Invalid file type. Please upload a JPG or PNG image.');
        return;
      }
      
      // Validate file size
      if (file.size > maxSizeMB * 1024 * 1024) {
        setError(`File too large. Maximum size is ${maxSizeMB}MB.`);
        return;
      }
      
      onImageSelect(file);
    },
    [accept, maxSizeMB, onImageSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      
      const file = e.dataTransfer.files[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const openCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      // In a real implementation, you would open a camera modal here
      // For now, we'll just stop the stream
      stream.getTracks().forEach((track) => track.stop());
      alert('Camera functionality would open a capture modal here');
    } catch {
      setError('Unable to access camera. Please check permissions.');
    }
  };

  return (
    <div className="w-full bg-surface rounded-xl border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2">
        {icon}
        <span className="font-medium text-text-primary">{label}</span>
      </div>

      {/* Upload Area */}
      <div className="p-4">
        {!previewUrl ? (
          <>
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              className={`
                border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200
                ${isDragging ? 'border-primary bg-primary/5' : 'border-gray-200'}
              `}
            >
              <div className="flex flex-col items-center gap-3">
                <div className="flex gap-3">
                  <label className="cursor-pointer">
                    <input
                      type="file"
                      accept={accept}
                      onChange={handleFileInput}
                      className="hidden"
                    />
                    <div className="flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition-colors">
                      <Upload size={18} />
                      <span className="font-medium">Upload Image</span>
                    </div>
                  </label>
                  <button
                    type="button"
                    onClick={openCamera}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-text-secondary rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <Camera size={18} />
                    <span className="font-medium">Camera</span>
                  </button>
                </div>
                <p className="text-sm text-text-secondary">
                  Drag & drop or click to upload
                </p>
                <p className="text-xs text-text-secondary/70">
                  Supported: JPG, PNG (max {maxSizeMB}MB)
                </p>
              </div>
            </div>
            {error && (
              <p className="mt-2 text-sm text-error">{error}</p>
            )}
          </>
        ) : (
          <div className="space-y-3">
            {/* Preview */}
            <div className="relative rounded-lg overflow-hidden bg-gray-100">
              <img
                src={previewUrl}
                alt="Uploaded preview"
                className="w-full h-48 object-cover"
              />
              {onRemove && (
                <button
                  type="button"
                  onClick={onRemove}
                  className="absolute top-2 right-2 p-1.5 bg-white/90 rounded-full hover:bg-white transition-colors"
                >
                  <X size={16} className="text-text-primary" />
                </button>
              )}
            </div>

            {/* Upload info */}
            <div className="flex items-center justify-between text-sm">
              <div className="text-text-secondary">
                {lastUploadDate && (
                  <span>Last uploaded: {lastUploadDate}</span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {analysisStatus === 'pending' && (
                  <span className="flex items-center gap-1.5 text-warning">
                    <span className="w-2 h-2 bg-warning rounded-full animate-pulse" />
                    Analyzing...
                  </span>
                )}
                {analysisStatus === 'complete' && onViewAnalysis && (
                  <Button
                    variant="ghost"
                    size="sm"
                    leftIcon={<Eye size={16} />}
                    onClick={onViewAnalysis}
                  >
                    View Analysis
                  </Button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
