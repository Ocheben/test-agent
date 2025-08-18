'use client';

import { useState } from 'react';
import { sendChatMessage } from '../lib/chat';

export default function Home() {
  const [messages, setMessages] = useState<{ role: 'user' | 'agent'; content: string }[]>([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', content: input };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    try {
      const answer = await sendChatMessage(userMsg.content);
      setMessages((m) => [...m, { role: 'agent', content: answer }]);
    } catch (err) {
      setMessages((m) => [...m, { role: 'agent', content: 'Error contacting agent' }]);
    }
  };

  return (
    <main>
      <div className="chat">
        {messages.map((m, i) => (
          <p key={i}>
            <strong>{m.role}:</strong> {m.content}
          </p>
        ))}
      </div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message"
      />
      <button onClick={handleSend}>Send</button>
    </main>
  );
}
