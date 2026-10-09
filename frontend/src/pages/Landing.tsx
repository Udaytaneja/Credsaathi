import React, { useState } from 'react';
import { ArrowRight, CheckCircle2, FileCheck2, Search, ShieldCheck, Sparkles, WalletCards, ChevronDown } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import PublicHeader from '../components/PublicHeader';
import Logo from '../components/Logo';
import { getSession } from '../lib/storage';

export default function Landing() {
  const navigate = useNavigate();
  const session = getSession();
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const handleStartJourney = () => {
    if (session) {
      navigate(session.role === 'APPLICANT' ? '/applicant/dashboard' : '/banker/dashboard');
    } else {
      navigate('/register');
    }
  };

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  return (
    <div className="public-page">
      <div className="public-container">
        <PublicHeader />

        {/* HERO SECTION */}
        <section className="hero">
          <div className="hero-copy">
            <span className="hero-kicker">
              <ShieldCheck size={15} /> Transparent Financing Discovery Platform / विश्वसनीय ऋण खोज मंच
            </span>
            
            <h1>
              Simplifying loan discovery for micro-entrepreneurs &amp; applicants across India.
            </h1>
            
            <p>
              CredSaathi helps you discover relevant government &amp; bank loan schemes, understand why they fit your profile, prepare structured documentation, and track your application transparently.
            </p>

            <div className="hero-actions">
              <button className="btn btn-primary btn-lg" onClick={handleStartJourney} type="button">
                Start your journey / शुरू करें <ArrowRight size={18} />
              </button>
              <Link className="btn btn-secondary btn-lg" to="/login">
                Sign in to account / लॉग इन
              </Link>
            </div>

            <div className="trust-row">
              <span><CheckCircle2 size={16} /> Explainable scheme matching</span>
              <span><CheckCircle2 size={16} /> Secure document preparation</span>
              <span><CheckCircle2 size={16} /> English + हिंदी support</span>
            </div>
          </div>

          <div className="hero-panel">
            <div className="mini-label">YOUR FINANCING JOURNEY / आपकी यात्रा</div>
            
            <div className="journey-step active">
              <div className="journey-icon"><Search size={18} /></div>
              <div>
                <strong>1. Discover / ऋण योजना खोजें</strong>
                <span>See relevant schemes matching your loan requirement</span>
              </div>
            </div>
            
            <div className="journey-line" />
            
            <div className="journey-step">
              <div className="journey-icon"><FileCheck2 size={18} /></div>
              <div>
                <strong>2. Prepare / दस्तावेज तैयार करें</strong>
                <span>Build structured applications with document checklist</span>
              </div>
            </div>
            
            <div className="journey-line" />
            
            <div className="journey-step">
              <div className="journey-icon"><WalletCards size={18} /></div>
              <div>
                <strong>3. Track / ट्रैक करें</strong>
                <span>Follow status updates directly from backend lender state</span>
              </div>
            </div>

            <div className="panel-disclaimer">
              <ShieldCheck size={16} />
              <span>
                CredSaathi does not approve or guarantee loans. All credit sanction decisions remain with lending institutions.
              </span>
            </div>
          </div>
        </section>

        {/* HOW IT WORKS SECTION */}
        <section id="how" className="section">
          <div className="section-heading">
            <div className="eyebrow">HOW IT WORKS / कैसे काम करता है</div>
            <h2>A simpler path from need to application.</h2>
            <p>Progressive steps, clear explanations, and no hidden surprises.</p>
          </div>

          <div className="feature-grid">
            <Feature
              n="01"
              icon={<Search size={22} />}
              title="Discover Relevant Options"
              hindiTitle="ऋण योजना खोजें"
              text="Explore verified Mudra, PMEGP, MSME, and Agri loan scheme details tailored to your specific financial needs."
            />
            <Feature
              n="02"
              icon={<Sparkles size={22} />}
              title="AI-Assisted Guidance"
              hindiTitle="साक्षी AI सहायक"
              text="Get explainable insights from Saakshi on scheme eligibility and required documents without approval promises."
            />
            <Feature
              n="03"
              icon={<FileCheck2 size={22} />}
              title="Prepare &amp; Submit"
              hindiTitle="आवेदन और दस्तावेज"
              text="Organize your financial profile, upload documents into a consent-driven vault, and submit structured applications."
            />
          </div>
        </section>

        {/* TRUST BANNER SECTION */}
        <section id="trust" className="trust-banner">
          <ShieldCheck size={32} style={{ flexShrink: 0 }} />
          <div>
            <strong>Built on Trust, Consent &amp; Data Protection / सुरक्षा एवं गोपनीयता</strong>
            <p>
              CredSaathi is a technology facilitation platform. We enforce consent-driven data sharing, end-to-end security, and zero upfront approval fees.
            </p>
          </div>
        </section>

        {/* FAQ SECTION */}
        <section id="faq" className="section faq">
          <div className="section-heading">
            <div className="eyebrow">FREQUENTLY ASKED QUESTIONS / अक्सर पूछे जाने वाले प्रश्न</div>
            <h2>What CredSaathi is — and isn't.</h2>
          </div>

          <div className="faq-grid">
            <FaqCard
              isOpen={openFaq === 0}
              onToggle={() => toggleFaq(0)}
              question="Is loan approval guaranteed on CredSaathi?"
              hindiQuestion="क्या ऋण स्वीकृति की गारंटी है?"
              answer="No. CredSaathi is a technology platform for scheme discovery and document organization. Official loan approvals, interest rates, and disbursements remain at the sole discretion of RBI-registered banks and lenders."
            />
            <FaqCard
              isOpen={openFaq === 1}
              onToggle={() => toggleFaq(1)}
              question="Does CredSaathi charge upfront approval fees?"
              hindiQuestion="क्या क्रेडसाथी कोई अग्रिम शुल्क लेता है?"
              answer="No. CredSaathi representatives will never ask for advance loan approval fees, UPI PINs, net banking passwords, or OTPs."
            />
            <FaqCard
              isOpen={openFaq === 2}
              onToggle={() => toggleFaq(2)}
              question="How is my financial data protected?"
              hindiQuestion="मेरा डेटा कैसे सुरक्षित है?"
              answer="Your documents and profile details are stored in a consent-driven workspace. Information is only shared with authorized lenders upon your explicit consent."
            />
          </div>
        </section>

        {/* FOOTER */}
        <footer className="footer">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <Logo />
            <span>Multilingual loan discovery and document preparation platform across India.</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', textAlign: 'right' }}>
            <span>Email Support: <strong>support@credsaathi.in</strong></span>
            <span>© 2026 CredSaathi Technologies Private Limited. All rights reserved.</span>
          </div>
        </footer>
      </div>
    </div>
  );
}

