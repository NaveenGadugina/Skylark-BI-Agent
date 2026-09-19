import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const suggestions = [
    "How is our sales pipeline looking?",
    "What are our current open deals?",
    "How much has been billed and collected?",
    "Which sectors have the most open deals?",
  ];

  const askQuestion = async (text = question) => {
    if (!text.trim()) return;

    setLoading(true);
    setAnswer("");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: text,
        }),
      });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      throw new Error(
        errorData.detail || "Backend request failed"
      );
    }

      const data = await response.json();
      setAnswer(data.answer);
    } catch (error) {
      setAnswer(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestion = (text) => {
    setQuestion(text);
    askQuestion(text);
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">S</div>

          <div>
            <h1>Skylark BI Agent</h1>
            <span>Monday.com Business Intelligence</span>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Live
        </div>
      </header>

      <main className="main-content">
        <section className="hero">
          <p className="eyebrow">EXECUTIVE BUSINESS INTELLIGENCE</p>

          <h2>Ask your business anything.</h2>

          <p className="hero-text">
            Get quick insights from your sales pipeline and work order data
            using natural language.
          </p>
        </section>

        <section className="suggestions">
          <p className="section-label">Try asking</p>

          <div className="suggestion-grid">
            {suggestions.map((item, index) => (
              <button
                key={index}
                className="suggestion-card"
                onClick={() => handleSuggestion(item)}
              >
                <span>{item}</span>
                <span className="arrow">→</span>
              </button>
            ))}
          </div>
        </section>

        <section className="chat-section">
          <div className="input-wrapper">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  askQuestion();
                }
              }}
              placeholder="Ask a business question..."
              rows="3"
            />

            <button
              className="ask-button"
              onClick={() => askQuestion()}
              disabled={loading || !question.trim()}
            >
              {loading ? "Analyzing..." : "Ask"}
              {!loading && <span>→</span>}
            </button>
          </div>

          <p className="input-hint">
            Press Enter to ask · Shift + Enter for a new line
          </p>
        </section>

        {loading && (
          <section className="answer-card loading-card">
            <div className="answer-header">
              <span className="answer-icon">AI</span>
              <span>Analysis</span>
            </div>

            <div className="loading-content">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </section>
        )}

        {!loading && answer && (
          <section className="answer-card">
            <div className="answer-header">
              <span className="answer-icon">AI</span>
              <span>Analysis</span>
            </div>

            <div className="answer-content">
              {answer.split("\n").map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          </section>
        )}
      </main>

      <footer>
        <span>Skylark Drones</span>
        <span>•</span>
        <span>Powered by Monday.com + AI</span>
      </footer>
    </div>
  );
}

export default App;