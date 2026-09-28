import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Sparkles, BookOpenCheck } from 'lucide-react';
import Message from './Message';
import LoadingIndicator from './LoadingIndicator';

const ChatWindow = ({
  messages,
  isLoading,
  onSendMessage,
  activeConversation,
  documentsCount
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="chat-header-info">
          <Bot className="icon-md text-accent" />
          <div>
            <h3>{activeConversation ? activeConversation.title : 'AI Document Assistant'}</h3>
            <p className="subtitle">
              Ask questions about your {documentsCount} uploaded document{documentsCount === 1 ? '' : 's'}
            </p>
          </div>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <div className="welcome-card">
              <Sparkles className="icon-lg text-accent animate-bounce" />
              <h2>Document RAG Intelligence</h2>
              <p>
                Upload your PDF, DOCX, or TXT documents to get started. Ask questions and get answers grounded strictly in your files with full page & chunk citations.
              </p>
              <div className="example-prompts">
                <h4>Try asking:</h4>
                <div
                  className="prompt-chip"
                  onClick={() => onSendMessage("What is the annual leave policy?")}
                >
                  "What is the annual leave policy?"
                </div>
                <div
                  className="prompt-chip"
                  onClick={() => onSendMessage("What are the standard working hours?")}
                >
                  "What are the standard working hours?"
                </div>
                <div
                  className="prompt-chip"
                  onClick={() => onSendMessage("Can employees work remotely?")}
                >
                  "Can employees work remotely?"
                </div>
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => <Message key={msg.id || idx} message={msg} />)
        )}

        {isLoading && <LoadingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <form onSubmit={handleSubmit} className="chat-input-form">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about your documents... (Shift+Enter for newline, Enter to send)"
            rows={1}
            className="chat-textarea"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn-send"
            title="Send Message"
          >
            <Send className="icon-sm" />
          </button>
        </form>
        <p className="input-footer">
          RAG Pipeline powered by Sentence Transformers, ChromaDB, and local Ollama.
        </p>
      </div>
    </div>
  );
};

export default ChatWindow;
