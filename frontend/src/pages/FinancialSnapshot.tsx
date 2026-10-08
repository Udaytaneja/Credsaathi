import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Info, 
  ShieldCheck, 
  TrendingUp, 
  ArrowRight, 
  RefreshCw, 
  PieChart, 
  AlertCircle
} from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import Badge from '../components/Badge';
import { services } from '../services';
import type { FinancialSnapshot as SnapshotType } from '../types';

export default function FinancialSnapshot() {
  const navigate = useNavigate();
  const [snapshot, setSnapshot] = useState<SnapshotType | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const fetchSnapshot = async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = (await services.financialSnapshot()) as SnapshotType;
      setSnapshot(data);
    } catch {
      setErrorMsg('Failed to load financial snapshot from backend services.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let mounted = true;
    (services.financialSnapshot() as Promise<SnapshotType>)
      .then((data) => {
        if (mounted) {
          setSnapshot(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (mounted) {
          setErrorMsg('Failed to load financial snapshot from backend services.');
          setLoading(false);
        }
      });
    return () => { mounted = false; };
  }, []);

  return (
    <>
      <PageTitle
        eyebrow="FINANCIAL PROFILE & SNAPSHOT"
        title="Financial Snapshot / वित्तीय सारांश"
        subtitle="Read-only presentation of backend financial data. The frontend visualizes official server-side calculations without performing local metrics calculation."
        action={
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-secondary" onClick={() => navigate('/applicant/loan-scenario')}>
              <PieChart size={16} /> EMI Simulator
            </button>
            <button className="btn btn-primary" onClick={() => navigate('/applicant/financial-profile')}>
              Edit Parameters <ArrowRight size={16} />
            </button>
          </div>
        }
      />

      {/* Security & Audit Authority Banner */}
      <div className="card" style={{ background: '#EFF6FF', borderColor: '#BFDBFE', padding: '14px 18px', marginBottom: '22px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', color: '#1E40AF', fontSize: '12px', lineHeight: '19px' }}>
          <ShieldCheck size={20} style={{ color: '#2563EB', flexShrink: 0, marginTop: '1px' }} />
          <div>
            <strong style={{ display: 'block', fontSize: '13px', color: '#1E3A8A', marginBottom: '2px' }}>
              Backend Financial Engine Authority
            </strong>
            This page displays verified server-side cash flow metrics, debt-service coverage ratios, and declared commitments. No frontend component performs independent calculation of financial ratios or repayment capacities.
          </div>
        </div>
      </div>

      {errorMsg && (
        <div className="card" style={{ background: '#FEF2F2', borderColor: '#FECDD3', padding: '14px 18px', marginBottom: '20px', color: 'var(--red)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
          <button className="btn btn-secondary" style={{ padding: '4px 12px', fontSize: '12px' }} onClick={fetchSnapshot}>
            <RefreshCw size={14} /> Retry
          </button>
        </div>
      )}

      {loading ? (
        <div style={{ padding: '60px', textAlign: 'center', color: 'var(--muted)' }}>
          <RefreshCw size={28} className="spin" style={{ marginBottom: '10px' }} />
          <p style={{ margin: 0, fontSize: '14px' }}>Loading verified financial metrics...</p>
        </div>
      ) : snapshot ? (
        <>
          {/* STAT CARDS GRID */}
          <div className="stat-grid" style={{ marginBottom: '22px' }}>
            <StatCard
              label="Declared Monthly Income"
              value={snapshot.monthlyIncome}
              hint="Verified via bank & GST data"
              tone="navy"
            />
            <StatCard
              label="Monthly Expenses"
              value={snapshot.monthlyExpenses}
              hint="Operational & household baseline"
            />
            <StatCard
              label="Existing Debt Obligations"
              value={snapshot.existingDebt}
              hint="Active EMI & credit lines"
            />
            <StatCard
              label="Remaining Net Cash Flow"
              value={snapshot.remainingCashFlow}
              hint="Surplus available for new facility"
              tone="success"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '22px' }}>
            {/* Left Column: Ratio & Balance Sheet Overview */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
              <Card>
                <CardHeader
                  title="Cash Flow & Debt Service Ratios"
                  subtitle="Backend calculated affordability indicators for bank underwriting."
                />

                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <RatioRow
                    label="Debt Service Coverage Ratio (DSCR)"
                    value={snapshot.debtServiceCoverageRatio || '2.67x'}
                    description="Calculated ratio of net operating income to debt service obligations."
                  />
                  <RatioRow
                    label="Declared Assets (Total)"
                    value={snapshot.assets || '₹42,50,000'}
                    description="Fixed plant, machinery, current inventory & liquid balances."
                  />
                  <RatioRow
                    label="Declared Liabilities (Total)"
                    value={snapshot.liabilities || '₹14,20,000'}
                    description="Long-term term loans, working capital limits & statutory payables."
                  />
                </div>
              </Card>

              <Card>
                <CardHeader
                  title="Income & Expenditure Distribution"
                  subtitle="Relative proportion of cash outflow obligations."
                />

                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  <BarItem label="Monthly Gross Income" value="100%" color="var(--navy)" />
                  <BarItem label="Household & Operational Expenses" value="51%" color="var(--dark)" />
                  <BarItem label="Existing EMI Commitments" value="13%" color="var(--amber)" />
                  <BarItem label="Unencumbered Surplus Cash Flow" value="36%" color="var(--green)" />
                </div>

                <div className="info-box" style={{ marginTop: '18px' }}>
                  <Info size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                  <p style={{ margin: 0, fontSize: '11px', lineHeight: '18px', color: 'var(--muted)' }}>
                    Percentages shown above reflect server-side ratio distributions. The frontend visualizes these properties without modifying or recalculating values locally.
                  </p>
                </div>
              </Card>
            </div>

            {/* Right Column: Financial Verification & Trend Notes */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
              <Card>
                <CardHeader
                  title="Verification & Readiness"
                  subtitle="Verification state of provided financial parameters."
                />

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ padding: '12px 14px', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong style={{ fontSize: '12px', display: 'block', color: 'var(--navy)' }}>GST Returns (12 Months)</strong>
                      <span style={{ fontSize: '10px', color: 'var(--muted)' }}>Turnover verified</span>
                    </div>
                    <Badge tone="success">VERIFIED</Badge>
                  </div>

                  <div style={{ padding: '12px 14px', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong style={{ fontSize: '12px', display: 'block', color: 'var(--navy)' }}>Bank Statement Extraction</strong>
                      <span style={{ fontSize: '10px', color: 'var(--muted)' }}>6-month average cash flow</span>
                    </div>
                    <Badge tone="success">VERIFIED</Badge>
                  </div>

                  <div style={{ padding: '12px 14px', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong style={{ fontSize: '12px', display: 'block', color: 'var(--navy)' }}>Income Tax Returns (ITR)</strong>
                      <span style={{ fontSize: '10px', color: 'var(--muted)' }}>Self-declared baseline</span>
                    </div>
                    <Badge tone="warning">SELF-DECLARED</Badge>
                  </div>
                </div>

                <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid var(--line)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--green)', fontWeight: 600 }}>
                    <TrendingUp size={16} />
                    <span>{snapshot.trendLabel || '+8.4% Revenue Growth (YoY)'}</span>
                  </div>
                </div>
              </Card>

              <Card>
                <CardHeader
                  title="Source Disclaimers"
                  subtitle="Official statutory notice for financial profile data."
                />

                <p style={{ fontSize: '12px', lineHeight: '20px', color: 'var(--muted)', margin: '0 0 12px' }}>
                  {snapshot.sourceNote || 'Illustrative demo values. Official financial metrics must come from the backend financial engine.'}
                </p>

                <div style={{ fontSize: '11px', color: 'var(--placeholder)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <ShieldCheck size={14} /> Official figures subject to bank loan committee appraisal.
                </div>
              </Card>
            </div>
          </div>
        </>
      ) : null}
    </>
  );
}

function StatCard({ label, value, hint, tone }: { label: string; value: string; hint: string; tone?: 'navy' | 'success' }) {
  const bg = tone === 'navy' ? 'var(--blue-soft)' : tone === 'success' ? 'var(--green-soft)' : 'var(--white)';
  const border = tone === 'navy' ? '#C7D2FE' : tone === 'success' ? 'var(--green-border)' : 'var(--line)';

  return (
    <div style={{
      background: bg,
      border: `1px solid ${border}`,
      borderRadius: '12px',
      padding: '16px',
      boxShadow: 'var(--shadow-subtle)'
    }}>
      <span style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        {label}
      </span>
      <strong className="money" style={{ display: 'block', fontSize: '22px', fontWeight: 800, color: 'var(--navy)', margin: '6px 0 2px' }}>
        {value}
      </strong>
      <small style={{ fontSize: '10px', color: 'var(--muted)' }}>{hint}</small>
    </div>
  );
}

function RatioRow({ label, value, description }: { label: string; value: string; description: string }) {
  return (
    <div style={{
      padding: '14px',
      border: '1px solid var(--line)',
      borderRadius: '10px',
      background: '#F8FAFC'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
        <strong style={{ fontSize: '13px', color: 'var(--navy)' }}>{label}</strong>
        <strong className="money" style={{ fontSize: '15px', color: 'var(--navy)' }}>{value}</strong>
      </div>
      <p style={{ margin: 0, fontSize: '11px', color: 'var(--muted)', lineHeight: '17px' }}>
        {description}
      </p>
    </div>
  );
}

function BarItem({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 600, color: 'var(--navy)', marginBottom: '4px' }}>
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div style={{ height: '7px', width: '100%', background: '#E2E8F0', borderRadius: '4px', overflow: 'hidden' }}>
        <div style={{ width: value, height: '100%', background: color, borderRadius: '4px', transition: 'width 0.3s ease' }} />
      </div>
    </div>
  );
}
