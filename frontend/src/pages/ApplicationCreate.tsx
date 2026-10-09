import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, FileText, Lock, AlertTriangle, Building2, RefreshCw } from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import { Button } from '../components/Button';
import { Field } from '../components/Field';
import Badge from '../components/Badge';

const steps = [
  '1. Facility & Target Lender',
  '2. Loan Sizing & Terms',
  '3. Enterprise Context',
  '4. Review & Consent',
];

const bankOptions = [
  { value: 'sbi', label: 'State Bank of India (SBI)' },
  { value: 'pnb', label: 'Punjab National Bank (PNB)' },
  { value: 'hdfc', label: 'HDFC Bank MSME Division' },
  { value: 'sidbi', label: 'SIDBI Direct Credit' },
  { value: 'union', label: 'Union Bank of India' },
];

const schemeOptions = [
  { value: 'cgtmse', label: 'CGTMSE Working Capital Facility' },
  { value: 'pmegp', label: 'PMEGP Subsidy Scheme' },
  { value: 'mudra', label: 'MUDRA Tarun Business Loan' },
  { value: 'agri', label: 'Agri Infrastructure Credit' },
];

export default function ApplicationCreate() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);

  // Form State
  const [scheme, setScheme] = useState('cgtmse');
  const [targetBank, setTargetBank] = useState('sbi');
  const [facilityType, setFacilityType] = useState('Cash Credit / Working Capital Limit');
  const [amount, setAmount] = useState('25,00,000');
  const [tenureYears, setTenureYears] = useState('5');
  const [collateral, setCollateral] = useState('CGTMSE Collateral-Free Guarantee');
  const [businessName, setBusinessName] = useState('Sharma Agro Tech Solutions');
  const [udyamNo, setUdyamNo] = useState('UDYAM-HP-01-0012345');
  const [turnover, setTurnover] = useState('48.50');
  const [projectDesc, setProjectDesc] = useState('Procurement of automated food processing equipment and expansion of raw material inventory storage.');
  const [agreeConsent, setAgreeConsent] = useState(false);

  // UX & Error States
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleNextStep = () => {
    setErrorMsg('');
    if (currentStep === 0 && (!scheme || !targetBank)) {
      setErrorMsg('Please select a target scheme and bank partner.');
      return;
    }
    if (currentStep === 1 && !amount.trim()) {
      setErrorMsg('Please enter the required loan amount.');
      return;
    }
    if (currentStep === 2 && !businessName.trim()) {
      setErrorMsg('Please enter your business name.');
      return;
    }
    setCurrentStep((prev) => prev + 1);
  };

  const handleFinalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agreeConsent) {
      setErrorMsg('You must authorize CredSaathi data processing consent to submit your application packet.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    try {
      // Simulate API application submission
      await new Promise((resolve) => setTimeout(resolve, 800));
      const generatedId = `CS-2026-00${Math.floor(10 + Math.random() * 89)}`;
      navigate(`/applicant/applications/${generatedId}`);
    } catch {
      setErrorMsg('Failed to submit application. Please click Retry.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Link className="back-link" to="/applicant/applications" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '16px', color: '#64748B', fontWeight: '700', fontSize: '12px' }}>
        <ArrowLeft size={16} /> Back to Applications
      </Link>

      <PageTitle
        eyebrow={`GUIDED APPLICATION PACKET · STEP ${currentStep + 1} OF 4`}
        title="New Loan Application"
        subtitle="Progressive disclosure keeps the application structured. Your packet will be prepared for the selected lender."
        action={
          <Badge tone="navy" icon={<FileText size={14} />}>
            Draft State · Auto-Saved
          </Badge>
        }
      />

      {/* STEP PROGRESS BAR */}
      <div className="stepper" style={{ marginBottom: '20px' }}>
        {steps.map((label, idx) => (
          <div key={label} className={`step ${idx === currentStep ? 'active' : ''} ${idx < currentStep ? 'done' : ''}`}>
            <span>{idx < currentStep ? '✓' : idx + 1}</span>
            <small>{label}</small>
          </div>
        ))}
      </div>

      {/* ERROR FEEDBACK BANNER */}
      {errorMsg && (
        <div className="form-error" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <AlertTriangle size={16} style={{ display: 'inline', marginRight: '6px' }} />
            {errorMsg}
          </div>
          <Button variant="ghost" size="md" onClick={() => setErrorMsg('')}>
            <RefreshCw size={14} /> Clear Error
          </Button>
        </div>
      )}

      <Card className="form-card">
        {/* SECTION 1: FACILITY & TARGET LENDER PREFERENCE */}
        {currentStep === 0 && (
          <div>
            <CardHeader
              title="1. Facility &amp; Target Lender Preference / बैंक और योजना चयन"
              subtitle="Select the loan scheme and preferred lending institution."
            />

            <div className="form-grid">
              <Field
                label="Target Loan Scheme"
                fieldType="select"
                value={scheme}
                onChange={(e) => setScheme(e.target.value)}
                options={schemeOptions}
                required
              />

              <Field
                label="Target Lending Institution / Bank"
                fieldType="select"
                value={targetBank}
                onChange={(e) => setTargetBank(e.target.value)}
                options={bankOptions}
                required
              />

              <Field
                label="Facility Type"
                value={facilityType}
                onChange={(e) => setFacilityType(e.target.value)}
                placeholder="Cash Credit / Term Loan / Overdraft"
                required
              />

              <div className="info-box" style={{ marginTop: 0 }}>
                <Building2 size={20} style={{ color: '#059669', flexShrink: 0 }} />
                <div>
                  <strong>Target Institution Routing</strong>
                  <p>Your application packet will be formatted according to the selected lender's MSME submission criteria.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SECTION 2: LOAN SIZING & TERMS */}
        {currentStep === 1 && (
          <div>
            <CardHeader
              title="2. Loan Sizing &amp; Terms / आवश्यक राशि और अवधि"
              subtitle="Declare the requested credit quantum in tabular lining numbers."
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
                label="Proposed Tenure (Years)"
                type="number"
                value={tenureYears}
                onChange={(e) => setTenureYears(e.target.value)}
                placeholder="5"
                required
              />

              <Field
                label="Security / Primary Collateral"
                value={collateral}
                onChange={(e) => setCollateral(e.target.value)}
                placeholder="CGTMSE Collateral-Free Guarantee"
              />
            </div>
          </div>
        )}

        {/* SECTION 3: ENTERPRISE OPERATIONAL CONTEXT */}
        {currentStep === 2 && (
          <div>
            <CardHeader
              title="3. Enterprise Context &amp; Project Summary / व्यावसायिक विवरण"
              subtitle="Provide operational context and project utilization plan."
            />

            <div className="form-grid">
              <Field
                label="Business / Enterprise Name"
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                required
              />

              <Field
                label="Udyam Registration Number"
                value={udyamNo}
                onChange={(e) => setUdyamNo(e.target.value)}
              />

              <Field
                label="Annual Turnover (₹ Lakhs)"
                affix="₹"
                value={turnover}
                onChange={(e) => setTurnover(e.target.value)}
              />
            </div>

            <div style={{ marginTop: '16px' }}>
              <Field
                label="Project Description / Fund Utilization Plan"
                fieldType="textarea"
                value={projectDesc}
                onChange={(e) => setProjectDesc(e.target.value)}
                placeholder="Describe how the loan funds will be utilized in your business operations…"
              />
            </div>
          </div>
        )}

        {/* SECTION 4: REVIEW & STATUTORY CONSENT */}
        {currentStep === 3 && (
          <div>
            <CardHeader
              title="4. Review Application &amp; Authorize Consent / समीक्षा और सहमति"
              subtitle="Review your structured application packet before submitting to the selected bank."
            />

            <div className="review-list" style={{ marginBottom: '20px' }}>
              <div className="review-row">
                <span>Target Lender:</span>
                <strong>{bankOptions.find((b) => b.value === targetBank)?.label || 'State Bank of India'}</strong>
              </div>
              <div className="review-row">
                <span>Selected Scheme:</span>
                <strong>{schemeOptions.find((s) => s.value === scheme)?.label || 'CGTMSE Working Capital Facility'}</strong>
              </div>
              <div className="review-row">
                <span>Facility Amount:</span>
                <strong className="money">₹ {amount} ({tenureYears} Years Tenure)</strong>
              </div>
              <div className="review-row">
                <span>Applicant Enterprise:</span>
                <strong>{businessName} ({udyamNo})</strong>
              </div>
              <div className="review-row">
                <span>Document Vault Status:</span>
                <Badge tone="success">4/4 Documents Attached</Badge>
              </div>
            </div>

            {/* STATUTORY CONSENT CHECKBOX */}
            <div className="consent-check" style={{ background: '#F8FAFC', padding: '16px', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
              <input
                id="app-consent"
                type="checkbox"
                checked={agreeConsent}
                onChange={(e) => setAgreeConsent(e.target.checked)}
                required
              />
              <label htmlFor="app-consent" style={{ cursor: 'pointer' }}>
                I authorize <strong>CredSaathi</strong> to format and submit this structured application packet to the selected bank partner upon my consent. CredSaathi is a technology facilitation platform and does not approve loans or make credit decisions.
              </label>
            </div>

            <div className="security-line" style={{ marginTop: '14px' }}>
              <Lock size={16} style={{ color: '#059669' }} /> Consent timestamps are recorded server-side for audit compliance.
            </div>
          </div>
        )}

        {/* FORM NAVIGATION ACTIONS */}
        <div className="form-actions" style={{ marginTop: '24px', paddingTop: '18px', borderTop: '1px solid #E2E8F0' }}>
          <Button
            type="button"
            variant="secondary"
            onClick={() => {
              if (currentStep > 0) setCurrentStep(currentStep - 1);
              else navigate('/applicant/applications');
            }}
          >
            {currentStep === 0 ? 'Cancel' : 'Previous Step'}
          </Button>

          {currentStep < steps.length - 1 ? (
            <Button type="button" variant="primary" onClick={handleNextStep}>
              Continue to Step {currentStep + 2} <ArrowRight size={16} />
            </Button>
          ) : (
            <Button
              type="button"
              variant="trust"
              loading={loading}
              onClick={handleFinalSubmit}
            >
              Submit Application to Bank <ArrowRight size={16} />
            </Button>
          )}
        </div>
      </Card>
    </>
  );
}
