import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Plus, FileText, Info, RefreshCw } from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import StatusPill from '../components/StatusPill';
import { Button } from '../components/Button';
import { services } from '../services';
import type { Application } from '../types';

export default function Applications() {
  const navigate = useNavigate();

  const [filter, setFilter] = useState('all');
  const [appList, setAppList] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const fetchApplications = useCallback(async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = (await services.applications()) as Application[];
      setAppList(data);
    } catch {
      setErrorMsg('Failed to load applications. Please click retry.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    (services.applications() as Promise<Application[]>).then((data) => {
      if (isMounted) {
        setAppList(data);
        setLoading(false);
      }
    }).catch(() => {
      if (isMounted) {
        setErrorMsg('Failed to load applications. Please click retry.');
        setLoading(false);
      }
    });
    return () => { isMounted = false; };
  }, []);

  const filteredApps = useMemo(() => {
    if (filter === 'all') return appList;
    if (filter === 'review') return appList.filter((a) => a.status === 'UNDER_REVIEW' || a.status === 'ADDITIONAL_INFO_REQUIRED');
    if (filter === 'accepted') return appList.filter((a) => a.status === 'ACCEPTED');
    return appList;
  }, [appList, filter]);

  return (
    <>
      <PageTitle
        eyebrow="APPLICATIONS PORTAL"
        title="Your Applications / आपके आवेदन"
        subtitle="Track every application using the lender-defined status returned directly from the backend state machine."
        action={
          <Button variant="primary" onClick={() => navigate('/applicant/applications/new')}>
            <Plus size={17} /> New Application
          </Button>
        }
      />

      {/* FILTER TABS */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        {[
          { id: 'all', label: 'All Applications' },
          { id: 'review', label: 'Under Review / Action Required' },
          { id: 'accepted', label: 'Accepted / Sanctioned' },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`btn ${filter === tab.id ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 14px', fontSize: '12px' }}
            onClick={() => setFilter(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* ERROR FEEDBACK BANNER */}
      {errorMsg && (
        <div className="form-error" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Info size={16} style={{ display: 'inline', marginRight: '6px' }} />
            {errorMsg}
          </div>
          <Button variant="ghost" size="md" onClick={fetchApplications}>
            <RefreshCw size={14} /> Retry Loading
          </Button>
        </div>
      )}

      <Card>
        <CardHeader
          title="Application History / आवेदन इतिहास"
          subtitle="Status transitions are governed server-side. No frontend-calculated decisions are displayed."
        />

        {loading ? (
          <div style={{ padding: '24px', textAlign: 'center', color: '#64748B' }}>
            Loading applications list…
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Application ID &amp; Date</th>
                  <th>Loan Scheme</th>
                  <th>Requested Amount</th>
                  <th>Status</th>
                  <th>Last Updated</th>
                  <th style={{ textAlign: 'right' }}>Track Progress</th>
                </tr>
              </thead>
              <tbody>
                {filteredApps.map((a) => (
                  <tr key={a.id}>
                    <td>
                      <strong style={{ color: '#0B192C' }}>{a.id}</strong>
                      <span style={{ fontSize: '11px', color: '#64748B' }}>Submitted: {a.submittedAt}</span>
                    </td>
                    <td>
                      <strong>{a.schemeName}</strong>
                      <span style={{ fontSize: '11px', color: '#64748B' }}>State Bank of India</span>
                    </td>
                    <td>
                      <strong className="money" style={{ color: '#0B192C' }}>{a.amountLabel}</strong>
                    </td>
                    <td>
                      <StatusPill status={a.status} />
                    </td>
                    <td>
                      <span style={{ fontSize: '11px', color: '#64748B' }}>{a.updatedAt}</span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link className="btn btn-secondary" to={`/applicant/applications/${a.id}`} style={{ padding: '6px 10px', fontSize: '11px' }}>
                        View Tracker <ArrowRight size={14} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && filteredApps.length === 0 && (
          <div className="empty-state">
            <FileText size={32} />
            <h3>No applications found</h3>
            <p>You have not created any applications under this filter yet.</p>
            <Button
              variant="primary"
              size="md"
              style={{ marginTop: '12px' }}
              onClick={() => navigate('/applicant/applications/new')}
            >
              Start New Application
            </Button>
          </div>
        )}
      </Card>
    </>
  );
}
