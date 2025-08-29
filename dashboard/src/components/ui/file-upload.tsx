import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onFilesChange: (files: File[]) => void;
  files: File[];
  accept?: Record<string, string[]>;
  multiple?: boolean;
  className?: string;
  label: string;
  description?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFilesChange,
  files,
  accept,
  multiple = false,
  className,
  label,
  description
}) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (multiple) {
      onFilesChange([...files, ...acceptedFiles]);
    } else {
      onFilesChange(acceptedFiles);
    }
  }, [files, multiple, onFilesChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple
  });

  const removeFile = (indexToRemove: number) => {
    onFilesChange(files.filter((_, index) => index !== indexToRemove));
  };

  return (
    <div className={cn("space-y-3", className)}>
      <div className="space-y-1">
        <label className="text-sm font-medium text-foreground">{label}</label>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
      
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
          isDragActive
            ? "border-secondary bg-secondary/5"
            : "border-border hover:border-secondary/50",
          "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        )}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
        {isDragActive ? (
          <p className="text-sm text-secondary">Drop the files here...</p>
        ) : (
          <div className="text-sm text-muted-foreground">
            <p>Drag & drop files here, or click to select</p>
            <p className="text-xs mt-1">Supports .txt, .asm, .c, .h, .md files</p>
          </div>
        )}
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-2 bg-muted rounded-md"
            >
              <div className="flex items-center space-x-2">
                <File className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">{file.name}</span>
                <span className="text-xs text-muted-foreground">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="p-1 hover:bg-destructive/10 hover:text-destructive rounded"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};