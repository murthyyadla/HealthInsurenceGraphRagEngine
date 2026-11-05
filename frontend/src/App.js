import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your myHealthInsure copilot. Ask me about plan benefits, deductibles, or medical procedures like an MRI scan.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Direct REST network fetch call to the containerized FastAPI router endpoint
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_query: userMessage }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.final_response,
          telemetry: {
            path: data.routing_path_taken,
            entities: data.extracted_entities,
            cypher: data.executed_cypher
          }
        }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: '🚨 Error communicating with the underlying microservice gateway.' }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: '🚨 Network connection timeout reaching the backend engine.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>💙 myHealthInsure Portal</h1>
        <p>Enterprise Hybrid GraphRAG Intelligent Gateway</p>
      </header>

      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message-row ${msg.role}`}>
            <div className={`message-bubble ${msg.role}`}>
              <div className="message-text">{msg.content}</div>
              
              {msg.telemetry && (msg.telemetry.entities.length > 0 || msg.telemetry.cypher) && (
                <div className="telemetry-panel">
                  <div className="telemetry-badge">📍 {msg.telemetry.path}</div>
                  {msg.telemetry.entities.length > 0 && (
                    <div className="telemetry-item"><strong>Extracted Nodes:</strong> <code>{msg.telemetry.entities.join(', ')}</code></div>
                  )}
                  {msg.telemetry.cypher && (
                    <div className="telemetry-item"><strong>Executed Cypher:</strong> <pre>{msg.telemetry.cypher}</pre></div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message-row assistant">
            <div className="message-bubble assistant loading">
              <span className="dot"></span><span className="dot"></span><span className="dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="input-area">
        <input 
          type="text" 
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about copays, diagnostic scans, specialist rules..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>Transmit</button>
      </form>
    </div>
  );
}

export default App;
