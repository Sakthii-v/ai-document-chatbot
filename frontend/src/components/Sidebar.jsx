import React, { useState } from 'react';
import {
  Plus,
  Upload,
  FileText,
  MessageSquare,
  Trash2,
  Database,
  Activity,
  ChevronRight
} from 'lucide-react';

const Sidebar = ({
  conversations,
  currentConvId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  documents,
  onDeleteDocument,
  onOpenUpload,
  healthStatus
}) => {
  const [activeTab, setActiveTab] = useState('chats');

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand">
          <Database className="brand-icon text-accent" />
          <h2>RAG Chatbot</h2>
        </div>
        <button className="btn btn-new-chat" onClick={onNewChat}>
          <Plus className="icon-sm" />
          <span>New Chat</span>
        </button>
      </div>

      <div className="sidebar-actions">
        <button className="btn btn-upload" onClick={onOpenUpload}>
          <Upload className="icon-sm" />
          <span>Upload Document</span>
        </button>
      </div>

      <div className="sidebar-tabs">
        <button
          className={`tab-btn ${activeTab === 'chats' ? 'active' : ''}`}
          onClick={() => setActiveTab('chats')}
        >
          <MessageSquare className="icon-xs" /> History ({conversations.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'docs' ? 'active' : ''}`}
          onClick={() => setActiveTab('docs')}
        >
          <FileText className="icon-xs" /> Docs ({documents.length})
        </button>
      </div>

      <div className="sidebar-content">
        {activeTab === 'chats' ? (
          <div className="conversation-list">
            {conversations.length === 0 ? (
              <div className="empty-state">No conversations yet</div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`conversation-item ${conv.id === currentConvId ? 'active' : ''}`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <MessageSquare className="icon-xs conv-icon" />
                  <span className="conv-title" title={conv.title}>
                    {conv.title}
                  </span>
                  <button
                    className="btn-icon delete-btn"
                    title="Delete Conversation"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteConversation(conv.id);
                    }}
                  >
                    <Trash2 className="icon-xs" />
                  </button>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="document-list">
            {documents.length === 0 ? (
              <div className="empty-state">No documents indexed yet</div>
            ) : (
              documents.map((doc) => (
                <div key={doc.id} className="document-item">
                  <FileText className="icon-xs doc-icon" />
                  <div className="doc-info">
                    <span className="doc-name" title={doc.filename}>
                      {doc.filename}
                    </span>
                    <span className="doc-meta">
                      {doc.chunk_count} chunks • {doc.file_type.toUpperCase()}
                    </span>
                  </div>
                  <button
                    className="btn-icon delete-btn"
                    title="Delete Document"
                    onClick={() => onDeleteDocument(doc.id)}
                  >
                    <Trash2 className="icon-xs" />
                  </button>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <div className="health-badge">
          <Activity className="icon-xs text-accent" />
          <span>Status:</span>
          <span className={`status-indicator ${healthStatus?.status === 'healthy' ? 'healthy' : 'degraded'}`}>
            {healthStatus?.services?.ollama === 'ok' ? 'Ollama Online' : 'Ollama Offline'}
          </span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
