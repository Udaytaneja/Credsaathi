import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Download, 
  ShieldCheck, 
  RefreshCw, 
  AlertCircle, 
  Building2, 
  PieChart, 
  CheckCircle2 
} from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import { Button } from '../components/Button';
import Badge from '../components/Badge';
import { services } from '../services';
import type { BankerReportMetrics } from '../types';

export default function BankerReports() {
  const [reports, setReports] = useState<BankerReportMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchReports = async () => {
    setLoading(true);
    setError('');
    try {
      const data = (await services.bankerReports()) as BankerReportMetrics;
      setReports(data);
    } catch {
      setError('Failed to fetch operational report metrics. Please check role permissions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    services.bankerReports()
      .then((data) => {
        if (isMounted) {
          setReports(data as BankerReportMetrics);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setError('Failed to fetch operational report metrics. Please check role permissions.');
          setLoading(false);
        }
      });
    return () => { isMounted = false; };
  }, []);

  return (
    <>
      <PageTitle
        eyebrow="BANKER · REPORTS / प्रचालन रिपोर्ट एवं विश्लेषण"
        title="Organization Portfolio Reports & Pipeline Analytics"
        subtitle="Operational pipeline summaries and metrics for your authorized banking institution. Metrics are calculated by backend reporting services."
        action={
          <Button variant="secondary" onClick={() => window.print()} style={{ fontSize: '12px' }}>
            <Download size={15} /> Export Audit Report
          </Button>
        }
      />

      {/* Loading State */}
      {loading && (
        <Card style={{ padding: '40px', textAlign: 'center' }}>
          <RefreshCw size={24} className="spin" style={{ color: 'var(--navy)', marginBottom: '12px' }} />
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--muted)' }}>
            Generating organization operational pipeline metrics...
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
                Reports Service Unavailable
              </strong>
              <p style={{ margin: '0 0 12px 0', fontSize: '12px', color: '#991B1B' }}>
                {error}
              </p>
              <Button variant="secondary" onClick={fetchReports} style={{ fontSize: '12px' }}>
                <RefreshCw size={13} /> Retry Loading Reports
              </Button>
            </div>
          </div>
        </Card>
      )}

      {!loading && reports && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
          {/* Top Stat Summary Grid */}
          <div className="stat-grid">
            <div className="stat-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span>Submitted Applications</span>
                <BarChart3 size={18} style={{ color: 'var(--navy)' }} />
              </div>
              <strong>{reports.totalSubmitted}</strong>
              <small>Pending Underwriting Desk</small>
            </div>

            <div className="stat-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span>Under Review</span>
                <PieChart size={18} style={{ color: '#0284C7' }} />
              </div>
              <strong>{reports.underReview}</strong>
              <small>Verification In Progress</small>
            </div>

            <div className="stat-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span>Action Required</span>
                <AlertCircle size={18} style={{ color: '#D97706' }} />
              </div>
              <strong>{reports.additionalInfoRequired}</strong>
              <small>Document Correction Needed</small>
            </div>

            <div className="stat-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <span>Completed / Closed</span>
                <CheckCircle2 size={18} style={{ color: '#059669' }} />
              </div>
              <strong>{reports.closed}</strong>
              <small>Sanctioned & Archived</small>
            </div>
          </div>

          {/* Main Pipeline Progress Chart */}
          <Card>
            <CardHeader
              title="Application Pipeline Breakdown"
              subtitle={`Organization Scope: ${reports.authorizedOrganization} · Last Updated: ${reports.lastUpdated}`}
              action={
                <Badge tone="navy" icon={<Building2 size={12} />}>
                  Server Metric Sync
                </Badge>
              }
            />

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '8px' }}>
              {reports.pipelineBreakdown.map((item, idx) => (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                    <strong style={{ color: 'var(--navy)' }}>{item.label}</strong>
                    <span style={{ fontWeight: 600, color: 'var(--muted)' }}>
                      {item.count} applications ({item.percentage})
                    </span>
                  </div>
                  <div className="bar-track" style={{
                    height: '10px',
                    background: '#E2E8F0',
                    borderRadius: '9999px',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      width: item.percentage,
                      height: '100%',
                      background: idx === 0 ? 'var(--navy)' : idx === 1 ? '#0284C7' : idx === 2 ? '#D97706' : '#059669',
                      borderRadius: '9999px',
                      transition: 'width 0.4s ease'
                    }} />
                  </div>
                </div>
              ))}
            </div>

            {/* Disclaimer & Security Footer */}
            <div style={{
              marginTop: '24px',
              padding: '14px 16px',
              background: '#F8FAFC',
              border: '1px solid var(--line)',
              borderRadius: '8px',
              fontSize: '12px',
              color: 'var(--muted)',
              lineHeight: '19px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '10px'
            }}>
              <ShieldCheck size={18} style={{ color: 'var(--navy)', flexShrink: 0, marginTop: '1px' }} />
              <div>
                <strong>Backend Reporting Disclaimer:</strong> {reports.disclaimer}
              </div>
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
