import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle2, Clock3, ShieldCheck, ArrowLeft, FileText, AlertTriangle } from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import StatusPill from '../components/StatusPill';
import { applications } from '../services/mock/data';

const trackerStages = [
  { key: 'SUBMITTED', title: '1. Application Submitted', hindi: 'आवेदन जमा किया गया', desc: 'Packet delivered to State Bank of India MSME desk' },
  { key: 'UNDER_REVIEW', title: '2. Document Verification', hindi: 'दस्तावेज़ सत्यापन', desc: 'Credit analyst reviewing GST returns & bank statements' },
  { key: 'SANCTION', title: '3. Lender Sanction / Underwriting', hindi: 'ऋण स्वीकृति समीक्षा', desc: 'Underwriting committee decision & risk assessment' },
  { key: 'DISBURSED', title: '4. Disbursement & Clearance', hindi: 'ऋण संवितरण', desc: 'Final loan agreement execution & fund transfer' },
];

export default function ApplicationStatus() {
  const { id } = useParams();

  // Find target application or fallback to primary demo item
  const appData = applications.find((a) => a.id === id) || applications[0];
  const appId = id || appData.id;
  const status = appData.status;

  // Compute tracker stage indices cleanly based on backend status
  const currentStageIndex =
    status === 'SUBMITTED'
      ? 0
      : status === 'UNDER_REVIEW' || status === 'ADDITIONAL_INFO_REQUIRED'
      ? 1
      : status === 'ACCEPTED'
      ? 2
      : status === 'CLOSED'
      ? 3
      : 1;

  return (
    <>
      <Link className="back-link" to="/applicant/applications" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '16px', color: '#64748B', fontWeight: '700', fontSize: '12px' }}>
        <ArrowLeft size={16} /> Back to Applications List
      </Link>

      <PageTitle
        eyebrow="APPLICATION STATUS TRACKER"
        title={`Application ${appId}`}
        subtitle="Real-time status tracking read directly from the backend lender state machine."
        action={<StatusPill status={status} />}
      />

      {/* ADDITIONAL INFO REQUIRED ACTION BANNER */}
      {status === 'ADDITIONAL_INFO_REQUIRED' && (
        <div style={{ background: '#FFF6E8', border: '1px solid #F7D9A8', color: '#A15C00', padding: '16px', borderRadius: '12px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <AlertTriangle size={22} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div style={{ flex: 1 }}>
              <strong style={{ fontSize: '14px', color: '#0B192C' }}>Action Required: Bank Requested Supplementary Document</strong>
              <p style={{ margin: '4px 0 10px', fontSize: '12px', color: '#64748B', lineHeight: '18px' }}>
                State Bank of India credit desk requested an updated 3-month GST Return (GSTR-3B) for Q3 FY26 verification.
              </p>
              <Link className="btn btn-primary" to="/applicant/documents" style={{ fontSize: '12px', padding: '8px 14px' }}>
                Upload Required Document to Vault <ArrowLeft size={14} style={{ transform: 'rotate(180deg)', marginLeft: '4px' }} />
              </Link>
            </div>
          </div>
        </div>
      )}

      <div className="details-grid">
        {/* LEFT COLUMN: 4-STAGE PROCESS TRACKER */}
        <Card>
          <CardHeader
            title="Lender Process Timeline / आवेदन प्रगति"
            subtitle="Stage updates are recorded upon receipt of official backend state transitions."
          />

          <div className="status-track" style={{ marginTop: '16px' }}>
            {trackerStages.map((stage, i) => {
              const isDone = i < currentStageIndex;
              const isCurrent = i === currentStageIndex;

              return (
                <div className="status-stage" key={stage.key}>
                  <div
                    className={`stage-icon ${isDone ? 'done' : isCurrent ? 'current' : ''}`}
                    style={{
                      background: isDone ? '#E7FAF2' : isCurrent ? '#0B192C' : '#EDF0F4',
                      color: isDone ? '#059669' : isCurrent ? '#FFFFFF' : '#64748B',
                    }}
                  >
                    {isDone ? <CheckCircle2 size={17} /> : isCurrent ? <Clock3 size={17} /> : <span>{i + 1}</span>}
                  </div>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <strong style={{ color: isCurrent ? '#0B192C' : isDone ? '#059669' : '#64748B' }}>
                        {stage.title}
                      </strong>
                      <span style={{ fontSize: '10px', color: '#94A3B8' }}>/ {stage.hindi}</span>
                    </div>

                    <span style={{ fontSize: '11px', color: '#64748B', marginTop: '2px' }}>
                      {stage.desc}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="info-box" style={{ marginTop: '20px' }}>
            <ShieldCheck size={18} style={{ color: '#059669', flexShrink: 0 }} />
            <div>
              <strong>Audit Compliance Guarantee</strong>
              <p>
                CredSaathi does not invent state transitions or guarantee loan approvals. All status updates accurately reflect lender underwriting actions.
              </p>
            </div>
          </div>
        </Card>

        {/* RIGHT COLUMN: APPLICATION PACKET SUMMARY & AUDIT LOG */}
        <aside>
          <Card>
            <CardHeader title="Application Summary" />

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '12px' }}>
              <div className="row-between" style={{ borderBottom: '1px solid #EDF0F4', paddingBottom: '8px' }}>
                <span style={{ color: '#64748B' }}>Application ID:</span>
                <strong>{appId}</strong>
              </div>

              <div className="row-between" style={{ borderBottom: '1px solid #EDF0F4', paddingBottom: '8px' }}>
                <span style={{ color: '#64748B' }}>Loan Scheme:</span>
                <strong>{appData.schemeName}</strong>
              </div>

              <div className="row-between" style={{ borderBottom: '1px solid #EDF0F4', paddingBottom: '8px' }}>
                <span style={{ color: '#64748B' }}>Requested Amount:</span>
                <strong className="money" style={{ color: '#0B192C' }}>{appData.amountLabel}</strong>
              </div>

              <div className="row-between" style={{ borderBottom: '1px solid #EDF0F4', paddingBottom: '8px' }}>
                <span style={{ color: '#64748B' }}>Submission Date:</span>
                <span>{appData.submittedAt}</span>
              </div>

              <div className="row-between">
                <span style={{ color: '#64748B' }}>Target Lender:</span>
                <span>State Bank of India</span>
              </div>
            </div>

            <div style={{ marginTop: '18px', paddingTop: '14px', borderTop: '1px solid #E2E8F0' }}>
              <Link className="btn btn-secondary full" to="/applicant/documents">
                <FileText size={16} /> View Attached Documents
              </Link>
            </div>
          </Card>

          <Card>
            <h3 className="side-title" style={{ fontSize: '15px', margin: '0 0 8px', color: '#0B192C' }}>
              Audit History Log
            </h3>
            <p className="muted" style={{ fontSize: '11px', lineHeight: '17px', margin: '0 0 12px' }}>
              Every status transition is logged by the backend audit engine.
            </p>

            <div className="history">
              <div><b>07 Oct</b><span>Application Packet Created</span></div>
              <div><b>07 Oct</b><span>Submitted to State Bank of India</span></div>
              <div><b>08 Oct</b><span>Under Review by Credit Desk</span></div>
            </div>
          </Card>
        </aside>
      </div>
    </>
  );
}
