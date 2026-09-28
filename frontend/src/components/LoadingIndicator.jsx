import React from 'react';
import { Bot, Sparkles } from 'lucide-react';

const LoadingIndicator = ({ text = "Retrieving context & generating answer..." }) => {
  return (
    <div className="message-wrapper assistant loading">
      <div className="avatar assistant-avatar">
        <Bot className="icon-sm" />
      </div>
      <div className="message-bubble assistant-bubble loading-bubble">
        <div className="loading-content">
          <Sparkles className="icon-sm spin-slow text-accent" />
          <span>{text}</span>
          <div className="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;
