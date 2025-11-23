import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { createBatch, Template } from '../../services/api';

interface UploadFormProps {
  templates: Template[];
  onUploadComplete: (batchId: number) => void;
}

const UploadForm: React.FC<UploadFormProps> = ({ templates, onUploadComplete }) => {
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [batchName, setBatchName] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
    },
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedTemplate || !batchName || files.length === 0) {
      setError('Please fill in all fields and upload at least one file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const batch = await createBatch(batchName, selectedTemplate, files);
      onUploadComplete(batch.id);
      
      // Reset form
      setBatchName('');
      setFiles([]);
      setSelectedTemplate(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">Upload Radiology Reports</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Batch Name */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Batch Name
          </label>
          <input
            type="text"
            value={batchName}
            onChange={(e) => setBatchName(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Morning Reports - Jan 2024"
          />
        </div>

        {/* Template Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Select Template
          </label>
          <select
            value={selectedTemplate || ''}
            onChange={(e) => setSelectedTemplate(Number(e.target.value))}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Choose a template...</option>
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name} - {template.description}
              </option>
            ))}
          </select>
        </div>

        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Upload Files
          </label>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-blue-400'
            }`}
          >
            <input {...getInputProps()} />
            <div className="text-gray-600">
              {isDragActive ? (
                <p>Drop the JSON file here...</p>
              ) : (
                <>
                  <p className="mb-2">Drag & drop JSON file here, or click to select</p>
                  <p className="text-sm text-gray-500">
                    Format: JSON array of report texts
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Example: ["report 1 text...", "report 2 text...", ...]
                  </p>
                </>
              )}
            </div>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="mt-4 space-y-2">
              <p className="text-sm font-medium">{files.length} file(s) selected:</p>
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between bg-gray-50 px-4 py-2 rounded"
                >
                  <span className="text-sm">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={uploading}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? 'Uploading and Processing...' : 'Upload and Process Reports'}
        </button>
      </form>
    </div>
  );
};

export default UploadForm;
