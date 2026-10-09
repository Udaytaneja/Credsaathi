import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, ArrowRight, ShieldCheck, AlertTriangle, RefreshCw, Save, Sparkles } from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import { Button } from '../components/Button';
import { Field } from '../components/Field';
import Badge from '../components/Badge';
import { getSession } from '../lib/storage';

const categoryOptions = [
  { value: 'micro', label: 'Micro Enterprise (Udyam registered)' },
  { value: 'small', label: 'Small Enterprise' },
  { value: 'medium', label: 'Medium Enterprise' },
  { value: 'individual', label: 'Individual Borrower / Self-Employed' },
  { value: 'agri', label: 'Farmer / Agri-Producer' },
];

const sectorOptions = [
  { value: 'food', label: 'Food Processing & Agriculture' },
  { value: 'retail', label: 'Retail & Wholesale Trade' },
  { value: 'manufacturing', label: 'Light Manufacturing & Textiles' },
  { value: 'services', label: 'Services, IT & Logistics' },
  { value: 'handicraft', label: 'Handicraft & Artisan' },
];

export default function Profile() {
  const navigate = useNavigate();
  const session = getSession();

  // Form State
  const [fullName, setFullName] = useState(session?.name || 'Aarohi Agarwal');
  const [email, setEmail] = useState(session?.email || 'aarohi@example.com');
  const [mobile, setMobile] = useState('9876543210');
  const [businessName, setBusinessName] = useState('Sharma Agro Tech Solutions');
  const [category, setCategory] = useState('micro');
  const [sector, setSector] = useState('food');
  const [udyamNo, setUdyamNo] = useState('UDYAM-HP-01-0012345');
  const [city, setCity] = useState('Una');
  const [state, setState] = useState('Himachal Pradesh');
  const [pincode, setPincode] = useState('174303');
  const [yearsInBusiness, setYearsInBusiness] = useState('3');

  // Page UX States
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !mobile.trim()) {
      setErrorMsg('Please fill in required name and contact fields.');
      return;
    }

    setLoading(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      // Simulate API update boundary call
      await new Promise((resolve) => setTimeout(resolve, 600));
      setSuccessMsg('Profile details saved successfully. Proceeding to Loan Requirement.');
      setTimeout(() => {
        navigate('/applicant/loan-requirement');
      }, 1000);
    } catch {
      setErrorMsg('Failed to update profile. Please click Retry.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* STEP PROGRESS BAR */}
      <div className="stepper" style={{ marginBottom: '20px' }}>
        <div className="step active">
          <span>1</span>
          <small>Basic Profile</small>
        </div>
        <div className="step">
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
        eyebrow="PROGRESSIVE ONBOARDING · STEP 1 OF 3"
        title="Applicant Profile & Business Classification"
        subtitle="Provide your identity and enterprise details to unlock tailored loan scheme recommendations."
        action={
          <Badge tone="success" icon={<CheckCircle2 size={14} />}>
            Step 1 · 25% Complete
          </Badge>
        }
      />

      {/* SUCCESS & ERROR FEEDBACK */}
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

      <div className="two-col">
        {/* MAIN PROFILE FORM */}
        <form onSubmit={handleSave}>
          <Card>
            <CardHeader
              title="Identity & Enterprise Details"
              subtitle="This information is used for self-assessed scheme matching and document building."
            />

            <div className="form-grid">
              <Field
                label="Full Name (as per Aadhar / PAN)"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />

              <Field
                label="Mobile Number"
                value={mobile}
                onChange={(e) => setMobile(e.target.value)}
                required
              />

              <Field
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <Field
                label="Business / Enterprise Name"
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                placeholder="e.g. Sharma Agro Tech Solutions"
              />

              <Field
                label="Enterprise Classification"
                fieldType="select"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                options={categoryOptions}
              />

              <Field
                label="Primary Industry Sector"
                fieldType="select"
                value={sector}
                onChange={(e) => setSector(e.target.value)}
                options={sectorOptions}
              />

              <Field
                label="Udyam / Registration Number (Optional)"
                value={udyamNo}
                onChange={(e) => setUdyamNo(e.target.value)}
                placeholder="UDYAM-XX-00-0000000"
              />

              <Field
                label="Years in Business / Vintage"
                type="number"
                value={yearsInBusiness}
                onChange={(e) => setYearsInBusiness(e.target.value)}
                placeholder="3"
              />

              <Field
                label="City / District"
                value={city}
                onChange={(e) => setCity(e.target.value)}
              />

              <Field
                label="State"
                value={state}
                onChange={(e) => setState(e.target.value)}
              />

              <Field
                label="Pincode"
                value={pincode}
                onChange={(e) => setPincode(e.target.value)}
              />
            </div>

            <div className="form-actions" style={{ marginTop: '24px', paddingTop: '18px', borderTop: '1px solid #E2E8F0' }}>
              <span className="save-note">Profile details are encrypted and stored in your authorized session.</span>
              <Button type="submit" variant="primary" loading={loading}>
                <Save size={16} /> Save &amp; Continue <ArrowRight size={17} />
              </Button>
            </div>
          </Card>
        </form>

        {/* SIDEBAR READINESS & ASSISTANT WIDGETS */}
        <aside>
          <Card>
            <CardHeader title="Verification & Readiness" />
            <div className="verification">
              <CheckCircle2 size={24} style={{ color: '#059669', flexShrink: 0 }} />
              <div>
                <strong>Identity Verified</strong>
                <p>Login credentials and phone number verified. Backend authorization is enforced server-side.</p>
              </div>
            </div>

            <div className="info-box">
              <ShieldCheck size={18} style={{ color: '#059669', flexShrink: 0 }} />
              <div>
                <strong>Data Protection Guarantee</strong>
                <p>Your details are shared only with explicit consent during loan application submission.</p>
              </div>
            </div>
          </Card>

          <Card className="assistant-card">
            <div className="assistant-orb small">
              <Sparkles size={18} />
            </div>
            <h3 style={{ fontSize: '15px', margin: '10px 0 4px', color: '#0B192C' }}>Saakshi Assistant Tip</h3>
            <p style={{ fontSize: '12px', color: '#64748B', lineHeight: '19px' }}>
              Completing your Udyam registration and business vintage details helps match government subsidies like <strong>PMEGP</strong> and <strong>CGTMSE collateral-free guarantees</strong>.
            </p>
            <Button variant="ghost" size="md" onClick={() => navigate('/applicant/assistant')}>
              Ask Saakshi <ArrowRight size={14} />
            </Button>
          </Card>
        </aside>
      </div>
    </>
  );
}
