import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import UploadDocument from '../components/UploadDocument';
import {
  getConversations,
  getConversationDetails,
  createConversation,
  deleteConversation,
  getDocuments,
  deleteDocument,
  sendMessage,
  healthCheck
} from '../services/api';

const ChatPage = () => {
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [errorBanner, setErrorBanner] = useState(null);

  // Initial load
  useEffect(() => {
    loadHealth();
    loadDocuments();
    loadConversations();
  }, []);

  const loadHealth = async () => {
    try {
      const data = await healthCheck();
      setHealthStatus(data);
    } catch (err) {
      setHealthStatus({ status: 'degraded', services: { ollama: 'unavailable' } });
    }
  };

  const loadDocuments = async () => {
    try {
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const loadConversations = async () => {
    try {
      const data = await getConversations();
      setConversations(data);
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const handleSelectConversation = async (convId) => {
    setCurrentConvId(convId);
    setErrorBanner(null);
    try {
      const details = await getConversationDetails(convId);
      setMessages(details.messages || []);
    } catch (err) {
      console.error('Failed to load conversation details:', err);
    }
  };

  const handleNewChat = () => {
    setCurrentConvId(null);
    setMessages([]);
    setErrorBanner(null);
  };

  const handleDeleteConversation = async (convId) => {
    try {
      await deleteConversation(convId);
      if (currentConvId === convId) {
        handleNewChat();
      }
      loadConversations();
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleDeleteDocument = async (docId) => {
    try {
      await deleteDocument(docId);
      loadDocuments();
    } catch (err) {
      console.error('Failed to delete document:', err);
    }
  };

  const handleSendMessage = async (text) => {
    setIsLoading(true);
    setErrorBanner(null);

    // Optimistic user message render
    const tempUserMsg = {
      role: 'user',
      content: text,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await sendMessage(text, currentConvId);
      
      // Update conversation ID if newly created
      if (!currentConvId && response.conversation_id) {
        setCurrentConvId(response.conversation_id);
      }

      // Add assistant response
      const assistantMsg = {
        role: 'assistant',
        content: response.message,
        sources: response.sources,
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Refresh sidebar conversation list
      loadConversations();
    } catch (err) {
      const errDetail = err.response?.data?.error;
      const errorMsg = errDetail?.message || err.message || 'Failed to generate response.';
      setErrorBanner(errorMsg);

      // Render assistant error message
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ Error: ${errorMsg}`,
          sources: [],
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const activeConv = conversations.find((c) => c.id === currentConvId);

  return (
    <div className="chat-page-layout">
      <Sidebar
        conversations={conversations}
        currentConvId={currentConvId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        documents={documents}
        onDeleteDocument={handleDeleteDocument}
        onOpenUpload={() => setShowUploadModal(true)}
        healthStatus={healthStatus}
      />

      <main className="main-chat-container">
        {errorBanner && (
          <div className="global-error-banner">
            <span>{errorBanner}</span>
            <button onClick={() => setErrorBanner(null)}>×</button>
          </div>
        )}

        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          activeConversation={activeConv}
          documentsCount={documents.length}
        />
      </main>

      {showUploadModal && (
        <UploadDocument
          onUploadSuccess={() => {
            loadDocuments();
          }}
          onClose={() => setShowUploadModal(false)}
        />
      )}
    </div>
  );
};

export default ChatPage;
