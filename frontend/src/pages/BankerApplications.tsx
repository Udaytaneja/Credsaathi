import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  ArrowRight, 
  RefreshCw, 
  AlertCircle, 
  FileText, 
  Building2, 
  ShieldCheck, 
  FileCheck 
} from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card } from '../components/Card';
import StatusPill from '../components/StatusPill';
import Badge from '../components/Badge';
import { services } from '../services';
import type { Application } from '../types';

export default function BankerApplications() {
  const navigate = useNavigate();
  const [applications, setApplications] = useState<Application[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const fetchApplications = async (query = '') => {
    setLoading(true);
    setError('');
    try {
      const data = (await services.bankerApplications(query)) as Application[];
      setApplications(data || []);
    } catch {
      setError('Failed to fetch organization applications. Please verify network or role permission.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchApplications(search);
    }, 250);
    return () => clearTimeout(timer);
  }, [search]);

  const filteredApplications = applications.filter((app) => {
    if (statusFilter === 'ALL') return true;
    return app.status === statusFilter;
  });

  return (
    <>
      <PageTitle
        eyebrow="BANKER · APPLICATIONS / ऋण आवेदन समीक्षा"
        title="Organization Application Portfolio"
        subtitle="Review organization-scoped applications. Frontend provides readiness and document inspection; official sanction decisioning remains strictly server-side."
        action={
          <Badge tone="navy" icon={<Building2 size={13} />}>
            Authorized Branch Scope
          </Badge>
        }
      />

      {/* Search & Filter Bar */}
      <div style={{ display: 'flex', gap: '14px', marginBottom: '20px', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{
          flex: 1,
          minWidth: '280px',
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
            placeholder="Search by Application ID, Customer Name, Enterprise, or Scheme…"
            style={{
              border: 'none',
              outline: 'none',
              width: '100%',
              fontSize: '13px',
              background: 'transparent'
            }}
          />
        </div>

        {/* Status Filter Tabs */}
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {[
            { key: 'ALL', label: 'All Statuses' },
            { key: 'SUBMITTED', label: 'Submitted' },
            { key: 'UNDER_REVIEW', label: 'Under Review' },
            { key: 'ADDITIONAL_INFO_REQUIRED', label: 'Action Required' }
          ].map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setStatusFilter(tab.key)}
              style={{
                padding: '6px 14px',
                fontSize: '12px',
                borderRadius: '9999px',
                border: statusFilter === tab.key ? '1px solid var(--navy)' : '1px solid var(--line)',
                background: statusFilter === tab.key ? 'var(--navy)' : 'var(--white)',
                color: statusFilter === tab.key ? 'var(--white)' : 'var(--navy)',
                fontWeight: statusFilter === tab.key ? 600 : 400,
                cursor: 'pointer'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <Card style={{ padding: '40px', textAlign: 'center' }}>
          <RefreshCw size={24} className="spin" style={{ color: 'var(--navy)', marginBottom: '12px' }} />
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--muted)' }}>
            Loading authorized application records...
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
                Application Fetch Failed
              </strong>
              <p style={{ margin: '0 0 12px 0', fontSize: '12px', color: '#991B1B' }}>
                {error}
              </p>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => fetchApplications(search)}
                style={{ fontSize: '12px' }}
              >
                <RefreshCw size={13} /> Retry Search
              </button>
            </div>
          </div>
        </Card>
      )}

      {/* Empty State */}
      {!loading && !error && filteredApplications.length === 0 && (
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
            <FileText size={24} />
          </div>
          <h3 style={{ margin: '0 0 6px 0', fontSize: '15px', color: 'var(--navy)' }}>No Applications Match Your Criteria</h3>
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--muted)' }}>
            Try adjusting your search query or status filter.
          </p>
        </Card>
      )}

      {/* Applications Table */}
      {!loading && !error && filteredApplications.length > 0 && (
        <Card style={{ padding: 0, overflow: 'hidden' }}>
          <div className="table-wrap">
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
              <thead>
                <tr style={{ background: '#F8FAFC', borderBottom: '1px solid var(--line)' }}>
                  <th style={{ padding: '14px 18px', fontWeight: 600, color: 'var(--navy)' }}>Application ID</th>
                  <th style={{ padding: '14px 18px', fontWeight: 600, color: 'var(--navy)' }}>Customer & Enterprise</th>
                  <th style={{ padding: '14px 18px', fontWeight: 600, color: 'var(--navy)' }}>Scheme Name</th>
                  <th style={{ padding: '14px 18px', fontWeight: 600, color: 'var(--navy)' }}>Requested Capital</th>
                  <th style={{ padding: '14px 18px', fontWeight: 600, color: 'var(--navy)' }}>Readiness</th>
                  <th style={{ padding: '14px 18px', fontWeight: 600, color: 'var(--navy)' }}>Status</th>
                  <th style={{ padding: '14px 18px', textAlign: 'right' }} />
                </tr>
              </thead>
              <tbody>
                {filteredApplications.map((app) => (
                  <tr
                    key={app.id}
                    onClick={() => navigate(`/applicant/applications/${app.id}`)}
                    style={{
                      borderBottom: '1px solid var(--line)',
                      cursor: 'pointer',
                      transition: 'background 0.15s ease'
                    }}
                    onMouseOver={(e) => { e.currentTarget.style.background = '#F8FAFC'; }}
                    onMouseOut={(e) => { e.currentTarget.style.background = 'transparent'; }}
                  >
                    <td style={{ padding: '14px 18px', fontWeight: 600, color: 'var(--navy)' }}>
                      {app.id}
                    </td>
                    <td style={{ padding: '14px 18px' }}>
                      <strong style={{ display: 'block', color: 'var(--navy)', fontSize: '13px' }}>
                        {app.customerName || 'Applicant'}
                      </strong>
                      <span style={{ fontSize: '11px', color: 'var(--muted)' }}>
                        {app.enterpriseName || 'MSME Enterprise'}
                      </span>
                    </td>
                    <td style={{ padding: '14px 18px', color: '#334155' }}>
                      {app.schemeName}
                    </td>
                    <td style={{ padding: '14px 18px', fontWeight: 600, color: 'var(--navy)' }}>
                      {app.amountLabel}
                    </td>
                    <td style={{ padding: '14px 18px' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: '#059669', fontWeight: 600 }}>
                        <FileCheck size={14} /> {app.readinessScore || '85%'}
                      </span>
                    </td>
                    <td style={{ padding: '14px 18px' }}>
                      <StatusPill status={app.status} />
                    </td>
                    <td style={{ padding: '14px 18px', textAlign: 'right' }}>
                      <button
                        type="button"
                        className="icon-link"
                        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                      >
                        <ArrowRight size={17} style={{ color: 'var(--navy)' }} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Compliance Footer Note */}
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
          <strong>Authorization Guardrail:</strong> Application view rights are locked to your bank branch ID. No autonomous approval or rejection commands are executed by frontend code.
        </span>
      </div>
    </>
  );
}
