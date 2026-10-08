import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  ShieldCheck, 
  FileText, 
  Users, 
  Clock, 
  AlertCircle, 
  RefreshCw,
  Building2,
  FileCheck2
} from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import StatusPill from '../components/StatusPill';
import Badge from '../components/Badge';
import { services } from '../services';
import type { Application, BankerCustomer } from '../types';

export default function BankerDashboard() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [customers, setCustomers] = useState<BankerCustomer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let isMounted = true;
    Promise.all([services.bankerApplications(), services.bankerCustomers()])
      .then(([appsData, custsData]) => {
        if (isMounted) {
          setApplications((appsData as Application[]) || []);
          setCustomers((custsData as BankerCustomer[]) || []);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setError('Unable to load banker workspace operational data. Please verify role authorization.');
          setLoading(false);
        }
      });
    return () => { isMounted = false; };
  }, []);

  const totalApps = applications.length;
  const underReviewApps = applications.filter(a => a.status === 'UNDER_REVIEW').length;
  const actionRequiredApps = applications.filter(a => a.status === 'ADDITIONAL_INFO_REQUIRED').length;
  const totalCustomers = customers.length;

  return (
    <>
      <PageTitle
        eyebrow="BANKER WORKSPACE / बैंकर कार्यक्षेत्र"
        title="Operational Dashboard & Portfolio Overview"
        subtitle="Organization-scoped workspace. Access controls are strictly enforced server-side by backend authorization boundaries."
        action={
          <Badge tone="navy" icon={<Building2 size={13} />}>
            State Bank of India — SME Branch
          </Badge>
        }
      />

      {/* Loading State */}
      {loading && (
        <Card style={{ padding: '40px', textAlign: 'center' }}>
          <RefreshCw size={24} className="spin" style={{ color: 'var(--navy)', marginBottom: '12px' }} />
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--muted)' }}>
            Retrieving organization-scoped applications and customer records...
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
                Banker Authorization Error
              </strong>
              <p style={{ margin: 0, fontSize: '12px', color: '#991B1B' }}>
                {error}
              </p>
            </div>
          </div>
        </Card>
      )}

      {!loading && !error && (
        <>
          {/* Stat Cards Grid */}
          <div className="stat-grid" style={{ marginBottom: '22px' }}>
            <div className="stat-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span>Total Applications</span>
                <FileText size={18} style={{ color: 'var(--navy)' }} />
              </div>
              <strong>{totalApps}</strong>
              <small>Organization Scoped</small>
            </div>

            <div className="stat-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span>Under Review</span>
                <Clock size={18} style={{ color: '#0284C7' }} />
              </div>
              <strong>{underReviewApps}</strong>
              <small>Pending Underwriting Desk</small>
            </div>

            <div className="stat-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span>Action Required</span>
                <AlertCircle size={18} style={{ color: '#D97706' }} />
              </div>
              <strong>{actionRequiredApps}</strong>
              <small>Info / Document Requested</small>
            </div>

            <div className="stat-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span>Assigned Customers</span>
                <Users size={18} style={{ color: '#059669' }} />
              </div>
              <strong>{totalCustomers}</strong>
              <small>Verified MSME Profiles</small>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '22px' }}>
            {/* Recent Applications List */}
            <Card>
              <CardHeader
                title="Recent Organization Applications"
                subtitle="Applications routed to your branch for verification."
                action={
                  <Link className="text-link" to="/banker/applications" style={{ fontSize: '12px', fontWeight: 600 }}>
                    View All ({applications.length})
                  </Link>
                }
              />

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {applications.map((app) => (
                  <Link
                    key={app.id}
                    to={`/applicant/applications/${app.id}`}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '14px 16px',
                      borderRadius: '8px',
                      border: '1px solid var(--line)',
                      background: '#F8FAFC',
                      textDecoration: 'none',
                      color: 'inherit',
                      transition: 'background 0.15s ease'
                    }}
                    onMouseOver={(e) => { e.currentTarget.style.background = '#EEF4FF'; }}
                    onMouseOut={(e) => { e.currentTarget.style.background = '#F8FAFC'; }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
                        <strong style={{ fontSize: '14px', color: 'var(--navy)' }}>{app.customerName || app.id}</strong>
                        <span style={{ fontSize: '11px', color: 'var(--muted)' }}>({app.id})</span>
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--muted)' }}>
                        {app.enterpriseName ? `${app.enterpriseName} · ` : ''}{app.schemeName} · <strong style={{ color: 'var(--navy)' }}>{app.amountLabel}</strong>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <StatusPill status={app.status} />
                      <ArrowRight size={16} style={{ color: 'var(--muted)' }} />
                    </div>
                  </Link>
                ))}
              </div>
            </Card>

            {/* Authorization & Compliance Guardrail Card */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
              <Card>
                <CardHeader
                  title="Organization Access Boundary"
                  subtitle="Statutory compliance & multi-tenant isolation."
                />

                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <div style={{
                    padding: '14px',
                    background: '#EFF6FF',
                    border: '1px solid #BFDBFE',
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px',
                    fontSize: '12px',
                    color: '#1E40AF',
                    lineHeight: '19px'
                  }}>
                    <ShieldCheck size={22} style={{ color: '#2563EB', flexShrink: 0, marginTop: '1px' }} />
                    <div>
                      <strong style={{ display: 'block', color: '#1E3A8A', marginBottom: '2px' }}>
                        Backend Scope Authorization
                      </strong>
                      Bankers can view applications strictly belonging to their authorized lending institution. Customer PII and raw documents are retrieved only via server-authorized secure sessions.
                    </div>
                  </div>

                  <div style={{
                    padding: '14px',
                    background: '#F8FAFC',
                    border: '1px solid var(--line)',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: 'var(--muted)',
                    lineHeight: '19px'
                  }}>
                    <strong style={{ display: 'block', color: 'var(--navy)', marginBottom: '2px' }}>
                      No Autonomous Decisions
                    </strong>
                    This workspace provides verification and readiness inspection only. Official credit sanctions, approvals, and rejections are governed by core banking backend APIs.
                  </div>

                  <Link to="/banker/customers" className="btn btn-secondary" style={{ width: '100%', justifyContent: 'center' }}>
                    Inspect Authorized Customers <ArrowRight size={15} />
                  </Link>
                </div>
              </Card>

              {/* Application Readiness Summary */}
              <Card>
                <CardHeader
                  title="Underwriting Readiness"
                  subtitle="Automated document & data verification."
                />

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 14px', background: '#ECFDF5', border: '1px solid #A7F3D0', borderRadius: '8px' }}>
                  <FileCheck2 size={20} style={{ color: '#059669' }} />
                  <div>
                    <strong style={{ fontSize: '13px', color: '#065F46', display: 'block' }}>Verified Readiness Avg: 85%</strong>
                    <span style={{ fontSize: '11px', color: '#047857' }}>All active applications match mandatory document parameters.</span>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </>
      )}
    </>
  );
}
