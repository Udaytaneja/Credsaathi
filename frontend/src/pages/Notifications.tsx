import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Bell, 
  CheckCircle2, 
  FileWarning, 
  Info, 
  Send, 
  BookOpen, 
  ArrowRight, 
  RefreshCw, 
  AlertCircle,
  Check
} from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card } from '../components/Card';
import Badge from '../components/Badge';
import { services } from '../services';
import type { NotificationItem, NotificationCategory } from '../types';

export default function Notifications() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'ALL' | NotificationCategory>('ALL');

  const fetchNotifications = async () => {
    setLoading(true);
    setError('');
    try {
      const data = (await services.notifications()) as NotificationItem[];
      setNotifications(data || []);
    } catch {
      setError('Unable to fetch notifications. Please verify network connectivity and retry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    services.notifications()
      .then((data) => {
        if (isMounted) {
          setNotifications((data as NotificationItem[]) || []);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setError('Unable to fetch notifications. Please verify network connectivity and retry.');
          setLoading(false);
        }
      });
    return () => { isMounted = false; };
  }, []);

  const handleMarkAsRead = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await services.markNotificationRead(id);
      setNotifications(prev =>
        prev.map(item => item.id === id ? { ...item, isRead: true } : item)
      );
    } catch {
      // Non-blocking UI update
    }
  };

  const handleNotificationClick = (item: NotificationItem) => {
    if (!item.isRead) {
      services.markNotificationRead(item.id);
    }
    if (item.actionUrl) {
      navigate(item.actionUrl);
    }
  };

  const getCategoryIcon = (category: NotificationCategory) => {
    switch (category) {
      case 'ADDITIONAL_DOCUMENTS':
        return <FileWarning size={18} style={{ color: '#D97706' }} />;
      case 'APPLICATION_TRANSMISSION':
        return <Send size={18} style={{ color: '#059669' }} />;
      case 'DOCUMENT_UPLOAD_CONFIRMATION':
        return <CheckCircle2 size={18} style={{ color: '#2563EB' }} />;
      case 'SCHEME_POLICY_INFO':
        return <BookOpen size={18} style={{ color: '#6366F1' }} />;
      default:
        return <Info size={18} style={{ color: '#64748B' }} />;
    }
  };

  const getCategoryTone = (category: NotificationCategory): 'warning' | 'success' | 'navy' | 'neutral' => {
    switch (category) {
      case 'ADDITIONAL_DOCUMENTS':
        return 'warning';
      case 'APPLICATION_TRANSMISSION':
        return 'success';
      case 'DOCUMENT_UPLOAD_CONFIRMATION':
        return 'navy';
      case 'SCHEME_POLICY_INFO':
        return 'neutral';
      default:
        return 'neutral';
    }
  };

  const filteredNotifications = notifications.filter(item => {
    if (activeTab === 'ALL') return true;
    return item.category === activeTab;
  });

  const unreadCount = notifications.filter(n => !n.isRead).length;

  return (
    <>
      <PageTitle
        eyebrow="NOTIFICATIONS & ALERTS / अधिसूचनाएं"
        title="Updates & Requests"
        subtitle="Important application status changes, document requests, transmission receipts, and scheme updates."
        action={
          unreadCount > 0 ? (
            <Badge tone="warning" icon={<Bell size={12} />}>
              {unreadCount} Unread Alert{unreadCount > 1 ? 's' : ''}
            </Badge>
          ) : (
            <Badge tone="success" icon={<CheckCircle2 size={12} />}>
              All Caught Up
            </Badge>
          )
        }
      />

      {/* Category Filter Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {[
          { key: 'ALL', label: 'All Updates' },
          { key: 'ADDITIONAL_DOCUMENTS', label: 'Document Requests' },
          { key: 'APPLICATION_TRANSMISSION', label: 'Transmission Status' },
          { key: 'DOCUMENT_UPLOAD_CONFIRMATION', label: 'Document Validations' },
          { key: 'SCHEME_POLICY_INFO', label: 'Scheme Policies' }
        ].map(tab => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveTab(tab.key as 'ALL' | NotificationCategory)}
            className="btn"
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              borderRadius: '9999px',
              border: activeTab === tab.key ? '1px solid var(--navy)' : '1px solid var(--line)',
              background: activeTab === tab.key ? 'var(--navy)' : 'var(--white)',
              color: activeTab === tab.key ? 'var(--white)' : 'var(--navy)',
              fontWeight: activeTab === tab.key ? 600 : 400,
              cursor: 'pointer'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Loading State */}
      {loading && (
        <Card style={{ padding: '40px', textAlign: 'center' }}>
          <RefreshCw size={24} className="spin" style={{ color: 'var(--navy)', marginBottom: '12px' }} />
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--muted)' }}>
            Retrieving latest notification updates from secure server...
          </p>
        </Card>
      )}

      {/* Error State with Retry */}
      {!loading && error && (
        <Card style={{ padding: '24px', background: '#FEF2F2', borderColor: '#FECDD3' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <AlertCircle size={20} style={{ color: 'var(--red)', flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <strong style={{ fontSize: '14px', color: 'var(--navy)', display: 'block', marginBottom: '4px' }}>
                Notification Service Unavailable
              </strong>
              <p style={{ margin: '0 0 12px 0', fontSize: '12px', color: '#991B1B' }}>
                {error}
              </p>
              <button type="button" className="btn btn-secondary" onClick={fetchNotifications} style={{ fontSize: '12px', padding: '6px 14px' }}>
                <RefreshCw size={13} /> Retry Loading Notifications
              </button>
            </div>
          </div>
        </Card>
      )}

      {/* Empty State */}
      {!loading && !error && filteredNotifications.length === 0 && (
        <Card style={{ padding: '48px 24px', textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            background: '#F1F5F9',
            display: 'grid',
            placeItems: 'center',
            margin: '0 auto 16px auto',
            color: 'var(--muted)'
          }}>
            <Bell size={24} />
          </div>
          <h3 style={{ margin: '0 0 6px 0', fontSize: '15px', color: 'var(--navy)' }}>No Notifications Found</h3>
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--muted)', maxWidth: '420px', marginLeft: 'auto', marginRight: 'auto' }}>
            There are no notifications present under the selected filter tab. Future application status updates and lender requests will appear here.
          </p>
        </Card>
      )}

      {/* Notification List */}
      {!loading && !error && filteredNotifications.length > 0 && (
        <Card style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {filteredNotifications.map((item, index) => (
              <div
                key={item.id}
                onClick={() => handleNotificationClick(item)}
                style={{
                  padding: '18px 20px',
                  borderBottom: index < filteredNotifications.length - 1 ? '1px solid var(--line)' : 'none',
                  background: item.isRead ? 'var(--white)' : '#F0F9FF',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '16px',
                  cursor: item.actionUrl ? 'pointer' : 'default',
                  transition: 'background 0.15s ease'
                }}
                onMouseOver={(e) => {
                  if (item.actionUrl) e.currentTarget.style.background = item.isRead ? '#F8FAFC' : '#E0F2FE';
                }}
                onMouseOut={(e) => {
                  if (item.actionUrl) e.currentTarget.style.background = item.isRead ? 'var(--white)' : '#F0F9FF';
                }}
              >
                {/* Category Icon Badge */}
                <div style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  background: item.isRead ? '#F1F5F9' : '#FFFFFF',
                  border: '1px solid var(--line)',
                  display: 'grid',
                  placeItems: 'center',
                  flexShrink: 0,
                  marginTop: '2px'
                }}>
                  {getCategoryIcon(item.category)}
                </div>

                {/* Main Notification Content */}
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexWrap: 'wrap' }}>
                    <Badge tone={getCategoryTone(item.category)}>
                      {item.category.replace(/_/g, ' ')}
                    </Badge>

                    {!item.isRead && (
                      <span style={{
                        padding: '2px 8px',
                        borderRadius: '9999px',
                        background: '#0284C7',
                        color: 'var(--white)',
                        fontSize: '10px',
                        fontWeight: 600
                      }}>
                        NEW
                      </span>
                    )}

                    <span style={{ fontSize: '11px', color: 'var(--muted)', marginLeft: 'auto' }}>
                      {item.timestamp}
                    </span>
                  </div>

                  <strong style={{ fontSize: '14px', color: 'var(--navy)', display: 'block', marginBottom: '4px' }}>
                    {item.title}
                  </strong>
                  <p style={{ margin: 0, fontSize: '13px', lineHeight: '20px', color: '#475569' }}>
                    {item.message}
                  </p>

                  {/* Actions Bar */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginTop: '12px' }}>
                    {item.actionUrl && (
                      <span style={{
                        fontSize: '12px',
                        fontWeight: 600,
                        color: 'var(--navy)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        {item.actionLabel || 'View Details'} <ArrowRight size={13} />
                      </span>
                    )}

                    {!item.isRead && (
                      <button
                        type="button"
                        onClick={(e) => handleMarkAsRead(item.id, e)}
                        style={{
                          background: 'none',
                          border: 'none',
                          padding: 0,
                          fontSize: '11px',
                          color: 'var(--muted)',
                          textDecoration: 'underline',
                          cursor: 'pointer',
                          marginLeft: item.actionUrl ? '0' : 'auto'
                        }}
                      >
                        <Check size={11} style={{ display: 'inline', marginRight: '2px' }} />
                        Mark as Read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </>
  );
}
