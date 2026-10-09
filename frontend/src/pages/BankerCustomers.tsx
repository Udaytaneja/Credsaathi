import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  Search, 
  ArrowRight, 
  RefreshCw, 
  AlertCircle, 
  ShieldCheck, 
  CheckCircle2, 
  Building2, 
  FileText 
} from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card } from '../components/Card';
import Badge from '../components/Badge';
import { services } from '../services';
import type { BankerCustomer } from '../types';

export default function BankerCustomers() {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<BankerCustomer[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchCustomers = async (query = '') => {
    setLoading(true);
    setError('');
    try {
      const data = (await services.bankerCustomers(query)) as BankerCustomer[];
      setCustomers(data || []);
    } catch {
      setError('Unable to load customer directory. Please check organization authorization.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCustomers(search);
    }, 250);
    return () => clearTimeout(timer);
  }, [search]);

  return (
    <>
      <PageTitle
        eyebrow="BANKER · CUSTOMERS / अधिकृत ग्राहक सूची"
        title="Authorized MSME Customer Directory"
        subtitle="Only customers within your authorized financial institution are visible. Access is enforced server-side via backend multi-tenant security."
        action={
          <Badge tone="navy" icon={<Building2 size={13} />}>
            Branch Customer Scope
          </Badge>
        }
      />

      {/* Search Input Bar */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{
          maxWidth: '480px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          background: 'var(--white)',
          border: '1px solid var(--border-action)',
          borderRadius: 'var(--radius-control)',
          padding: '0 14px',
          height: '42px'
        }}>
          <Search size={18} style={{ color: 'var(--muted)' }} />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search customer name, enterprise, customer ID, or Udyam No…"
            style={{
              border: 'none',
              outline: 'none',
              width: '100%',
              fontSize: '13px',
              background: 'transparent'
            }}
          />
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <Card style={{ padding: '40px', textAlign: 'center' }}>
          <RefreshCw size={24} className="spin" style={{ color: 'var(--navy)', marginBottom: '12px' }} />
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--muted)' }}>
            Retrieving authorized customer directory...
          </p>
        </Card>
      )}

      {/* Error State */}
      {!loading && error && (
        <Card style={{ padding: '24px', background: '#FEF2F2', borderColor: '#FECDD3' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <AlertCircle size={20} style={{ color: 'var(--red)', flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <strong style={{ fontSize: '14px', color: 'var(--navy)', display: 'block', marginBottom: '4px' }}>
                Customer Directory Unavailable
              </strong>
              <p style={{ margin: '0 0 12px 0', fontSize: '12px', color: '#991B1B' }}>
                {error}
              </p>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => fetchCustomers(search)}
                style={{ fontSize: '12px' }}
              >
                <RefreshCw size={13} /> Retry Loading Customers
              </button>
            </div>
          </div>
        </Card>
      )}

      {/* Empty State */}
      {!loading && !error && customers.length === 0 && (
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
            <Users size={24} />
          </div>
          <h3 style={{ margin: '0 0 6px 0', fontSize: '15px', color: 'var(--navy)' }}>No Customers Found</h3>
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--muted)' }}>
            No authorized customer records match your current search query.
          </p>
        </Card>
      )}

      {/* Customer List */}
      {!loading && !error && customers.length > 0 && (
        <Card style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {customers.map((cust, index) => (
              <div
                key={cust.id}
                onClick={() => navigate('/banker/applications')}
                style={{
                  padding: '18px 20px',
                  borderBottom: index < customers.length - 1 ? '1px solid var(--line)' : 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  cursor: 'pointer',
                  transition: 'background 0.15s ease'
                }}
                onMouseOver={(e) => { e.currentTarget.style.background = '#F8FAFC'; }}
                onMouseOut={(e) => { e.currentTarget.style.background = 'transparent'; }}
              >
                {/* Avatar Icon */}
                <div style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '10px',
                  background: '#EEF4FF',
                  color: 'var(--navy)',
                  display: 'grid',
                  placeItems: 'center',
                  flexShrink: 0
                }}>
                  <Users size={20} />
                </div>

                {/* Main Customer Info */}
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <strong style={{ fontSize: '15px', color: 'var(--navy)' }}>{cust.name}</strong>
                    <Badge tone="navy">{cust.id}</Badge>
                    <Badge tone="success" icon={<CheckCircle2 size={10} />}>
                      {cust.verificationStatus}
                    </Badge>
                  </div>

                  <div style={{ fontSize: '13px', color: '#334155', marginBottom: '4px' }}>
                    <strong>{cust.enterpriseName}</strong> · Udyam: <span style={{ color: 'var(--muted)' }}>{cust.udyamNo}</span>
                  </div>

                  <div style={{ display: 'flex', gap: '16px', fontSize: '11px', color: 'var(--muted)' }}>
                    <span>Active Applications: <strong style={{ color: 'var(--navy)' }}>{cust.activeApplicationsCount}</strong></span>
                    <span>Last Activity: {cust.lastActivity}</span>
                    <span>Risk Profile: <strong style={{ color: '#059669' }}>{cust.riskCategory}</strong></span>
                  </div>
                </div>

                {/* Right Action Link */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--navy)', fontWeight: 600, fontSize: '12px' }}>
                  <FileText size={15} />
                  <span>View Applications</span>
                  <ArrowRight size={16} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Security Note */}
      <div style={{
        marginTop: '20px',
        padding: '12px 16px',
        background: '#EFF6FF',
        border: '1px solid #BFDBFE',
        borderRadius: '8px',
        fontSize: '12px',
        color: '#1E40AF',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        <ShieldCheck size={16} style={{ color: '#2563EB', flexShrink: 0 }} />
        <span>
          <strong>Data Privacy Boundary:</strong> Customer information is filtered according to your bank's authorization context. Unassigned or out-of-scope customer profiles are strictly omitted at the backend service layer.
        </span>
      </div>
    </>
  );
}
