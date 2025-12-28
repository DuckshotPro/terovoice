import React from 'react';

function Message({ message }) {
  const isAI = message.sender === 'ai';

  return (
    <div className={`flex ${isAI ? 'justify-start' : 'justify-end'}`}>
      <div
        className={`max-w-xs px-4 py-2 rounded-lg ${
          isAI
            ? 'bg-gray-200 text-gray-900'
            : 'bg-blue-500 text-white'
        }`}
      >
        <p className="text-sm">{message.text}</p>
        <span className="text-xs opacity-70 mt-1 block">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
}

export default Message;
