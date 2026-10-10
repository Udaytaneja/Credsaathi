import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, ShieldCheck, AlertTriangle } from 'lucide-react';
import Logo from '../components/Logo';
import { Button } from '../components/Button';
import { setSession } from '../lib/storage';
import { services } from '../services';
import type { UserSession } from '../types';

const entityTypes = [
  { id: 'micro', label: 'Micro-Enterprise', hindi: 'सूक्ष्म उद्यम' },
  { id: 'self', label: 'Self-Employed', hindi: 'स्व-नियोजित' },
  { id: 'salaried', label: 'Salaried', hindi: 'वेतनभोगी' },
  { id: 'farmer', label: 'Farmer / Agri', hindi: 'किसान' },
  { id: 'student', label: 'Student / Youth', hindi: 'युवा / छात्र' },
];

export default function Register() {
  const navigate = useNavigate();

  const [role, setRole] = useState<'APPLICANT' | 'BANKER'>('APPLICANT');
  const [selectedEntity, setSelectedEntity] = useState('micro');

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreeConsent, setAgreeConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim() || !email.trim() || !password.trim()) {
      setError('Please complete all required fields.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match. Please re-enter your password.');
      return;
    }

    if (!agreeConsent) {
      setError('You must authorize CredSaathi data processing terms to proceed.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Public registration safely creates APPLICANT role users
      const session = (await services.register(name, email, password)) as UserSession;
      session.role = 'APPLICANT'; // Ensure public registration produces Applicant users only
      setSession(session);
      navigate('/applicant/dashboard');
    } catch (err: unknown) {
      const errorObj = err as Error;
      if (errorObj.message === 'Failed to fetch' || errorObj.name === 'TypeError') {
        setError('Unable to connect to CredSaathi server. Please check your connection or backend URL.');
      } else {
        setError(errorObj.message || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-brand">
        <Link to="/">
          <Logo />
        </Link>
        <span>
          <ShieldCheck size={14} /> Applicant Registration
        </span>
      </div>

      <div className="auth-card wide">
        {/* HEADER */}
        <div className="auth-head">
          <div className="eyebrow">GET STARTED / नया खाता लें</div>
          <h1>Create your CredSaathi account</h1>
          <p>Register as a loan applicant to explore schemes and prepare structured applications.</p>
        </div>

        {/* ROLE INDICATOR */}
        <div className="auth-role-tabs">
          <button
            type="button"
            className={`auth-role-tab ${role === 'APPLICANT' ? 'active' : ''}`}
            onClick={() => setRole('APPLICANT')}
          >
            <span>Loan Applicant Account</span>
            <small>ऋण आवेदक खाता</small>
          </button>
          
          <button
            type="button"
            className={`auth-role-tab ${role === 'BANKER' ? 'active' : ''}`}
            onClick={() => setRole('BANKER')}
          >
            <span>Bank Officer Onboarding</span>
            <small>बैंक अधिकारी सत्यापन (Institutional verification required)</small>
          </button>
        </div>

        {/* ENTITY TYPE SELECTOR CHIPS */}
        <div style={{ margin: '16px 0 8px' }}>
          <label className="field">
            <span>Select Applicant Category / श्रेणी चुनें</span>
          </label>
          <div className="chip-grid">
            {entityTypes.map((item) => (
              <div
                key={item.id}
                className={`entity-chip ${selectedEntity === item.id ? 'selected' : ''}`}
                onClick={() => setSelectedEntity(item.id)}
              >
                <div>{item.label}</div>
                <small style={{ display: 'block', fontSize: '9px', opacity: 0.8 }}>{item.hindi}</small>
              </div>
            ))}
          </div>
        </div>

        {/* ERROR DISPLAY */}
        {error && (
          <div className="form-error" style={{ marginBottom: '16px' }}>
            <AlertTriangle size={16} style={{ display: 'inline', marginRight: '6px' }} />
            {error}
          </div>
        )}

        {/* REGISTRATION FORM */}
        <form onSubmit={handleSubmit} className="form-stack">
          <div className="field">
            <label htmlFor="reg-name">
              <span>Full Name (as per Aadhar / PAN)</span>
              <em>*</em>
            </label>
            <input
              id="reg-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Aarohi Sharma"
              required
            />
          </div>

          <div className="form-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="field">
              <label htmlFor="reg-email">
                <span>Email Address</span>
                <em>*</em>
              </label>
              <input
                id="reg-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="aarohi@example.com"
                required
              />
            </div>

            <div className="field">
              <label htmlFor="reg-mobile">
                <span>Mobile Number</span>
                <em>*</em>
              </label>
              <input
                id="reg-mobile"
                type="tel"
                maxLength={10}
                value={mobile}
                onChange={(e) => setMobile(e.target.value.replace(/\D/g, ''))}
                placeholder="9876543210"
                required
              />
            </div>
          </div>

          <div className="form-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="field">
              <label htmlFor="reg-pass">
                <span>Password (min 8 chars)</span>
                <em>*</em>
              </label>
              <input
                id="reg-pass"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Create a strong password"
                minLength={8}
                required
              />
            </div>

            <div className="field">
              <label htmlFor="reg-confirm">
                <span>Confirm Password</span>
                <em>*</em>
              </label>
              <input
                id="reg-confirm"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter password"
                minLength={8}
                required
              />
            </div>
          </div>

          {/* CONSENT CHECKBOX */}
          <div className="consent-check" style={{ marginTop: '12px', background: '#F8FAFC', padding: '14px', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
            <input
              id="consent"
              type="checkbox"
              checked={agreeConsent}
              onChange={(e) => setAgreeConsent(e.target.checked)}
              required
            />
            <label htmlFor="consent" style={{ cursor: 'pointer' }}>
              I authorize <strong>CredSaathi</strong> to process my details in accordance with the Privacy Policy and share them strictly with selected lending institutions upon my explicit consent. CredSaathi is a technology platform for loan discovery and application assistance and does not approve or guarantee loans.
            </label>
          </div>

          <Button type="submit" variant="primary" size="lg" full loading={loading}>
            Create Applicant Account / सत्यापन के लिए आगे बढ़ें <ArrowRight size={17} />
          </Button>
        </form>

        {/* LOGIN LINK */}
        <div className="auth-divider">
          <span>Already registered with CredSaathi?</span>
        </div>

        <Link className="btn btn-secondary full" to="/login">
          Sign In / साइन-इन करें
        </Link>

        {/* SECURITY & STATUTORY FOOTER */}
        <div className="security-banner-card">
          <ShieldCheck size={22} />
          <div>
            <h4>Secure, Consent-Driven &amp; Transparent</h4>
            <p style={{ margin: 0, fontSize: '11px', color: '#64748B' }}>
              CredSaathi is a technology platform for loan discovery and application assistance and does not approve or guarantee loans. All loan approvals remain at the sole discretion of lending institutions. Support: support@credsaathi.in
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
