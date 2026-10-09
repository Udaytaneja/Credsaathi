import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  Send, 
  ShieldCheck, 
  RefreshCw, 
  Sparkles, 
  User, 
  AlertCircle, 
  BookOpen, 
  HelpCircle 
} from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import Badge from '../components/Badge';
import { services } from '../services';
import type { ChatMessage, AssistantResponse } from '../types';

export default function Assistant() {
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-msg',
      sender: 'assistant',
      text: 'Namaste! I am Saakshi (साक्षी), your explainable AI assistant. I can explain scheme eligibility criteria, application status transitions, required documents, and credit readiness. How may I help you today?',
      timestamp: 'Just now',
      sources: ['CredSaathi Scheme & Application Knowledge Base'],
      confidence: 'High',
      humanReviewRequired: false
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll chat to bottom
  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputMessage).trim();
    if (!query || loading) return;

    setErrorMsg('');
    const userMsgId = `user-${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputMessage('');
    setLoading(true);

    try {
      const res = (await services.assistant(query)) as AssistantResponse;
      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: res.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: res.sources,
        confidence: res.confidence,
        humanReviewRequired: res.humanReviewRequired
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      setErrorMsg('Failed to fetch response from Saakshi AI service. Please click retry.');
      const errorChatMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: 'I encountered a communication issue connecting to the AI assistant endpoint (/ai/assistant/query). Please retry your question.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        error: true
      };
      setMessages((prev) => [...prev, errorChatMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleRetryLast = () => {
    const lastUserMsg = [...messages].reverse().find((m) => m.sender === 'user');
    if (lastUserMsg) {
      handleSendMessage(lastUserMsg.text);
    }
  };

  return (
    <>
      <PageTitle
        eyebrow="SAAKSHI · AI ASSISTANT / साक्षी एआई सहायक"
        title="Saakshi AI Assistant / साक्षी"
        subtitle="Explainable AI guidance scoped to official scheme criteria and your account. Answers do not constitute guaranteed sanctions or credit approvals."
        action={
          <Badge tone="navy" icon={<Sparkles size={13} />}>
            Explainable AI · Account Scoped
          </Badge>
        }
      />

      {/* Safety & Non-Authoritative Guardrail Banner */}
      <div className="card" style={{ background: '#EFF6FF', borderColor: '#BFDBFE', padding: '14px 18px', marginBottom: '22px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', color: '#1E40AF', fontSize: '12px', lineHeight: '19px' }}>
          <ShieldCheck size={20} style={{ color: '#2563EB', flexShrink: 0, marginTop: '1px' }} />
          <div>
            <strong style={{ display: 'block', fontSize: '13px', color: '#1E3A8A', marginBottom: '2px' }}>
              Statutory AI Safety Notice
            </strong>
            Saakshi provides explainable guidance based on authorized scheme metadata and account context. Saakshi responses are strictly non-authoritative and do NOT constitute guaranteed loan sanction, approval decisions, or financial advice.
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 0.9fr', gap: '22px' }}>
        {/* Main Chat Container */}
        <div>
          <Card style={{ display: 'flex', flexDirection: 'column', height: '620px', padding: 0, overflow: 'hidden' }}>
            {/* Assistant Header */}
            <div style={{
              padding: '16px 20px',
              borderBottom: '1px solid var(--line)',
              background: 'var(--white)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  background: 'var(--navy)',
                  color: 'var(--white)',
                  display: 'grid',
                  placeItems: 'center'
                }}>
                  <Bot size={20} />
                </div>
                <div>
                  <strong style={{ fontSize: '15px', color: 'var(--navy)', display: 'block' }}>Saakshi / साक्षी</strong>
                  <span style={{ fontSize: '11px', color: 'var(--muted)' }}>
                    Explainable AI Assistant · Scoped Context
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: 'var(--green)',
                  display: 'inline-block'
                }} />
                <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--green)' }}>Active</span>
              </div>
            </div>

            {/* Conversation Area */}
            <div style={{
              flex: 1,
              padding: '20px',
              overflowY: 'auto',
              background: '#F8FAFC',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px'
            }}>
              {messages.map((msg) => {
                const isUser = msg.sender === 'user';
                return (
                  <div
                    key={msg.id}
                    style={{
                      display: 'flex',
                      gap: '12px',
                      justifyContent: isUser ? 'flex-end' : 'flex-start',
                      alignItems: 'flex-start'
                    }}
                  >
                    {!isUser && (
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '8px',
                        background: 'var(--navy)',
                        color: 'var(--white)',
                        display: 'grid',
                        placeItems: 'center',
                        flexShrink: 0,
                        marginTop: '2px'
                      }}>
                        <Bot size={16} />
                      </div>
                    )}

                    <div style={{
                      maxWidth: '80%',
                      background: isUser ? 'var(--navy)' : msg.error ? '#FEF2F2' : 'var(--white)',
                      color: isUser ? 'var(--white)' : 'var(--navy)',
                      border: isUser ? 'none' : msg.error ? '1px solid #FECDD3' : '1px solid var(--line)',
                      borderRadius: isUser ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                      padding: '14px 16px',
                      boxShadow: 'var(--shadow-subtle)'
                    }}>
                      <p style={{ margin: 0, fontSize: '13px', lineHeight: '21px', whiteSpace: 'pre-wrap' }}>
                        {msg.text}
                      </p>

                      {/* Assistant Response Metadata Footer */}
                      {!isUser && !msg.error && (
                        <div style={{
                          marginTop: '10px',
                          paddingTop: '8px',
                          borderTop: '1px solid #EDF0F4',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '6px',
                          fontSize: '11px',
                          color: 'var(--muted)'
                        }}>
                          {msg.sources && msg.sources.length > 0 && (
                            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                              <BookOpen size={12} style={{ color: 'var(--navy)' }} />
                              <span>Source: <strong>{msg.sources.join(', ')}</strong></span>
                            </div>
                          )}

                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            {msg.confidence && (
                              <span>Confidence Level: <strong>{msg.confidence}</strong></span>
                            )}

                            {msg.humanReviewRequired && (
                              <Badge tone="warning" icon={<AlertCircle size={10} />}>
                                Human Review Recommended
                              </Badge>
                            )}
                          </div>
                        </div>
                      )}

                      <div style={{
                        marginTop: '6px',
                        fontSize: '10px',
                        textAlign: 'right',
                        opacity: isUser ? 0.7 : 0.5,
                        color: isUser ? 'var(--white)' : 'var(--muted)'
                      }}>
                        {msg.timestamp}
                      </div>
                    </div>

                    {isUser && (
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '8px',
                        background: 'var(--green)',
                        color: 'var(--white)',
                        display: 'grid',
                        placeItems: 'center',
                        flexShrink: 0,
                        marginTop: '2px'
                      }}>
                        <User size={16} />
                      </div>
                    )}
                  </div>
                );
              })}

              {loading && (
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    background: 'var(--navy)',
                    color: 'var(--white)',
                    display: 'grid',
                    placeItems: 'center',
                    flexShrink: 0
                  }}>
                    <Bot size={16} />
                  </div>
                  <div style={{
                    background: 'var(--white)',
                    border: '1px solid var(--line)',
                    borderRadius: '14px 14px 14px 2px',
                    padding: '12px 16px',
                    fontSize: '12px',
                    color: 'var(--muted)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <RefreshCw size={14} className="spin" />
                    <span>Saakshi is evaluating authorized scheme context...</span>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Error Feedback with Retry */}
            {errorMsg && (
              <div style={{
                padding: '10px 16px',
                background: '#FEF2F2',
                borderTop: '1px solid #FECDD3',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                fontSize: '12px',
                color: 'var(--red)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertCircle size={15} />
                  <span>{errorMsg}</span>
                </div>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ padding: '3px 10px', fontSize: '11px', height: '28px' }}
                  onClick={handleRetryLast}
                >
                  <RefreshCw size={12} /> Retry Question
                </button>
              </div>
            )}

            {/* Message Composer Form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              style={{
                padding: '16px',
                background: 'var(--white)',
                borderTop: '1px solid var(--line)',
                display: 'flex',
                gap: '10px',
                alignItems: 'center'
              }}
            >
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask Saakshi in English, Hindi, or Hinglish… (Press Enter to send)"
                disabled={loading}
                style={{
                  flex: 1,
                  height: '44px',
                  padding: '0 16px',
                  borderRadius: 'var(--radius-control)',
                  border: '1px solid var(--border-action)',
                  fontSize: '13px',
                  outline: 'none',
                  background: loading ? '#F1F5F9' : 'var(--white)'
                }}
              />
              <button
                type="submit"
                className="btn btn-primary"
                disabled={!inputMessage.trim() || loading}
                style={{ height: '44px', padding: '0 18px' }}
              >
                {loading ? <RefreshCw size={16} className="spin" /> : <Send size={16} />}
              </button>
            </form>
          </Card>
        </div>

        {/* Right Sidebar: AI Safety Boundaries & Quick Prompts */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
          {/* Quick Prompts Panel */}
          <Card>
            <CardHeader
              title="Suggested Questions"
              subtitle="Click any prompt to ask Saakshi directly."
            />

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {[
                'Why may PMEGP scheme be relevant to my enterprise profile?',
                'What does the UNDER_REVIEW application status mean?',
                'What document checks are required for SIDBI 4E financing?',
                'How does my declared cash flow impact loan eligibility?'
              ].map((promptText, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleSendMessage(promptText)}
                  disabled={loading}
                  style={{
                    textAlign: 'left',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: '1px solid var(--line)',
                    background: '#F8FAFC',
                    fontSize: '12px',
                    color: 'var(--navy)',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontWeight: 500,
                    transition: 'all 0.15s ease'
                  }}
                  onMouseOver={(e) => {
                    if (!loading) e.currentTarget.style.background = '#EEF4FF';
                  }}
                  onMouseOut={(e) => {
                    if (!loading) e.currentTarget.style.background = '#F8FAFC';
                  }}
                >
                  <HelpCircle size={13} style={{ display: 'inline', marginRight: '6px', color: 'var(--navy)' }} />
                  {promptText}
                </button>
              ))}
            </div>
          </Card>

          {/* AI Safety Boundaries Panel */}
          <Card>
            <CardHeader
              title="AI Safety Boundaries"
              subtitle="Statutory guardrails governing Saakshi AI."
            />

            <ul style={{
              margin: 0,
              paddingLeft: '18px',
              fontSize: '12px',
              lineHeight: '20px',
              color: 'var(--muted)'
            }}>
              <li style={{ marginBottom: '8px' }}>
                <strong>No Approval Authority:</strong> Saakshi cannot grant loan approvals, sanctions, or rate commitments.
              </li>
              <li style={{ marginBottom: '8px' }}>
                <strong>No Policy Invention:</strong> Explanations are constrained strictly to verified scheme parameters.
              </li>
              <li style={{ marginBottom: '8px' }}>
                <strong>Account Scoped:</strong> Answers utilize only authorized document and application context.
              </li>
              <li>
                <strong>Audit Logged:</strong> Query logs are preserved for compliance & review.
              </li>
            </ul>
          </Card>
        </div>
      </div>
    </>
  );
}
