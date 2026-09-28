import React, { useState } from 'react';
import { FileText, Layers, Hash, Info, ExternalLink } from 'lucide-react';

const SourceCard = ({ source }) => {
  const [showDetails, setShowDetails] = useState(false);

  const similarityPercent = Math.round((source.similarity || 0) * 100);

  return (
    <div className="source-card">
      <div className="source-card-header" onClick={() => setShowDetails(!showDetails)}>
        <div className="source-file-badge">
          <FileText className="icon-sm text-accent" />
          <span className="source-filename" title={source.filename}>
            {source.filename}
          </span>
        </div>
        <div className="source-meta-pills">
          {source.page && (
            <span className="pill pill-page">
              <Layers className="icon-xs" /> Page {source.page}
            </span>
          )}
          <span className="pill pill-chunk">
            <Hash className="icon-xs" /> Chunk {source.chunk_index}
          </span>
          <span className={`pill pill-sim ${similarityPercent > 70 ? 'high' : 'med'}`}>
            {similarityPercent}% match
          </span>
        </div>
      </div>

      <div className="source-preview">
        <p>"{source.preview}"</p>
      </div>

      {showDetails && (
        <div className="source-modal-details">
          <div className="modal-row">
            <span className="label">Document ID:</span>
            <span className="val">{source.document_id}</span>
          </div>
          <div className="modal-row">
            <span className="label">Filename:</span>
            <span className="val">{source.filename}</span>
          </div>
          <div className="modal-row">
            <span className="label">Page Number:</span>
            <span className="val">{source.page || 'N/A (TXT/DOCX)'}</span>
          </div>
          <div className="modal-row">
            <span className="label">Chunk Index:</span>
            <span className="val">{source.chunk_index}</span>
          </div>
          <div className="modal-row">
            <span className="label">Cosine Similarity:</span>
            <span className="val">{source.similarity}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default SourceCard;
