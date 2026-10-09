import React from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, CheckCircle2, FileText, ShieldCheck, Sparkles, ExternalLink, Info } from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import Badge from '../components/Badge';
import { Button } from '../components/Button';
import { schemes } from '../services/mock/data';

export default function SchemeDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  // Find target scheme or fallback to first item
  const scheme = schemes.find((x) => x.id === id) || schemes[0];

  return (
    <>
      <Link className="back-link" to="/applicant/schemes" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '16px', color: '#64748B', fontWeight: '700', fontSize: '12px' }}>
        <ArrowLeft size={16} /> Back to Scheme Discovery
      </Link>

      <PageTitle
        eyebrow="SCHEME DETAILS &amp; ELIGIBILITY CRITERIA"
        title={scheme.name}
        subtitle={scheme.description}
        action={
          <Button variant="primary" onClick={() => navigate('/applicant/applications/new')}>
            Start Guided Application <ArrowRight size={16} />
          </Button>
        }
      />

      <div className="details-grid">
        {/* MAIN DETAILS COLUMN */}
        <div>
          {/* STATUTORY BANNER */}
          <Card style={{ marginBottom: '18px' }}>
            <div className="detail-banner" style={{ display: 'flex', gap: '12px', background: '#F4FBF8', border: '1px solid #CDEEE0', padding: '16px', borderRadius: '10px' }}>
              <ShieldCheck size={24} style={{ color: '#059669', flexShrink: 0 }} />
              <div>
                <strong style={{ fontSize: '13px', color: '#0B192C' }}>Indicative Scheme Information &amp; Guidelines</strong>
                <span style={{ display: 'block', fontSize: '11px', color: '#64748B', marginTop: '2px' }}>
                  Verify current official eligibility, interest rates, and loan terms with your lending institution before applying.
                </span>
              </div>
            </div>

            {/* AI EXPLANATION BLOCK */}
            <div style={{ marginTop: '20px' }}>
              <CardHeader
                title="Why This Scheme May Be Relevant To You"
                subtitle="AI-assisted match breakdown based on your self-declared business profile."
              />
              <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '10px', padding: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                  <Sparkles size={16} style={{ color: '#059669' }} />
                  <span style={{ fontSize: '11px', fontWeight: '800', color: '#059669', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                    AI-Assisted Relevance Analysis
                  </span>
                </div>
                <ul className="reason-list" style={{ padding: 0, margin: 0, listStyle: 'none' }}>
                  {scheme.reasons.map((reason, idx) => (
                    <li key={idx} style={{ display: 'flex', gap: '8px', alignItems: 'flex-start', fontSize: '12px', color: '#334155', marginBottom: '8px' }}>
                      <CheckCircle2 size={16} style={{ color: '#059669', flexShrink: 0, marginTop: '2px' }} />
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* INDICATIVE SCHEME BENEFITS */}
            <div style={{ marginTop: '24px' }}>
              <CardHeader title="Indicative Key Features &amp; Benefits" />
              <div className="scheme-meta" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', background: '#F7F9FC', padding: '14px', borderRadius: '10px', textAlign: 'center' }}>
                <div>
                  <b style={{ display: 'block', fontSize: '10px', color: '#64748B', textTransform: 'uppercase' }}>Primary Purpose</b>
                  <strong style={{ fontSize: '13px', color: '#0B192C' }}>{scheme.purpose}</strong>
                </div>
                <div>
                  <b style={{ display: 'block', fontSize: '10px', color: '#64748B', textTransform: 'uppercase' }}>Collateral Mandate</b>
                  <strong style={{ fontSize: '13px', color: '#059669' }}>CGTMSE Covered</strong>
                </div>
                <div>
                  <b style={{ display: 'block', fontSize: '10px', color: '#64748B', textTransform: 'uppercase' }}>Last Verified</b>
                  <strong style={{ fontSize: '13px', color: '#0B192C' }}>{scheme.lastVerified}</strong>
                </div>
              </div>
            </div>

            {/* REQUIRED DOCUMENTS CHECKLIST */}
            <div style={{ marginTop: '24px' }}>
              <CardHeader
                title="Required Application Documents"
                subtitle="Ensure these documents are uploaded to your Document Vault before submitting."
              />
              <ul className="document-list" style={{ padding: 0, margin: 0, listStyle: 'none' }}>
                {scheme.documents.map((doc, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 0', borderBottom: '1px solid #EDF0F4', fontSize: '12px' }}>
                    <FileText size={18} style={{ color: '#0B192C' }} />
                    <span style={{ flex: 1, color: '#334155' }}>{doc}</span>
                    <Badge tone="success">Ready in Vault</Badge>
                  </li>
                ))}
              </ul>
            </div>

            {/* AUTHORITATIVE SOURCE BOX */}
            <div className="source-box" style={{ marginTop: '24px', border: '1px solid #DCE3EC', background: '#F8FAFC', borderRadius: '10px', padding: '16px' }}>
              <strong style={{ fontSize: '12px', color: '#0B192C' }}>Official Source &amp; Reference Guidelines</strong>
              <p style={{ fontSize: '11px', color: '#64748B', margin: '4px 0 8px', lineHeight: '18px' }}>
                {scheme.source}
              </p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px', color: '#94A3B8' }}>
                <span>Verification Timestamp: {scheme.lastVerified}</span>
                <span className="text-link" style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}>
                  Official Portal <ExternalLink size={12} />
                </span>
              </div>
            </div>

            {/* BOTTOM ACTIONS */}
            <div className="form-actions" style={{ marginTop: '24px' }}>
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate('/applicant/schemes')}
              >
                Back to Discovery
              </Button>

              <Button
                variant="primary"
                onClick={() => navigate('/applicant/applications/new')}
              >
                Start Guided Application <ArrowRight size={16} />
              </Button>
            </div>
          </Card>
        </div>

        {/* SIDEBAR RELEVANCE & APPLICATION STATUS */}
        <aside>
          <Card>
            <Badge tone="success" style={{ fontSize: '12px', padding: '6px 12px' }}>
              {scheme.matchLabel}
            </Badge>

            <h3 className="side-title" style={{ fontSize: '16px', margin: '14px 0 6px', color: '#0B192C' }}>
              Relevance Signal Summary
            </h3>

            <p className="muted" style={{ fontSize: '11px', lineHeight: '18px', margin: 0 }}>
              This relevance signal is calculated from self-declared profile criteria. It is <strong>NOT</strong> an approval probability, a credit score, or a guarantee of loan sanction.
            </p>

            <div className="info-box" style={{ marginTop: '16px' }}>
              <Info size={16} style={{ color: '#0B192C', flexShrink: 0 }} />
              <div>
                <strong>Application Status</strong>
                <p>No active application started for this scheme yet.</p>
              </div>
            </div>

            <Button
              variant="trust"
              size="md"
              full
              style={{ marginTop: '16px' }}
              onClick={() => navigate('/applicant/applications/new')}
            >
              Apply for {scheme.name}
            </Button>
          </Card>

          <Card style={{ background: '#F8FAFC', borderColor: '#E2E8F0' }}>
            <strong style={{ fontSize: '12px', color: '#0B192C' }}>Statutory Disclaimer</strong>
            <p style={{ fontSize: '10px', color: '#64748B', lineHeight: '16px', marginTop: '4px' }}>
              CredSaathi is a technology facilitation platform for scheme discovery and document organization. CredSaathi is not a bank or lender and does not approve or disburse loans.
            </p>
          </Card>
        </aside>
      </div>
    </>
  );
}
