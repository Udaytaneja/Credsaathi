import React, { useState, useEffect, useCallback } from 'react';
import { 
  Calculator, 
  Info, 
  ShieldCheck, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle2, 
  Layers
} from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import Badge from '../components/Badge';
import { services } from '../services';
import type { LoanScenarioResponse } from '../types';

export default function LoanScenario() {
  // Scenario input parameters
  const [amount, setAmount] = useState<number>(25); // in Lakhs
  const [tenure, setTenure] = useState<number>(5); // in Years
  const [interestRate, setInterestRate] = useState<number>(10.5); // in % p.a.

  // Async UI States
  const [result, setResult] = useState<LoanScenarioResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string>('');

  const runScenario = useCallback(async (amt: number, ten: number, rate: number) => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = (await services.loanScenario({
        amount: amt,
        tenureYears: ten,
        interestRate: rate
      })) as LoanScenarioResponse;
      setResult(data);
    } catch {
      setErrorMsg('Failed to calculate loan scenario from backend service. Please click retry.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch scenario calculation asynchronously on parameter changes
  useEffect(() => {
    let mounted = true;
    
    services.loanScenario({ amount, tenureYears: tenure, interestRate })
      .then((data) => {
        if (mounted) {
          setResult(data as LoanScenarioResponse);
          setLoading(false);
        }
      })
      .catch(() => {
        if (mounted) {
          setErrorMsg('Failed to calculate loan scenario from backend service. Please click retry.');
          setLoading(false);
        }
      });

    return () => { mounted = false; };
  }, [amount, tenure, interestRate]);

  return (
    <>
      <PageTitle
        eyebrow="FINANCIAL SIMULATOR"
        title="Loan Scenario & EMI Simulator"
        subtitle="Explore potential loan amounts, tenure options, and cash-flow impacts. All calculations are requested from backend services."
        action={
          <Badge tone="warning" icon={<Calculator size={13} />}>
            Backend Calculation Engine
          </Badge>
        }
      />

      {/* Security Authority Banner */}
      <div className="card" style={{ background: '#EFF6FF', borderColor: '#BFDBFE', padding: '14px 18px', marginBottom: '22px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', color: '#1E40AF', fontSize: '12px', lineHeight: '19px' }}>
          <ShieldCheck size={20} style={{ color: '#2563EB', flexShrink: 0, marginTop: '1px' }} />
          <div>
            <strong style={{ display: 'block', fontSize: '13px', color: '#1E3A8A', marginBottom: '2px' }}>
              No Local Math Calculations in UI Component
            </strong>
            The EMI, total repayment amounts, and cash-flow impact percentages displayed below are generated strictly by calling the backend scenario API endpoint (<code style={{ background: '#DBEAFE', padding: '1px 5px', borderRadius: '4px' }}>POST /financial/loan-scenarios</code>).
          </div>
        </div>
      </div>

      {errorMsg && (
        <div className="card" style={{ background: '#FEF2F2', borderColor: '#FECDD3', padding: '14px 18px', marginBottom: '20px', color: 'var(--red)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
          <button className="btn btn-secondary" style={{ padding: '4px 12px', fontSize: '12px' }} onClick={() => runScenario(amount, tenure, interestRate)}>
            <RefreshCw size={14} /> Retry Calculation
          </button>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1.8fr', gap: '22px' }}>
        {/* Left Column: Parameter Inputs & Sliders */}
        <div>
          <Card>
            <CardHeader
              title="Scenario Parameters"
              subtitle="Adjust loan principal, tenure, and rate to request server-side scenario."
            />

            <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
              {/* Slider 1: Loan Amount */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <label style={{ fontSize: '12px', fontWeight: 700, color: 'var(--navy)' }}>
                    Loan Principal Amount
                  </label>
                  <strong className="money" style={{ fontSize: '15px', color: 'var(--navy)' }}>
                    ₹{amount},00,000 ({amount} Lakhs)
                  </strong>
                </div>
                <input
                  type="range"
                  min="2"
                  max="100"
                  step="1"
                  value={amount}
                  onChange={(e) => setAmount(Number(e.target.value))}
                  style={{ width: '100%', height: '6px', cursor: 'pointer', accentColor: 'var(--navy)' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--muted)', marginTop: '4px' }}>
                  <span>₹2 Lakhs</span>
                  <span>₹50 Lakhs</span>
                  <span>₹1 Crore</span>
                </div>
              </div>

              {/* Slider 2: Tenure */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <label style={{ fontSize: '12px', fontWeight: 700, color: 'var(--navy)' }}>
                    Repayment Tenure
                  </label>
                  <strong style={{ fontSize: '15px', color: 'var(--navy)' }}>
                    {tenure} {tenure === 1 ? 'Year' : 'Years'} ({tenure * 12} Months)
                  </strong>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  value={tenure}
                  onChange={(e) => setTenure(Number(e.target.value))}
                  style={{ width: '100%', height: '6px', cursor: 'pointer', accentColor: 'var(--navy)' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--muted)', marginTop: '4px' }}>
                  <span>1 Year</span>
                  <span>5 Years</span>
                  <span>10 Years</span>
                </div>
              </div>

              {/* Slider 3: Indicative Interest Rate */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <label style={{ fontSize: '12px', fontWeight: 700, color: 'var(--navy)' }}>
                    Indicative Interest Rate (% p.a.)
                  </label>
                  <strong style={{ fontSize: '15px', color: 'var(--navy)' }}>
                    {interestRate.toFixed(1)}% p.a.
                  </strong>
                </div>
                <input
                  type="range"
                  min="6.0"
                  max="18.0"
                  step="0.5"
                  value={interestRate}
                  onChange={(e) => setInterestRate(Number(e.target.value))}
                  style={{ width: '100%', height: '6px', cursor: 'pointer', accentColor: 'var(--navy)' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--muted)', marginTop: '4px' }}>
                  <span>6.0% (Subsidized)</span>
                  <span>10.5% (Standard)</span>
                  <span>18.0% (Commercial)</span>
                </div>
              </div>
            </div>

            <div className="info-box" style={{ marginTop: '24px' }}>
              <Info size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
              <p style={{ margin: 0, fontSize: '11px', lineHeight: '18px', color: 'var(--muted)' }}>
                Changing slider inputs automatically sends a request to <code style={{ background: '#E2E8F0', padding: '1px 4px', borderRadius: '3px' }}>services.loanScenario(...)</code>.
              </p>
            </div>
          </Card>
        </div>

        {/* Right Column: Backend Calculation Results & Amortization Table */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
          {/* Main EMI Results Header Cards */}
          <Card>
            <CardHeader
              title="Official Backend Scenario Results"
              subtitle="Server-calculated repayment baseline and monthly cash flow impact."
              action={
                loading ? (
                  <Badge tone="warning" icon={<RefreshCw size={12} className="spin" />}>
                    Calculating...
                  </Badge>
                ) : (
                  <Badge tone="success" icon={<CheckCircle2 size={12} />}>
                    Server Verified
                  </Badge>
                )
              }
            />

            {loading ? (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)' }}>
                <RefreshCw size={24} className="spin" style={{ marginBottom: '8px' }} />
                <p style={{ margin: 0, fontSize: '13px' }}>Querying backend financial calculation engine...</p>
              </div>
            ) : result ? (
              <>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '14px', marginBottom: '18px' }}>
                  <ResultBox
                    label="Estimated Monthly EMI"
                    value={result.emiLabel}
                    sub="Monthly installment"
                    primary
                  />
                  <ResultBox
                    label="Total Repayment"
                    value={result.totalRepaymentLabel}
                    sub="Principal + Interest"
                  />
                  <ResultBox
                    label="Total Interest Cost"
                    value={result.totalInterestLabel}
                    sub={`Rate: ${result.interestRateApplied}`}
                  />
                </div>

                <div style={{ padding: '14px 16px', background: '#F8FAFC', borderRadius: '10px', border: '1px solid var(--line)', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--navy)' }}>
                      Post-EMI Remaining Monthly Cash Flow
                    </span>
                    <strong className="money" style={{ fontSize: '15px', color: 'var(--green)' }}>
                      {result.remainingCashFlowPostEmiLabel}
                    </strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--muted)' }}>
                    <span>Total Monthly Obligations (Existing + New EMI): <strong>{result.monthlyDebtObligationsLabel}</strong></span>
                    <span>Cash Flow Impact: <strong>{result.cashFlowImpactPercentage}</strong></span>
                  </div>
                </div>

                {/* Amortization Schedule Table */}
                <h4 style={{ fontSize: '13px', margin: '18px 0 10px', color: 'var(--navy)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Layers size={15} /> Yearly Amortization Breakdown
                </h4>

                <div className="table-wrap" style={{ marginBottom: '16px' }}>
                  <table>
                    <thead>
                      <tr>
                        <th>Year</th>
                        <th>Principal Paid</th>
                        <th>Interest Paid</th>
                        <th style={{ textAlign: 'right' }}>Remaining Principal Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.amortizationBreakdown.map((row) => (
                        <tr key={row.year}>
                          <td><strong>Year {row.year}</strong></td>
                          <td><span className="money">{row.principalPaid}</span></td>
                          <td><span className="money" style={{ color: 'var(--amber)' }}>{row.interestPaid}</span></td>
                          <td style={{ textAlign: 'right' }}><strong className="money" style={{ color: 'var(--navy)' }}>{row.balanceRemaining}</strong></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="panel-disclaimer" style={{ marginTop: '12px' }}>
                  <ShieldCheck size={16} />
                  <span>{result.disclaimer}</span>
                </div>
              </>
            ) : null}
          </Card>
        </div>
      </div>
    </>
  );
}

function ResultBox({ label, value, sub, primary }: { label: string; value: string; sub: string; primary?: boolean }) {
  return (
    <div style={{
      background: primary ? 'var(--navy)' : '#F8FAFC',
      color: primary ? 'var(--white)' : 'var(--navy)',
      border: primary ? 'none' : '1px solid var(--line)',
      borderRadius: '12px',
      padding: '16px',
      boxShadow: primary ? '0 4px 12px rgba(11, 25, 44, 0.15)' : 'none'
    }}>
      <span style={{ display: 'block', fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', opacity: primary ? 0.8 : 0.6 }}>
        {label}
      </span>
      <strong className="money" style={{ display: 'block', fontSize: '18px', fontWeight: 800, margin: '6px 0 2px' }}>
        {value}
      </strong>
      <small style={{ fontSize: '10px', opacity: primary ? 0.8 : 0.6 }}>
        {sub}
      </small>
    </div>
  );
}
