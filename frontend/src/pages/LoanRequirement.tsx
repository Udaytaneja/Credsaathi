import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, ArrowRight, AlertTriangle, Save, RefreshCw, Calculator } from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import { Button } from '../components/Button';
import { Field } from '../components/Field';
import Badge from '../components/Badge';

const purposes = [
  { id: 'expansion', title: 'Business Expansion', hindi: 'व्यवसाय विस्तार', desc: 'Scale capacity or open new outlet' },
  { id: 'working_cap', title: 'Working Capital', hindi: 'कार्यशील पूंजी', desc: 'Day-to-day inventory & raw materials' },
  { id: 'equipment', title: 'Plant & Machinery', hindi: 'संयंत्र और मशीनरी', desc: 'Purchase tools or equipment' },
  { id: 'agri', title: 'Agri Infrastructure', hindi: 'कृषि अवसंरचना', desc: 'Storage, solar or farm equipment' },
  { id: 'refinance', title: 'Loan Refinancing', hindi: 'ऋण पुनर्वित्त', desc: 'Consolidate or reduce interest cost' },
  { id: 'micro', title: 'Micro-Credit Facility', hindi: 'सूक्ष्म ऋण', desc: 'Small ticket business financing' },
];

const collateralTypes = [
  { id: 'cgtmse', label: 'CGTMSE Collateral-Free Guarantee', hindi: 'CGTMSE बिना बंधक गारंटी' },
  { id: 'hypothecation', label: 'Stock & Machinery Hypothecation', hindi: 'स्टॉक हाइपोथेकेशन' },
  { id: 'mortgage', label: 'Land or Commercial Property Mortgage', hindi: 'संपत्ति बंधक' },
  { id: 'none', label: 'Clean / Unsecured Credit', hindi: 'अनसिक्योर्ड क्रेडिट' },
];

export default function LoanRequirement() {
  const navigate = useNavigate();

  // Form State
  const [selectedPurpose, setSelectedPurpose] = useState('expansion');
  const [amount, setAmount] = useState('25,00,000');
  const [tenureYears, setTenureYears] = useState('5');
  const [collateral, setCollateral] = useState('cgtmse');
  const [timeline, setTimeline] = useState('1-3');

  // UX States
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!amount.trim()) {
      setErrorMsg('Please specify the required loan amount.');
      return;
    }

    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setSuccessMsg('Loan requirements saved. Moving to Financial Profile.');
      setTimeout(() => {
        navigate('/applicant/financial-profile');
      }, 1000);
    } catch {
      setErrorMsg('Failed to save requirements. Please try again.');
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
        <div className="step active">
          <span>2</span>
          <small>Loan Requirement</small>
        </div>
        <div className="step">
          <span>3</span>
          <small>Financial Profile</small>
        </div>
        <div className="step">
          <span>4</span>
          <small>Scheme Discovery</small>
        </div>
      </div>

      <PageTitle
        eyebrow="PROGRESSIVE ONBOARDING · STEP 2 OF 3"
        title="Loan Requirement Specification"
        subtitle="Specify your loan purpose, quantum, and tenure to identify matching government subsidy schemes."
        action={
          <Badge tone="success" icon={<CheckCircle2 size={14} />}>
            Step 2 · 50% Complete
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
        {/* PURPOSE SELECTION GRID */}
        <Card className="form-card">
          <CardHeader
            title="1. Primary Financing Purpose / ऋण का उद्देश्य"
            subtitle="Select the primary purpose of your funding request."
          />

          <div className="choice-grid">
            {purposes.map((p) => (
              <button
                key={p.id}
                type="button"
                className={`choice ${selectedPurpose === p.id ? 'selected' : ''}`}
                onClick={() => setSelectedPurpose(p.id)}
              >
                <span className="choice-check">
                  {selectedPurpose === p.id ? <CheckCircle2 size={18} /> : null}
                </span>
                <strong style={{ display: 'block', fontSize: '13px', color: '#0B192C' }}>{p.title}</strong>
                <span style={{ display: 'block', fontSize: '11px', color: '#64748B', marginTop: '2px' }}>{p.hindi}</span>
                <small style={{ display: 'block', fontSize: '10px', color: '#94A3B8', marginTop: '4px' }}>{p.desc}</small>
              </button>
            ))}
          </div>

          <CardHeader
            title="2. Quantum, Tenure &amp; Collateral / ऋण राशि और अवधि"
            subtitle="State your required amount in INR tabular numbers."
          />

          <div className="form-grid">
            <Field
              label="Required Loan Amount (₹ INR)"
              affix="₹"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="25,00,000"
              required
            />

            <Field
              label="Preferred Tenure (Years)"
              type="number"
              value={tenureYears}
              onChange={(e) => setTenureYears(e.target.value)}
              placeholder="5"
              hint="Typical MSME loan tenure: 1 to 7 years"
              required
            />

            <Field
              label="Expected Disbursement Timeframe"
              fieldType="select"
              value={timeline}
              onChange={(e) => setTimeline(e.target.value)}
              options={[
                { value: 'asap', label: 'As soon as possible (Immediate)' },
                { value: '1-3', label: 'Within 1–3 Months' },
                { value: '3-6', label: 'Within 3–6 Months' },
              ]}
            />

            <Field
              label="Security / Collateral Preference"
              fieldType="select"
              value={collateral}
              onChange={(e) => setCollateral(e.target.value)}
              options={collateralTypes.map((c) => ({ value: c.id, label: c.label }))}
            />
          </div>

          {/* SIMULATOR QUICK ENTRY */}
          <div className="info-box" style={{ marginTop: '24px' }}>
            <Calculator size={20} style={{ color: '#059669', flexShrink: 0 }} />
            <div>
              <strong>Interactive EMI Simulator Available</strong>
              <p>
                Want to test different interest rate scenarios and monthly EMI impact? Try out our <a className="text-link" onClick={() => navigate('/applicant/loan-scenario')}>EMI Scenario Simulator</a>.
              </p>
            </div>
          </div>

          {/* FORM ACTIONS */}
          <div className="form-actions">
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/applicant/profile')}
            >
              Back to Profile
            </Button>

            <Button type="submit" variant="primary" loading={loading}>
              <Save size={16} /> Save &amp; Continue <ArrowRight size={17} />
            </Button>
          </div>
        </Card>
      </form>
    </>
  );
}
