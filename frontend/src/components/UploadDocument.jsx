import React, { useState } from 'react';
import { UploadCloud, CheckCircle2, AlertCircle, Loader2, X } from 'lucide-react';
import { uploadDocument } from '../services/api';

const UploadDocument = ({ onUploadSuccess, onClose }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setStatusMessage(null);
      setErrorMessage(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setStatusMessage(null);
      setErrorMessage(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setStatusMessage(null);
    setErrorMessage(null);

    try {
      const result = await uploadDocument(file);
      if (result.is_duplicate) {
        setStatusMessage(`Duplicate Detected: '${result.filename}' is already processed (${result.chunk_count} chunks).`);
      } else {
        setStatusMessage(`Successfully processed '${result.filename}' into ${result.chunk_count} chunks!`);
      }
      setFile(null);
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
    } catch (err) {
      const msg = err.response?.data?.error?.message || err.message || 'Failed to upload document.';
      setErrorMessage(msg);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="upload-modal-overlay">
      <div className="upload-modal-card">
        <div className="upload-modal-header">
          <h3>Upload Knowledge Document</h3>
          {onClose && (
            <button className="btn-icon" onClick={onClose}>
              <X className="icon-sm" />
            </button>
          )}
        </div>

        <form onSubmit={handleSubmit}>
          <div
            className={`drop-zone ${file ? 'has-file' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <UploadCloud className="icon-lg text-accent" />
            {file ? (
              <div className="file-info">
                <span className="file-name">{file.name}</span>
                <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
              </div>
            ) : (
              <div className="drop-instructions">
                <p className="primary-text">Drag & drop your document here, or click to browse</p>
                <p className="secondary-text">Supported formats: PDF, DOCX, TXT (Max 25MB)</p>
              </div>
            )}
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleFileChange}
              className="file-input"
            />
          </div>

          {statusMessage && (
            <div className="alert alert-success">
              <CheckCircle2 className="icon-sm" />
              <span>{statusMessage}</span>
            </div>
          )}

          {errorMessage && (
            <div className="alert alert-error">
              <AlertCircle className="icon-sm" />
              <span>{errorMessage}</span>
            </div>
          )}

          <div className="upload-actions">
            {onClose && (
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Close
              </button>
            )}
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!file || isUploading}
            >
              {isUploading ? (
                <>
                  <Loader2 className="icon-sm spin" /> Processing...
                </>
              ) : (
                'Upload & Index'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UploadDocument;
