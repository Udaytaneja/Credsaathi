import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, ArrowRight, CheckCircle2, Info, ShieldCheck, Sparkles, RefreshCw, ExternalLink } from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card } from '../components/Card';
import Badge from '../components/Badge';
import { Button } from '../components/Button';
import { services } from '../services';
import type { Scheme } from '../types';

export default function Schemes() {
  const navigate = useNavigate();

  // Search & Filter State
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedPurpose, setSelectedPurpose] = useState('all');
  const [schemesList, setSchemesList] = useState<Scheme[]>([]);

  // UX States
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  // Debounce search effect (300ms)
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 300);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  const fetchSchemes = useCallback(async (query: string) => {
    setLoading(true);
    setErrorMsg('');
    try {
      const data = (await services.schemes(query)) as Scheme[];
      setSchemesList(data);
    } catch {
      setErrorMsg('Failed to load schemes. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    (services.schemes(debouncedSearch) as Promise<Scheme[]>).then((data) => {
      if (isMounted) {
        setSchemesList(data);
        setLoading(false);
      }
    }).catch(() => {
      if (isMounted) {
        setErrorMsg('Failed to load schemes. Please try again.');
        setLoading(false);
      }
    });
    return () => { isMounted = false; };
  }, [debouncedSearch]);

  // Filter by purpose
  const filteredSchemes = useMemo(() => {
    if (selectedPurpose === 'all') return schemesList;
    return schemesList.filter(
      (s) => s.purpose.toLowerCase().includes(selectedPurpose.toLowerCase()) || s.name.toLowerCase().includes(selectedPurpose.toLowerCase())
    );
  }, [schemesList, selectedPurpose]);

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
        <div className="step done">
          <span>✓</span>
          <small>Financial Profile</small>
        </div>
        <div className="step active">
          <span>4</span>
          <small>Scheme Discovery (Active)</small>
        </div>
      </div>

      <PageTitle
        eyebrow="PROGRESSIVE ONBOARDING · STEP 4 OF 4"
        title="Matched Loan Scheme Discovery"
        subtitle="Explore relevant government & bank loan schemes matching your profile and financing requirements."
        action={
          <Badge tone="success" icon={<CheckCircle2 size={14} />}>
            Step 4 · 100% Dossier Ready
          </Badge>
        }
      />

      {/* STATUTORY DISCLAIMER BANNER */}
      <div className="info-box" style={{ marginBottom: '20px', background: '#F8FAFC', borderColor: '#E2E8F0' }}>
        <ShieldCheck size={20} style={{ color: '#059669', flexShrink: 0 }} />
        <div>
          <strong>Indicative Scheme Relevance Signal:</strong>
          <p>
            Relevance matches are self-assessed signals based on your profile inputs. They represent scheme discovery relevance, <strong>NOT</strong> an approval probability, guaranteed sanction, or credit score.
          </p>
        </div>
      </div>

      {/* SEARCH AND FILTERS BAR */}
      <div className="search-row" style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        <div className="search-box" style={{ flex: 1 }}>
          <Search size={18} />
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by scheme name, purpose (Mudra, PMEGP, Working Capital, Agri)…"
          />
          {searchTerm && (
            <button
              type="button"
              style={{ border: 0, background: 'transparent', color: '#64748B', fontSize: '11px', cursor: 'pointer' }}
              onClick={() => setSearchTerm('')}
            >
              Clear
            </button>
          )}
        </div>

        <div style={{ display: 'flex', gap: '6px' }}>
          {['all', 'working capital', 'pmegp', 'mudra', 'agri'].map((filter) => (
            <button
              key={filter}
              type="button"
              className={`btn ${selectedPurpose === filter ? 'btn-primary' : 'btn-secondary'}`}
              style={{ padding: '6px 12px', fontSize: '12px', textTransform: 'capitalize' }}
              onClick={() => setSelectedPurpose(filter)}
            >
              {filter === 'all' ? 'All Schemes' : filter}
            </button>
          ))}
        </div>
      </div>

      {/* ERROR FEEDBACK BANNER */}
      {errorMsg && (
        <div className="form-error" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Info size={16} style={{ display: 'inline', marginRight: '6px' }} />
            {errorMsg}
          </div>
          <Button variant="ghost" size="md" onClick={() => fetchSchemes(debouncedSearch)}>
            <RefreshCw size={14} /> Retry Loading
          </Button>
        </div>
      )}

      {/* SCHEME CARDS LAYOUT */}
      <div className="scheme-layout">
        <div className="scheme-list" style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {/* LOADING SKELETON STATE */}
          {loading && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {[1, 2, 3].map((idx) => (
                <Card key={idx} style={{ padding: '24px', opacity: 0.6 }}>
                  <div style={{ height: '20px', width: '30%', background: '#E2E8F0', borderRadius: '4px', marginBottom: '12px' }} />
                  <div style={{ height: '24px', width: '60%', background: '#CBD5E1', borderRadius: '4px', marginBottom: '8px' }} />
                  <div style={{ height: '14px', width: '90%', background: '#E2E8F0', borderRadius: '4px', marginBottom: '16px' }} />
                  <div style={{ height: '60px', width: '100%', background: '#F1F5F9', borderRadius: '8px' }} />
                </Card>
              ))}
            </div>
          )}

          {/* SCHEME LIST CARDS */}
          {!loading && filteredSchemes.map((scheme, i) => (
            <Card key={scheme.id} className={i === 0 ? 'scheme-card featured' : 'scheme-card'}>
              <div className="scheme-card-top">
                <Badge tone={i === 0 ? 'success' : 'neutral'}>
                  {scheme.matchLabel}
                </Badge>
                <span className="muted">Status: {scheme.status}</span>
              </div>

              <h2>{scheme.name}</h2>
              <p>{scheme.description}</p>

              {/* AI EXPLANATION SECTION */}
              <div className="reason-box">
                <strong style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Sparkles size={16} style={{ color: '#059669' }} /> Why this scheme may be relevant to you
                </strong>
                <ul>
                  {scheme.reasons.map((reason, idx) => (
                    <li key={idx}>
                      <CheckCircle2 size={16} /> {reason}
                    </li>
                  ))}
                </ul>
              </div>

              {/* SCHEME METRICS & METADATA */}
              <div className="scheme-meta">
                <span>
                  <b>Primary Purpose</b>
                  {scheme.purpose}
                </span>
                <span>
                  <b>Documents Required</b>
                  {scheme.documents.length} verified items
                </span>
                <span>
                  <b>Source Reference</b>
                  {scheme.source}
                </span>
              </div>

              {/* CARD ACTIONS */}
              <div className="card-actions">
                <Link className="text-link" to={`/applicant/schemes/${scheme.id}`}>
                  View Full Details <ExternalLink size={14} style={{ display: 'inline' }} />
                </Link>

                <Button
                  variant="primary"
                  onClick={() => navigate('/applicant/applications/new')}
                >
                  Start Guided Application <ArrowRight size={16} />
                </Button>
              </div>
            </Card>
          ))}

          {/* NO RESULTS EMPTY STATE */}
          {!loading && filteredSchemes.length === 0 && (
            <div className="empty-state">
              <Info size={32} />
              <h3>No matching schemes found</h3>
              <p>Try searching for a broader keyword such as "Mudra", "PMEGP", or "Working Capital".</p>
              <Button
                variant="secondary"
                size="md"
                style={{ marginTop: '12px' }}
                onClick={() => { setSearchTerm(''); setSelectedPurpose('all'); }}
              >
                Reset Search Filters
              </Button>
            </div>
          )}
        </div>

        {/* SIDEBAR ADVISORY & ASSISTANCE */}
        <aside className="scheme-aside">
          <Card>
            <ShieldCheck size={24} style={{ color: '#059669', marginBottom: '8px' }} />
            <h3 style={{ fontSize: '15px', margin: '0 0 6px', color: '#0B192C' }}>Source &amp; Verification</h3>
            <p className="muted" style={{ fontSize: '11px', lineHeight: '18px' }}>
              CredSaathi scheme information is cross-referenced with official RBI, Ministry of MSME, and bank guidelines.
            </p>
            <div style={{ marginTop: '12px', borderTop: '1px solid #E2E8F0', paddingTop: '10px', fontSize: '10px', color: '#94A3B8' }}>
              Last Verified: October 2026
            </div>
          </Card>

          <Card style={{ background: '#EFF4FF', border: '1px solid #C7D2FE' }}>
            <span style={{ fontSize: '11px', fontWeight: '700', color: '#0B192C', display: 'block', marginBottom: '4px' }}>
              Need Help Deciding?
            </span>
            <p style={{ fontSize: '11px', color: '#64748B', lineHeight: '17px', margin: 0 }}>
              Ask Saakshi AI assistant to explain scheme eligibility requirements for your specific Udyam vintage.
            </p>
            <Button
              variant="secondary"
              size="md"
              full
              style={{ marginTop: '10px' }}
              onClick={() => navigate('/applicant/assistant')}
            >
              Ask Saakshi Assistant
            </Button>
          </Card>
        </aside>
      </div>
    </>
  );
}