function Feature({ n, icon, title, hindiTitle, text }: { n: string; icon: React.ReactNode; title: string; hindiTitle: string; text: string }) {
  return (
    <div className="feature-card">
      <div className="feature-top">
        <span>{n}</span>
        <div>{icon}</div>
      </div>
      <h3>{title} <span style={{ fontSize: '13px', fontWeight: '500', color: '#64748B', display: 'block' }}>{hindiTitle}</span></h3>
      <p>{text}</p>
    </div>
  );
}

function FaqCard({ isOpen, onToggle, question, hindiQuestion, answer }: { isOpen: boolean; onToggle: () => void; question: string; hindiQuestion: string; answer: string }) {
  return (
    <div style={{ background: '#FFF', border: '1px solid #E2E8F0', borderRadius: '14px', padding: '20px', cursor: 'pointer' }} onClick={onToggle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '10px' }}>
        <div>
          <h3 style={{ fontSize: '15px', margin: 0, color: '#0B192C' }}>{question}</h3>
          <span style={{ fontSize: '12px', color: '#64748B' }}>{hindiQuestion}</span>
        </div>
        <ChevronDown size={18} style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s', flexShrink: 0 }} />
      </div>
      {isOpen && (
        <p style={{ fontSize: '13px', lineHeight: '21px', color: '#64748B', marginTop: '12px', borderTop: '1px solid #F1F5F9', paddingTop: '10px' }}>
          {answer}
        </p>
      )}
    </div>
  );
}
