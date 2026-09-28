import React from 'react';
import { User, Bot, BookOpen } from 'lucide-react';
import SourceCard from './SourceCard';

const Message = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar ${isUser ? 'user-avatar' : 'assistant-avatar'}`}>
        {isUser ? <User className="icon-sm" /> : <Bot className="icon-sm" />}
      </div>
      
      <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
        <div className="message-content">
          <p>{message.content}</p>
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="sources-container">
            <div className="sources-header">
              <BookOpen className="icon-xs text-accent" />
              <span>Retrieved Sources ({message.sources.length})</span>
            </div>
            <div className="sources-grid">
              {message.sources.map((src, idx) => (
                <SourceCard key={idx} source={src} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;
