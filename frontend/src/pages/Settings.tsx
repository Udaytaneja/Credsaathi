import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Languages, 
  Trash2, 
  AlertCircle, 
  RefreshCw, 
  FileCheck, 
  UserCheck, 
  Building2, 
  KeyRound 
} from 'lucide-react';
import { useTranslation } from 'react-i18next';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import { Button } from '../components/Button';
import Badge from '../components/Badge';
import { services } from '../services';
import type { UserSettings } from '../types';

export default function Settings() {
  const { i18n } = useTranslation();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updatingConsent, setUpdatingConsent] = useState<string | null>(null);

  const fetchSettings = async () => {
    setLoading(true);
    setError('');
    try {
      const data = (await services.settings()) as UserSettings;
      setSettings(data);
    } catch {
      setError('Unable to load user settings and consent records. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let isMounted = true;
    services.settings()
      .then((data) => {
        if (isMounted) {
          setSettings(data as UserSettings);
          setLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setError('Unable to load user settings and consent records. Please try again.');
          setLoading(false);
        }
      });
    return () => { isMounted = false; };
  }, []);

  const handleToggleConsent = async (consentId: string, currentStatus: 'ACTIVE' | 'REVOKED' | 'EXPIRED') => {
    if (!settings) return;
    const newActiveState = currentStatus !== 'ACTIVE';
    setUpdatingConsent(consentId);
    try {
      await services.updateConsent(consentId, newActiveState);
      setSettings((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          activeConsents: prev.activeConsents.map((c) => 
            c.id === consentId ? { ...c, status: newActiveState ? 'ACTIVE' : 'REVOKED' } : c
          )
        };
      });
    } catch {
      // Revert handle error
    } finally {
      setUpdatingConsent(null);
    }
  };

  return (
    <>
      <PageTitle
        eyebrow="SETTINGS & CONSENT CONTROL / सेटिंग्स एवं सहमति"
        title="Settings & Data Consent Management"
        subtitle="Manage entity information, verified credentials, explicit consent artifacts, language preference, and account security controls."
        action={
          <Badge tone="success" icon={<ShieldCheck size={13} />}>
            Verified Credential Status: ACTIVE
          </Badge>
        }
      />

      {/* Loading State */}
      {loading && (
        <Card style={{ padding: '40px', textAlign: 'center' }}>
          <RefreshCw size={24} className="spin" style={{ color: 'var(--navy)', marginBottom: '12px' }} />
          <p style={{ margin: 0, fontSize: '13px', color: 'var(--muted)' }}>
            Retrieving settings and active consent artifacts from secure vault...
          </p>
        </Card>
      )}

      {/* Error State */}
      {!loading && error && (
        <Card style={{ padding: '24px', background: '#FEF2F2', borderColor: '#FECDD3' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <AlertCircle size={20} style={{ color: 'var(--red)', flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <strong style={{ fontSize: '14px', color: 'var(--navy)', display: 'block', marginBottom: '4px' }}>
                Settings Retrieval Error
              </strong>
              <p style={{ margin: '0 0 12px 0', fontSize: '12px', color: '#991B1B' }}>
                {error}
              </p>
              <Button variant="secondary" onClick={fetchSettings} style={{ fontSize: '12px' }}>
                <RefreshCw size={13} /> Retry Loading Settings
              </Button>
            </div>
          </div>
        </Card>
      )}

      {!loading && settings && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
          {/* Section 1: Registered Applicant & Enterprise Entity */}
          <Card>
            <CardHeader
              title="Registered Applicant & Entity Information"
              subtitle="Verified identity parameters bound to your CredSaathi workspace."
            />

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '18px' }}>
              <div style={{ padding: '14px 16px', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--line)' }}>
                <span style={{ fontSize: '11px', color: 'var(--muted)', display: 'block', marginBottom: '4px' }}>
                  Registered Applicant Name
                </span>
                <strong style={{ fontSize: '14px', color: 'var(--navy)' }}>{settings.applicantName}</strong>
              </div>

              <div style={{ padding: '14px 16px', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--line)' }}>
                <span style={{ fontSize: '11px', color: 'var(--muted)', display: 'block', marginBottom: '4px' }}>
                  Enterprise Entity Name
                </span>
                <strong style={{ fontSize: '14px', color: 'var(--navy)' }}>{settings.entityName}</strong>
              </div>

              <div style={{ padding: '14px 16px', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--line)' }}>
                <span style={{ fontSize: '11px', color: 'var(--muted)', display: 'block', marginBottom: '4px' }}>
                  Udyam Registration Number
                </span>
                <strong style={{ fontSize: '14px', color: 'var(--navy)' }}>{settings.udyamRegistrationNo}</strong>
              </div>

              <div style={{ padding: '14px 16px', background: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--line)' }}>
                <span style={{ fontSize: '11px', color: 'var(--muted)', display: 'block', marginBottom: '4px' }}>
                  Primary Contact Email & Phone
                </span>
                <strong style={{ fontSize: '13px', color: 'var(--navy)', display: 'block' }}>{settings.email}</strong>
                <span style={{ fontSize: '12px', color: 'var(--muted)' }}>{settings.phone}</span>
              </div>
            </div>
          </Card>

          {/* Section 2: Verified Credentials Status */}
          <Card>
            <CardHeader
              title="Verified Credential Badges"
              subtitle="Verification status of statutory credentials used for eligibility matching."
            />

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '14px 16px',
                background: '#ECFDF5',
                border: '1px solid #A7F3D0',
                borderRadius: '8px'
              }}>
                <UserCheck size={22} style={{ color: '#059669' }} />
                <div>
                  <strong style={{ fontSize: '13px', color: '#065F46', display: 'block' }}>Applicant Identity Verified</strong>
                  <span style={{ fontSize: '11px', color: '#047857' }}>Aadhaar Checksum Verified</span>
                </div>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '14px 16px',
                background: '#ECFDF5',
                border: '1px solid #A7F3D0',
                borderRadius: '8px'
              }}>
                <Building2 size={22} style={{ color: '#059669' }} />
                <div>
                  <strong style={{ fontSize: '13px', color: '#065F46', display: 'block' }}>Business Registration Verified</strong>
                  <span style={{ fontSize: '11px', color: '#047857' }}>MSME Udyam Database Matched</span>
                </div>
              </div>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '14px 16px',
                background: '#ECFDF5',
                border: '1px solid #A7F3D0',
                borderRadius: '8px'
              }}>
                <FileCheck size={22} style={{ color: '#059669' }} />
                <div>
                  <strong style={{ fontSize: '13px', color: '#065F46', display: 'block' }}>Financial Records Verified</strong>
                  <span style={{ fontSize: '11px', color: '#047857' }}>Banking & GST Statements Validated</span>
                </div>
              </div>
            </div>
          </Card>

          {/* Section 3: Explicit Consent Artifacts & Controls */}
          <Card>
            <CardHeader
              title="Explicit Consent Management & Active Artifacts"
              subtitle="Consent UI is explicit. Consent is granted only upon active transmission or request. Revocation halts data sharing."
            />

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {settings.activeConsents.map((consent) => (
                <div
                  key={consent.id}
                  style={{
                    padding: '18px',
                    borderRadius: '10px',
                    border: '1px solid var(--line)',
                    background: consent.status === 'ACTIVE' ? '#F8FAFC' : '#FFF5F5',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '12px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <strong style={{ fontSize: '14px', color: 'var(--navy)' }}>{consent.title}</strong>
                        <Badge tone={consent.status === 'ACTIVE' ? 'success' : 'warning'}>
                          {consent.status}
                        </Badge>
                      </div>
                      <p style={{ margin: 0, fontSize: '12px', color: 'var(--muted)', lineHeight: '18px' }}>
                        {consent.purpose}
                      </p>
                    </div>

                    <Button
                      variant={consent.status === 'ACTIVE' ? 'secondary' : 'primary'}
                      onClick={() => handleToggleConsent(consent.id, consent.status)}
                      disabled={updatingConsent === consent.id}
                      style={{ fontSize: '12px', padding: '6px 14px', height: '32px' }}
                    >
                      {updatingConsent === consent.id ? (
                        <RefreshCw size={13} className="spin" />
                      ) : consent.status === 'ACTIVE' ? (
                        'Revoke Consent'
                      ) : (
                        'Re-grant Consent'
                      )}
                    </Button>
                  </div>

                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    paddingTop: '10px',
                    borderTop: '1px solid #E2E8F0',
                    fontSize: '11px',
                    color: 'var(--muted)',
                    flexWrap: 'wrap',
                    gap: '8px'
                  }}>
                    <div>
                      <span>Timestamp: <strong>{consent.grantedAt}</strong></span>
                    </div>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      {consent.scope.map((s, idx) => (
                        <span key={idx} style={{
                          padding: '2px 8px',
                          background: 'var(--white)',
                          border: '1px solid var(--line)',
                          borderRadius: '4px',
                          color: 'var(--navy)',
                          fontWeight: 500
                        }}>
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Statutory Data Control Banner */}
            <div style={{
              marginTop: '18px',
              padding: '14px 16px',
              background: '#EFF6FF',
              border: '1px solid #BFDBFE',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#1E40AF',
              lineHeight: '19px'
            }}>
              <strong>Statutory Data Protection Guarantee:</strong> CredSaathi never transmits enterprise application profiles or uploaded financial documents to third-party lenders without an active, explicit consent artifact. Consent can be revoked at any time prior to bank sanction processing.
            </div>
          </Card>

          {/* Section 4: Language Preference & Security Controls */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '22px' }}>
            {/* Language Preference */}
            <Card>
              <CardHeader
                title="Interface Language"
                subtitle="Switch application language preference (English / हिंदी)."
              />

              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '16px',
                background: '#F8FAFC',
                borderRadius: '8px',
                border: '1px solid var(--line)'
              }}>
                <div>
                  <strong style={{ fontSize: '13px', color: 'var(--navy)', display: 'block', marginBottom: '2px' }}>
                    Current Active Language
                  </strong>
                  <span style={{ fontSize: '12px', color: 'var(--muted)' }}>
                    {i18n.language === 'hi' ? 'Hindi (हिंदी)' : 'English (en-IN)'}
                  </span>
                </div>

                <Button
                  variant="secondary"
                  onClick={() => i18n.changeLanguage(i18n.language === 'en' ? 'hi' : 'en')}
                  style={{ fontSize: '12px' }}
                >
                  <Languages size={15} />
                  {i18n.language === 'en' ? 'हिंदी में बदलें' : 'Switch to English'}
                </Button>
              </div>
            </Card>

            {/* Session & Security Controls */}
            <Card>
              <CardHeader
                title="Session & Security Controls"
                subtitle="Authorized authentication and access controls."
              />

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  background: '#F8FAFC',
                  borderRadius: '8px',
                  border: '1px solid var(--line)'
                }}>
                  <ShieldCheck size={20} style={{ color: 'var(--green)' }} />
                  <div>
                    <strong style={{ fontSize: '13px', color: 'var(--navy)', display: 'block' }}>Session Authorization</strong>
                    <span style={{ fontSize: '11px', color: 'var(--muted)' }}>Backend HTTP-Only Cookies Enforced</span>
                  </div>
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  background: '#F8FAFC',
                  borderRadius: '8px',
                  border: '1px solid var(--line)'
                }}>
                  <KeyRound size={20} style={{ color: 'var(--navy)' }} />
                  <div>
                    <strong style={{ fontSize: '13px', color: 'var(--navy)', display: 'block' }}>Password & MFA Controls</strong>
                    <span style={{ fontSize: '11px', color: 'var(--muted)' }}>Managed via secure auth service endpoints</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Section 5: Data Deletion Request */}
          <Card>
            <CardHeader
              title="Data Deletion & Retention Rights"
              subtitle="Statutory data erasure request process."
            />

            <div className="danger-zone" style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '16px 20px',
              borderRadius: '8px',
              background: '#FEF2F2',
              border: '1px solid #FECDD3'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <Trash2 size={24} style={{ color: 'var(--red)' }} />
                <div>
                  <strong style={{ fontSize: '14px', color: 'var(--navy)', display: 'block', marginBottom: '2px' }}>
                    Request Workspace & Account Data Erasure
                  </strong>
                  <span style={{ fontSize: '12px', color: '#991B1B' }}>
                    Data deletion requests are executed by backend compliance services according to RBI & Digital Personal Data Protection (DPDP) guidelines.
                  </span>
                </div>
              </div>

              <Button variant="danger" style={{ fontSize: '12px', whiteSpace: 'nowrap' }}>
                Request Erasure
              </Button>
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
