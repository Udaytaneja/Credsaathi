import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, ArrowRight, ShieldCheck, AlertTriangle, Save, RefreshCw, FileText } from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import { Button } from '../components/Button';
import { Field } from '../components/Field';
import Badge from '../components/Badge';
import { financial } from '../services/mock/data';

export default function FinancialProfile() {
  const navigate = useNavigate();

  // Form State
  const [turnover, setTurnover] = useState('48.50');
  const [monthlyIncome, setMonthlyIncome] = useState(financial.monthlyIncome.replace('₹', '').replace(',', ''));
  const [monthlyExpenses, setMonthlyExpenses] = useState(financial.monthlyExpenses.replace('₹', '').replace(',', ''));
  const [existingDebt, setExistingDebt] = useState(financial.existingDebt.replace('₹', '').replace(',', ''));
  const [repaymentTrack, setRepaymentTrack] = useState('regular');

  // Document Readiness Checks
  const [docGst, setDocGst] = useState(true);
  const [docBank, setDocBank] = useState(true);
  const [docItr, setDocItr] = useState(true);
  const [docUdyam, setDocUdyam] = useState(true);

  // UX States
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!monthlyIncome.trim() || !monthlyExpenses.trim()) {
      setErrorMsg('Please complete monthly income and expense fields.');
      return;
    }

    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      await new Promise((resolve) => setTimeout(resolve, 600));
      setSuccessMsg('Financial profile saved successfully! Proceeding to Scheme Discovery.');
      setTimeout(() => {
        navigate('/applicant/schemes');
      }, 1000);
    } catch {
      setErrorMsg('Failed to save financial profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* STEP PROGRESS BAR */}
      <div className="stepper" style={{ marginBottom: '20px' }}>
        <div className="step done">
          <span>✓</span>
          <small>Basic Profile</small>
        </div>
        <div className="step done">
          <span>✓</span>
          <small>Loan Requirement</small>
        </div>
        <div className="step active">
          <span>3</span>
          <small>Financial Profile</small>
        </div>
        <div className="step">
          <span>4</span>
          <small>Scheme Discovery</small>
        </div>
      </div>

      <PageTitle
        eyebrow="PROGRESSIVE ONBOARDING · STEP 3 OF 3"
        title="Financial Profile &amp; Credit Readiness"
        subtitle="Declare your revenue, net profit, and existing commitments for financial verification."
        action={
          <Badge tone="success" icon={<CheckCircle2 size={14} />}>
            Step 3 · 75% Complete
          </Badge>
        }
      />

      {/* FEEDBACK BANNERS */}
      {successMsg && (
        <div style={{ background: '#E7FAF2', border: '1px solid #BFEAD7', color: '#047857', padding: '12px 16px', borderRadius: '8px', marginBottom: '16px', fontWeight: '600', fontSize: '13px' }}>
          <CheckCircle2 size={18} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'text-bottom' }} />
          {successMsg}
        </div>
      )}

      {errorMsg && (
        <div className="form-error" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <AlertTriangle size={16} style={{ display: 'inline', marginRight: '8px' }} />
            {errorMsg}
          </div>
          <Button variant="ghost" size="md" onClick={() => setErrorMsg('')}>
            <RefreshCw size={14} /> Retry
          </Button>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="two-col">
          <Card className="form-card">
            <CardHeader
              title="Revenue &amp; Monthly Overview"
              subtitle="All monetary fields enforce tabular lining numerals (font-variant-numeric: tabular-nums)."
            />

            <div className="form-grid">
              <Field
                label="Annual Turnover / Revenue (₹ Lakhs)"
                affix="₹"
                value={turnover}
                onChange={(e) => setTurnover(e.target.value)}
                placeholder="48.50"
                hint="FY 2023–24 Total Revenue"
                required
              />

              <Field
                label="Average Net Monthly Profit / Income"
                affix="₹"
                value={monthlyIncome}
                onChange={(e) => setMonthlyIncome(e.target.value)}
                placeholder="85,000"
                required
              />

              <Field
                label="Monthly Business &amp; Household Expenses"
                affix="₹"
                value={monthlyExpenses}
                onChange={(e) => setMonthlyExpenses(e.target.value)}
                placeholder="32,000"
                required
              />

              <Field
                label="Existing Debt &amp; Monthly EMI Obligations"
                affix="₹"
                value={existingDebt}
                onChange={(e) => setExistingDebt(e.target.value)}
                placeholder="15,000"
                required
              />

              <Field
                label="Prior Debt Repayment Track-Record"
                fieldType="select"
                value={repaymentTrack}
                onChange={(e) => setRepaymentTrack(e.target.value)}
                options={[
                  { value: 'regular', label: 'Regular / No Delays (Clean Credit History)' },
                  { value: 'minor_delay', label: 'Occasional Minor Delays (< 30 days)' },
                  { value: 'no_prior_debt', label: 'First-time Borrower (No prior loans)' },
                ]}
              />
            </div>

            <div className="info-box" style={{ marginTop: '20px' }}>
              <ShieldCheck size={18} style={{ color: '#059669', flexShrink: 0 }} />
              <div>
                <strong>Backend Calculation Authority</strong>
                <p>
                  Official financial calculations, debt-service coverage ratio (DSCR), and cash flow surplus metrics are owned by backend services.
                </p>
              </div>
            </div>

            <div className="form-actions">
              <Button
                type="button"
                variant="secondary"
                onClick={() => navigate('/applicant/loan-requirement')}
              >
                Back to Loan Requirement
              </Button>

              <Button type="submit" variant="primary" loading={loading}>
                <Save size={16} /> Save &amp; Explore Schemes <ArrowRight size={17} />
              </Button>
            </div>
          </Card>

          {/* DOCUMENT READINESS CHECKLIST */}
          <aside>
            <Card>
              <CardHeader
                title="Document Readiness"
                subtitle="Check off documents available in your vault"
              />

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <label className="checkbox" style={{ padding: '8px', background: docGst ? '#EDF8F4' : '#FFF', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                  <input type="checkbox" checked={docGst} onChange={(e) => setDocGst(e.target.checked)} />
                  <div>
                    <strong style={{ display: 'block', fontSize: '12px', color: '#0B192C' }}>GST Returns (Last 12 Months)</strong>
                    <span style={{ fontSize: '10px', color: '#64748B' }}>Used for revenue verification</span>
                  </div>
                </label>

                <label className="checkbox" style={{ padding: '8px', background: docBank ? '#EDF8F4' : '#FFF', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                  <input type="checkbox" checked={docBank} onChange={(e) => setDocBank(e.target.checked)} />
                  <div>
                    <strong style={{ display: 'block', fontSize: '12px', color: '#0B192C' }}>Bank Account Statements (6 Months)</strong>
                    <span style={{ fontSize: '10px', color: '#64748B' }}>Used for cash flow evaluation</span>
                  </div>
                </label>

                <label className="checkbox" style={{ padding: '8px', background: docItr ? '#EDF8F4' : '#FFF', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                  <input type="checkbox" checked={docItr} onChange={(e) => setDocItr(e.target.checked)} />
                  <div>
                    <strong style={{ display: 'block', fontSize: '12px', color: '#0B192C' }}>Income Tax Returns (ITR - FY23/24)</strong>
                    <span style={{ fontSize: '10px', color: '#64748B' }}>Used for financial underwriting</span>
                  </div>
                </label>

                <label className="checkbox" style={{ padding: '8px', background: docUdyam ? '#EDF8F4' : '#FFF', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                  <input type="checkbox" checked={docUdyam} onChange={(e) => setDocUdyam(e.target.checked)} />
                  <div>
                    <strong style={{ display: 'block', fontSize: '12px', color: '#0B192C' }}>Udyam MSME Certificate</strong>
                    <span style={{ fontSize: '10px', color: '#64748B' }}>Unlocks MSME subsidy eligibility</span>
                  </div>
                </label>
              </div>

              <div style={{ marginTop: '16px', paddingTop: '14px', borderTop: '1px solid #E2E8F0' }}>
                <Button
                  type="button"
                  variant="secondary"
                  full
                  onClick={() => navigate('/applicant/documents')}
                >
                  <FileText size={16} /> Manage Document Vault
                </Button>
              </div>
            </Card>
          </aside>
        </div>
      </form>
    </>
  );
}
