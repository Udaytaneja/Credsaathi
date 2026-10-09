import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, ArrowRight, Eye, EyeOff, User, AlertTriangle } from 'lucide-react';
import Logo from '../components/Logo';
import { Button } from '../components/Button';
import { services } from '../services';
import { setSession } from '../lib/storage';
import type { UserSession } from '../types';

export default function Login() {
  const navigate = useNavigate();

  // Tab states matching Stitch
  const [userRole, setUserRole] = useState<'APPLICANT' | 'BANKER'>('APPLICANT');
  const [authMode, setAuthMode] = useState<'password' | 'otp'>('password');

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mobile, setMobile] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // OTP State Machine
  const [otpSent, setOtpSent] = useState(false);
  const [otpValues, setOtpValues] = useState<string[]>(['', '', '', '', '', '']);
  const [timer, setTimer] = useState(45);
  const [timerActive, setTimerActive] = useState(false);
  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

  // OTP Countdown Timer effect
  useEffect(() => {
    if (!timerActive) return;
    const interval = setInterval(() => {
      setTimer((t) => {
        if (t <= 1) {
          setTimerActive(false);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [timerActive]);

  // Handle Password Submit
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Please enter both email and password.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const session = (await services.login(email, password)) as UserSession;
      // Ensure session role reflects selection if demo user
      if (userRole === 'BANKER' && session.role === 'APPLICANT') {
        session.role = 'BANKER';
      }
      setSession(session);
      navigate(session.role === 'BANKER' ? '/banker/dashboard' : '/applicant/dashboard');
    } catch (err: unknown) {
      const errorObj = err as Error;
      setError(errorObj.message || 'Unable to sign in. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  // Handle Send OTP
  const handleSendOtp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!mobile.trim() || mobile.length < 10) {
      setError('Please enter a valid 10-digit mobile number.');
      return;
    }
    setError('');
    setOtpSent(true);
    setTimer(45);
    setTimerActive(true);
  };

  // Handle OTP digit change
  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) value = value.slice(-1);
    const newValues = [...otpValues];
    newValues[index] = value;
    setOtpValues(newValues);

    if (value && index < 5) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  // Handle OTP digit backspace
  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otpValues[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  // Handle Verify & Sign In with OTP
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    const otpCode = otpValues.join('');
    if (otpCode.length < 6) {
      setError('Please enter the complete 6-digit OTP code.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Authenticate via service boundary proxy
      const demoEmail = mobile ? `${mobile}@credsaathi.in` : 'aarohi@credsaathi.in';
      const session = (await services.login(demoEmail, 'otp-login')) as UserSession;
      if (userRole === 'BANKER') session.role = 'BANKER';
      setSession(session);
      navigate(session.role === 'BANKER' ? '/banker/dashboard' : '/applicant/dashboard');
    } catch (err: unknown) {
      const errorObj = err as Error;
      setError(errorObj.message || 'OTP verification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Quick Demo Login
  const handleDemoLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const targetEmail = userRole === 'BANKER' ? 'banker@credsaathi.in' : 'aarohi@credsaathi.in';
      const session = (await services.login(targetEmail, 'demo')) as UserSession;
      if (userRole === 'BANKER') session.role = 'BANKER';
      setSession(session);
      navigate(session.role === 'BANKER' ? '/banker/dashboard' : '/applicant/dashboard');
    } catch (err: unknown) {
      const errorObj = err as Error;
      setError(errorObj.message || 'Demo login failed.');
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
          <ShieldCheck size={14} /> Secure Authentication Portal
        </span>
      </div>

      <div className="auth-card">
        {/* HEADER */}
        <div className="auth-head">
          <div className="eyebrow">PORTAL ACCESS / पोर्टल लॉगिन</div>
          <h1>Sign in to CredSaathi</h1>
          <p>Access your financing discovery workspace securely.</p>
        </div>

        {/* ROLE SELECTION TABS */}
        <div className="auth-role-tabs">
          <button
            type="button"
            className={`auth-role-tab ${userRole === 'APPLICANT' ? 'active' : ''}`}
            onClick={() => setUserRole('APPLICANT')}
          >
            <span>Applicant Login</span>
            <small>ऋण आवेदक लॉगिन</small>
          </button>
          
          <button
            type="button"
            className={`auth-role-tab ${userRole === 'BANKER' ? 'active' : ''}`}
            onClick={() => setUserRole('BANKER')}
          >
            <span>Partner Banker</span>
            <small>बैंक अधिकारी लॉगिन</small>
          </button>
        </div>

        {/* AUTH MODE SWITCH TABS */}
        <div className="auth-mode-switch">
          <button
            type="button"
            className={`auth-mode-btn ${authMode === 'password' ? 'active' : ''}`}
            onClick={() => { setAuthMode('password'); setError(''); }}
          >
            Password Sign-in / पासवर्ड से साइन-इन
          </button>
          
          <button
            type="button"
            className={`auth-mode-btn ${authMode === 'otp' ? 'active' : ''}`}
            onClick={() => { setAuthMode('otp'); setError(''); }}
          >
            Mobile OTP / मोबाइल OTP
          </button>
        </div>

        {/* ERROR DISPLAY */}
        {error && (
          <div className="form-error" style={{ marginBottom: '16px' }}>
            <AlertTriangle size={16} style={{ display: 'inline', marginRight: '6px' }} />
            {error}
          </div>
        )}

        {/* PASSWORD SIGN IN FORM */}
        {authMode === 'password' && (
          <form onSubmit={handlePasswordSubmit} className="form-stack">
            <div className="field">
              <label htmlFor="login-email">
                <span>Email address or Username</span>
                <em>*</em>
              </label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="aarohi@example.com"
                required
              />
            </div>

            <div className="field">
              <label htmlFor="login-password">
                <span>Password</span>
                <em>*</em>
              </label>
              <div className="password-wrap">
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div className="form-meta">
              <label className="checkbox">
                <input type="checkbox" defaultChecked /> Remember workspace
              </label>
              <button
                type="button"
                style={{ background: 'none', border: 'none', padding: 0, color: 'var(--navy)', textDecoration: 'underline', fontSize: '13px', cursor: 'pointer' }}
                onClick={() => setError('Password reset instructions will be sent to your registered email upon backend server connection.')}
              >
                Forgot password?
              </button>
            </div>

            <Button type="submit" variant="primary" size="lg" full loading={loading}>
              Sign in to Workspace <ArrowRight size={17} />
            </Button>
          </form>
        )}

        {/* MOBILE OTP SIGN IN FORM */}
        {authMode === 'otp' && (
          <div>
            {!otpSent ? (
              <form onSubmit={handleSendOtp} className="form-stack">
                <div className="field">
                  <label htmlFor="login-mobile">
                    <span>10-Digit Mobile Number</span>
                    <em>*</em>
                  </label>
                  <div className="input-affix">
                    <b>+91</b>
                    <input
                      id="login-mobile"
                      type="tel"
                      maxLength={10}
                      value={mobile}
                      onChange={(e) => setMobile(e.target.value.replace(/\D/g, ''))}
                      placeholder="9876543210"
                      required
                    />
                  </div>
                </div>

                <Button type="submit" variant="primary" size="lg" full>
                  Send OTP Code / OTP भेजें <ArrowRight size={17} />
                </Button>
              </form>
            ) : (
              <form onSubmit={handleVerifyOtp} className="form-stack">
                <div className="field" style={{ textAlign: 'center' }}>
                  <label>
                    <span>Enter 6-Digit OTP sent to +91 {mobile}</span>
                  </label>
                  
                  <div className="otp-inputs">
                    {otpValues.map((val, idx) => (
                      <input
                        key={idx}
                        ref={(el) => { otpRefs.current[idx] = el; }}
                        type="text"
                        inputMode="numeric"
                        maxLength={1}
                        className="otp-box"
                        value={val}
                        onChange={(e) => handleOtpChange(idx, e.target.value)}
                        onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                        autoFocus={idx === 0}
                      />
                    ))}
                  </div>

                  <div className="otp-timer">
                    <span>
                      {timerActive ? (
                        <>Resend OTP in <strong>0:{timer < 10 ? `0${timer}` : timer}</strong></>
                      ) : (
                        <button
                          type="button"
                          className="text-link"
                          style={{ border: 0, background: 'transparent', padding: 0 }}
                          onClick={() => { setTimer(45); setTimerActive(true); }}
                        >
                          Resend OTP Code
                        </button>
                      )}
                    </span>
                    <button
                      type="button"
                      className="text-link"
                      style={{ border: 0, background: 'transparent', padding: 0 }}
                      onClick={() => setOtpSent(false)}
                    >
                      Change Mobile Number
                    </button>
                  </div>
                </div>

                <Button type="submit" variant="trust" size="lg" full loading={loading}>
                  Verify &amp; Sign In / सत्यापन करें <ArrowRight size={17} />
                </Button>
              </form>
            )}
          </div>
        )}

        {/* DEMO ACCOUNT QUICK LOGIN */}
        <div className="auth-divider">
          <span>OR QUICK ACCESS / त्वरित साइन-इन</span>
        </div>

        <Button
          type="button"
          variant="secondary"
          full
          onClick={handleDemoLogin}
          disabled={loading}
        >
          <User size={16} /> Fast Demo Account Login ({userRole})
        </Button>

        {/* REGISTRATION SWITCH */}
        <div className="text-center" style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid #E2E8F0' }}>
          <p className="auth-disclaimer">
            New to CredSaathi?{' '}
            <Link className="text-link" to="/register" style={{ fontWeight: '700' }}>
              Create an Account / खाता बनाएं <ArrowRight size={14} style={{ display: 'inline' }} />
            </Link>
          </p>
        </div>

        {/* STATUTORY SECURITY NOTICE */}
        <div className="security-banner-card">
          <ShieldCheck size={22} />
          <div>
            <h4>User Safety &amp; Statutory Notice</h4>
            <ul>
              <li>CredSaathi does not approve loans, disburse funds, or guarantee sanctions.</li>
              <li>CredSaathi representatives will never ask for your UPI PIN, OTP, or advance approval fees.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
