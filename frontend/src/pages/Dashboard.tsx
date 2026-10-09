import React from 'react';
import { ArrowRight, CheckCircle2, Clock3, FileText, Search, ShieldCheck, Sparkles, WalletCards, UserRound, Calculator } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, CardHeader } from '../components/Card';
import Badge from '../components/Badge';
import StatusPill from '../components/StatusPill';
import PageTitle from '../components/PageTitle';
import Button from '../components/Button';
import { applications, financial, schemes } from '../services/mock/data';
import { getSession } from '../lib/storage';

export default function Dashboard() {
  const navigate = useNavigate();
  const session = getSession();
  const userName = session?.name || 'Aarohi';

  return (
    <>
      {/* PAGE TITLE & ACTION */}
      <PageTitle
        eyebrow="APPLICANT WORKSPACE / आवेदक डैशबोर्ड"
        title={`Good evening, ${userName}`}
        subtitle="Your loan discovery, document preparation, and application journey in one place."
        action={
          <Link className="btn btn-primary" to="/applicant/schemes">
            Explore Schemes <ArrowRight size={17} />
          </Link>
        }
      />

      {/* STAT CARDS GRID */}
      <div className="stat-grid">
        <StatCard
          icon={<FileText size={18} />}
          label="Active Applications"
          value="2"
          hint="1 under review by lender"
        />
        <StatCard
          icon={<Search size={18} />}
          label="Relevant Loan Schemes"
          value="8"
          hint="Based on profile classification"
        />
        <StatCard
          icon={<WalletCards size={18} />}
          label="Monthly Cash Flow"
          value={financial.remainingCashFlow}
          hint="Declared remaining surplus"
        />
        <StatCard
          icon={<ShieldCheck size={18} />}
          label="Profile Readiness"
          value="75%"
          hint="Step 3 of 3 completed"
        />
      </div>

      {/* ONBOARDING PROGRESSION BANNER */}
      <Card style={{ background: '#F8FAFC', borderColor: '#E2E8F0', padding: '16px 20px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <span style={{ fontSize: '11px', fontWeight: '800', color: '#059669', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              PROGRESSIVE JOURNEY · 75% COMPLETE
            </span>
            <h3 style={{ margin: '4px 0 2px', fontSize: '15px', color: '#0B192C' }}>
              Financial Profile Ready. Next: Explore Scheme Eligibility.
            </h3>
            <p style={{ margin: 0, fontSize: '12px', color: '#64748B' }}>
              Complete final document uploads in your vault to unlock 1-click application preparation.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <Button variant="secondary" size="md" onClick={() => navigate('/applicant/financial-profile')}>
              Review Financials
            </Button>
            <Button variant="primary" size="md" onClick={() => navigate('/applicant/schemes')}>
              Explore Schemes <ArrowRight size={15} />
            </Button>
          </div>
        </div>
      </Card>

      {/* MAIN DASHBOARD GRID */}
      <div className="dashboard-grid">
        {/* LEFT COLUMN: APPLICATIONS & RECOMMENDED SCHEMES */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {/* APPLICATION ACTIVITY */}
          <Card>
            <CardHeader
              title="Application Activity / आवेदन स्थिति"
              subtitle="Status updates read directly from backend lender state machine."
              action={<Link className="text-link" to="/applicant/applications">View all applications</Link>}
            />

            <div className="timeline">
              {applications.map((app, i) => (
                <div className="timeline-item" key={app.id}>
                  <div className="timeline-dot">
                    {i === 0 ? <Clock3 size={15} /> : <CheckCircle2 size={15} />}
                  </div>
                  <div className="timeline-content">
                    <div className="row-between">
                      <strong>{app.schemeName}</strong>
                      <StatusPill status={app.status} />
                    </div>
                    <span>{app.id} · Amount: {app.amountLabel}</span>
                    <small>Updated {app.updatedAt}</small>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* EXPLAINABLE SCHEME RECOMMENDATIONS */}
          <Card>
            <CardHeader
              title="Recommended Loan Schemes / अनुशंसित योजनाएं"
              subtitle="Self-assessed relevance matches based on your business classification and loan requirement."
              action={<Link className="text-link" to="/applicant/schemes">Browse all 8 schemes</Link>}
            />

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {schemes.slice(0, 2).map((scheme) => (
                <div key={scheme.id} style={{ border: '1px solid #E2E8F0', borderRadius: '12px', padding: '16px', background: '#FFF' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
                    <div>
                      <h3 style={{ margin: 0, fontSize: '15px', color: '#0B192C' }}>{scheme.name}</h3>
                      <p style={{ margin: '4px 0 8px', fontSize: '12px', color: '#64748B' }}>{scheme.purpose}</p>
                    </div>
                    <Badge tone="success">{scheme.matchLabel}</Badge>
                  </div>

                  <div style={{ background: '#F8FAFC', borderRadius: '8px', padding: '10px', fontSize: '11px', color: '#334155' }}>
                    <strong>Why this scheme fits:</strong>
                    <ul style={{ margin: '4px 0 0', paddingLeft: '16px', color: '#64748B' }}>
                      {scheme.reasons.map((r, idx) => (
                        <li key={idx}>{r}</li>
                      ))}
                    </ul>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px' }}>
                    <span style={{ fontSize: '11px', color: '#64748B' }}>Source: {scheme.source}</span>
                    <Link className="btn btn-secondary" to={`/applicant/schemes/${scheme.id}`} style={{ padding: '6px 12px', fontSize: '12px' }}>
                      View Scheme Details <ArrowRight size={14} />
                    </Link>
                  </div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: '14px', fontSize: '10px', color: '#94A3B8', fontStyle: 'italic' }}>
              * Relevance matches are informational signals to aid discovery. They do not constitute a credit score, pre-approval, or sanction guarantee.
            </div>
          </Card>
        </div>

        {/* RIGHT COLUMN: AI ASSISTANT & QUICK METRICS */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {/* SAAKSHI AI ASSISTANT WIDGET */}
          <Card className="assistant-card">
            <div className="assistant-orb">
              <Sparkles size={24} />
            </div>
            <Badge tone="success">AI-Assisted · Scoped Context</Badge>
            <h2>Ask Saakshi about your financing options</h2>
            <p>
              Saakshi can explain eligibility criteria, scheme benefits, and document requirements for your MSME profile.
            </p>
            <Button
              variant="primary"
              full
              onClick={() => navigate('/applicant/assistant')}
            >
              Start Conversation <ArrowRight size={16} />
            </Button>
            <div className="mini-disclaimer">
              AI answers are informational assistance and do not approve or reject loans.
            </div>
          </Card>

          {/* FINANCIAL SNAPSHOT SUMMARY WIDGET */}
          <Card>
            <CardHeader title="Financial Snapshot" subtitle="Declared figures for application building" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12px' }}>
              <div className="row-between" style={{ borderBottom: '1px solid #EDF0F4', paddingBottom: '8px' }}>
                <span style={{ color: '#64748B' }}>Monthly Income:</span>
                <strong className="money" style={{ color: '#0B192C' }}>{financial.monthlyIncome}</strong>
              </div>
              <div className="row-between" style={{ borderBottom: '1px solid #EDF0F4', paddingBottom: '8px' }}>
                <span style={{ color: '#64748B' }}>Monthly Expenses:</span>
                <strong className="money" style={{ color: '#0B192C' }}>{financial.monthlyExpenses}</strong>
              </div>
              <div className="row-between" style={{ borderBottom: '1px solid #EDF0F4', paddingBottom: '8px' }}>
                <span style={{ color: '#64748B' }}>Existing Debt Obligations:</span>
                <strong className="money" style={{ color: '#0B192C' }}>{financial.existingDebt}</strong>
              </div>
              <div className="row-between">
                <span style={{ color: '#059669', fontWeight: '700' }}>Remaining Cash Flow:</span>
                <strong className="money" style={{ color: '#059669', fontSize: '15px' }}>{financial.remainingCashFlow}</strong>
              </div>
            </div>
            <Button
              variant="ghost"
              size="md"
              full
              style={{ marginTop: '14px' }}
              onClick={() => navigate('/applicant/financial')}
            >
              View Full Breakdown <ArrowRight size={14} />
            </Button>
          </Card>

          {/* SIMULATOR QUICK TOOL */}
          <Card style={{ background: '#EFF4FF', border: '1px solid #C7D2FE' }}>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <Calculator size={22} style={{ color: '#0B192C' }} />
              <div>
                <strong style={{ fontSize: '13px', color: '#0B192C' }}>EMI Scenario Simulator</strong>
                <p style={{ margin: '2px 0 0', fontSize: '11px', color: '#64748B' }}>Test monthly installment scenarios for your required tenure.</p>
              </div>
            </div>
            <Button
              variant="secondary"
              size="md"
              full
              style={{ marginTop: '12px' }}
              onClick={() => navigate('/applicant/loan-scenario')}
            >
              Open Simulator <ArrowRight size={14} />
            </Button>
          </Card>
        </div>
      </div>

      {/* NEXT BEST ACTIONS GRID */}
      <Card className="next-card" style={{ marginTop: '20px' }}>
        <CardHeader
          title="Next Best Actions / अगले कदम"
          subtitle="Complete these actions to make your loan applications review-ready."
        />

        <div className="action-list">
          <Link className="action-item" to="/applicant/profile">
            <UserRound size={18} style={{ color: '#059669' }} />
            <div>
              <h4>Complete Profile Classification ✓</h4>
              <p>Basic identity &amp; enterprise details updated</p>
            </div>
          </Link>

          <Link className="action-item" to="/applicant/financial-profile">
            <WalletCards size={18} style={{ color: '#059669' }} />
            <div>
              <h4>Review Financial Profile</h4>
              <p>Confirm turnover, expenses &amp; existing debt</p>
            </div>
          </Link>

          <Link className="action-item" to="/applicant/documents">
            <FileText size={18} style={{ color: '#0B192C' }} />
            <div>
              <h4>Upload Required Documents</h4>
              <p>GST returns &amp; 6-month bank statements</p>
            </div>
          </Link>
        </div>
      </Card>
    </>
  );
}

function StatCard({ icon, label, value, hint }: { icon: React.ReactNode; label: string; value: string; hint: string }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{hint}</small>
    </div>
  );
}
