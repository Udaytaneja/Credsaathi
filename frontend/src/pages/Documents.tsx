import React, { useState, useEffect } from 'react';
import { 
  FileUp, 
  RefreshCw, 
  ShieldCheck, 
  AlertCircle, 
  CheckCircle2, 
  Clock, 
  FileText, 
  Upload, 
  X, 
  Trash2, 
  Filter
} from 'lucide-react';
import PageTitle from '../components/PageTitle';
import { Card, CardHeader } from '../components/Card';
import StatusPill from '../components/StatusPill';
import Badge from '../components/Badge';
import { services } from '../services';
import type { DocumentItem, DocumentStatus } from '../types';

export default function Documents() {
  const [docList, setDocList] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('ALL');
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('Identity');
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    let mounted = true;
    async function loadDocs() {
      try {
        setLoading(true);
        const data = (await services.documents()) as DocumentItem[];
        if (mounted) {
          setDocList(data);
        }
      } catch (err) {
        console.error('Failed to load documents:', err);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    loadDocs();
    return () => { mounted = false; };
  }, []);

  const MAX_FILE_SIZE = 10 * 1024 * 1024;
  const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setValidationError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setValidationError('Invalid file type. Only PDF, JPG, JPEG, and PNG documents are supported.');
      setSelectedFile(null);
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setValidationError(`File size exceeds 10MB limit (${(file.size / (1024 * 1024)).toFixed(1)}MB). Please upload a smaller file.`);
      setSelectedFile(null);
      return;
    }

    const isDuplicate = docList.some(d => d.name.toLowerCase() === file.name.toLowerCase());
    if (isDuplicate) {
      setValidationError('A document with this exact filename is already uploaded. You can re-upload or select a unique name.');
    }

    setSelectedFile(file);
  };

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setValidationError('Please select a file to upload.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(15);

    const tempId = `doc-${Date.now()}`;
    const newDoc: DocumentItem = {
      id: tempId,
      name: selectedFile.name,
      type: docType,
      size: `${(selectedFile.size / 1024).toFixed(0)} KB`,
      status: 'UPLOADING',
      updatedAt: 'Just now'
    };

    setDocList(prev => [newDoc, ...prev]);

    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 25;
      });
    }, 300);

    setTimeout(() => {
      clearInterval(progressInterval);
      setUploadProgress(100);

      setDocList(prev => prev.map(d => d.id === tempId ? { ...d, status: 'PROCESSING' } : d));
      setIsUploading(false);
      setIsModalOpen(false);
      setSelectedFile(null);
      setUploadProgress(0);

      setTimeout(() => {
        setDocList(prev => prev.map(d => {
          if (d.id === tempId) {
            const nextStatus: DocumentStatus = Math.random() > 0.3 ? 'VALID' : 'NEEDS_REVIEW';
            return { ...d, status: nextStatus, updatedAt: 'Just now' };
          }
          return d;
        }));
      }, 3500);

    }, 1800);
  };

  const handleRetry = (id: string) => {
    setDocList(prev => prev.map(d => {
      if (d.id === id) {
        return { ...d, status: 'PROCESSING', updatedAt: 'Retrying now' };
      }
      return d;
    }));

    setTimeout(() => {
      setDocList(prev => prev.map(d => {
        if (d.id === id) {
          return { ...d, status: 'VALID', updatedAt: 'Just now' };
        }
        return d;
      }));
    }, 2500);
  };

  const handleDelete = (id: string) => {
    setDocList(prev => prev.filter(d => d.id !== id));
  };

  const filteredDocs = docList.filter(d => {
    if (filter === 'ALL') return true;
    return d.status === filter;
  });

  const getDocStyle = (status: DocumentStatus) => {
    if (status === 'NEEDS_REVIEW') {
      return { bg: '#FFFBEB', iconBg: 'var(--amber-soft)', iconColor: 'var(--amber)' };
    }
    if (status === 'FAILED') {
      return { bg: '#FEF2F2', iconBg: 'var(--red-soft)', iconColor: 'var(--red)' };
    }
    if (status === 'VALID') {
      return { bg: 'var(--white)', iconBg: 'var(--green-soft)', iconColor: 'var(--green)' };
    }
    return { bg: 'var(--white)', iconBg: 'var(--blue-soft)', iconColor: 'var(--navy)' };
  };

  return (
    <>
      <PageTitle
        eyebrow="DOCUMENT VAULT"
        title="Secure Document Workspace"
        subtitle="Manage required business and identity verification documents. Protected with backend-authorized access controls."
        action={
          <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
            <FileUp size={16} /> Upload New Document
          </button>
        }
      />

      <div className="card" style={{ background: '#EFF6FF', borderColor: '#BFDBFE', padding: '14px 18px', marginBottom: '22px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', color: '#1E40AF', fontSize: '12px', lineHeight: '19px' }}>
          <ShieldCheck size={20} style={{ color: '#2563EB', flexShrink: 0, marginTop: '1px' }} />
          <div>
            <strong style={{ display: 'block', fontSize: '13px', color: '#1E3A8A', marginBottom: '2px' }}>
              Backend-Authorized Access and Audit Logging Active
            </strong>
            Documents uploaded to the CredSaathi vault are never exposed via permanent public URLs or query parameters. Document access requires time-bound, backend-authorized tokens and every access request is audited.
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 0.9fr', gap: '22px' }}>
        <div>
          <Card>
            <CardHeader
              title="Vault Documents"
              subtitle="View status, review requirements, and validation lifecycle for uploaded files."
              action={
                <div className="flex gap-2 items-center">
                  <Filter size={14} />
                  <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="text-xs font-semibold rounded p-1 border"
                  >
                    <option value="ALL">All Statuses ({docList.length})</option>
                    <option value="VALID">Valid</option>
                    <option value="PROCESSING">Processing</option>
                    <option value="NEEDS_REVIEW">Needs Review</option>
                    <option value="FAILED">Failed</option>
                    <option value="UPLOADING">Uploading</option>
                  </select>
                </div>
              }
            />

            {loading && (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)' }}>
                <RefreshCw size={24} className="spin" style={{ marginBottom: '8px' }} />
                <p style={{ margin: 0, fontSize: '13px' }}>Loading document vault...</p>
              </div>
            )}

            {!loading && filteredDocs.length === 0 && (
              <div className="empty-state" style={{ padding: '50px 20px' }}>
                <FileText size={40} style={{ opacity: 0.4 }} />
                <h3>No documents found</h3>
                <p>
                  {filter === 'ALL'
                    ? 'Your vault is currently empty. Upload required identity and business documents to prepare scheme applications.'
                    : `No documents matching status "${filter}".`}
                </p>
                <button
                  className="btn btn-secondary"
                  style={{ marginTop: '16px' }}
                  onClick={() => setIsModalOpen(true)}
                >
                  <FileUp size={15} /> Upload Document
                </button>
              </div>
            )}

            {!loading && filteredDocs.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {filteredDocs.map((doc) => {
                  const styleInfo = getDocStyle(doc.status);

                  return (
                    <div
                      key={doc.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '14px 16px',
                        border: '1px solid var(--line)',
                        borderRadius: '10px',
                        background: styleInfo.bg,
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flex: 1, minWidth: 0 }}>
                        <div
                          style={{
                            width: '40px',
                            height: '40px',
                            borderRadius: '8px',
                            background: styleInfo.iconBg,
                            color: styleInfo.iconColor,
                            display: 'grid',
                            placeItems: 'center',
                            flexShrink: 0
                          }}
                        >
                          {doc.status === 'PROCESSING' ? (
                            <RefreshCw size={18} className="spin" />
                          ) : doc.status === 'VALID' ? (
                            <CheckCircle2 size={18} />
                          ) : doc.status === 'FAILED' ? (
                            <AlertCircle size={18} />
                          ) : (
                            <FileText size={18} />
                          )}
                        </div>

                        <div style={{ minWidth: 0, flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <strong style={{
                              fontSize: '13px',
                              color: 'var(--navy)',
                              whiteSpace: 'nowrap',
                              overflow: 'hidden',
                              textOverflow: 'ellipsis'
                            }}>
                              {doc.name}
                            </strong>
                          </div>
                          <div style={{ display: 'flex', gap: '12px', fontSize: '11px', color: 'var(--muted)', marginTop: '3px' }}>
                            <span>Type: <strong>{doc.type}</strong></span>
                            <span>•</span>
                            <span>Format: <strong>{doc.size}</strong></span>
                            <span>•</span>
                            <span>Updated: <strong>{doc.updatedAt}</strong></span>
                          </div>

                          {doc.status === 'PROCESSING' && (
                            <div style={{ fontSize: '11px', color: 'var(--amber)', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <Clock size={12} /> Extracting document parameters and verifying statutory metadata...
                            </div>
                          )}
                          {doc.status === 'NEEDS_REVIEW' && (
                            <div style={{ fontSize: '11px', color: '#B45309', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <AlertCircle size={12} /> Flagged for human officer review - clarity check pending.
                            </div>
                          )}
                          {doc.status === 'FAILED' && (
                            <div style={{ fontSize: '11px', color: 'var(--red)', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <AlertCircle size={12} /> Automated validation failed. Please upload a clear document image/PDF.
                            </div>
                          )}
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginLeft: '14px', flexShrink: 0 }}>
                        <StatusPill status={doc.status} />

                        {doc.status === 'FAILED' && (
                          <button
                            className="btn btn-secondary"
                            style={{ padding: '4px 10px', fontSize: '11px', height: '30px' }}
                            onClick={() => handleRetry(doc.id)}
                            title="Retry extraction pipeline"
                          >
                            <RefreshCw size={12} /> Retry
                          </button>
                        )}

                        <button
                          className="icon-btn"
                          onClick={() => handleDelete(doc.id)}
                          title="Remove document from local vault"
                          aria-label="Delete document"
                        >
                          <Trash2 size={15} style={{ color: 'var(--muted)' }} />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader
              title="Vault Readiness"
              subtitle="Document readiness for scheme application submission."
            />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px 14px',
                background: '#F8FAFC',
                borderRadius: '8px',
                border: '1px solid var(--line)'
              }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--navy)' }}>
                  Identity Proof (Aadhaar/PAN)
                </span>
                {docList.some(d => d.type === 'Identity' && d.status === 'VALID') ? (
                  <Badge tone="success">READY</Badge>
                ) : (
                  <Badge tone="warning">PENDING</Badge>
                )}
              </div>

              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px 14px',
                background: '#F8FAFC',
                borderRadius: '8px',
                border: '1px solid var(--line)'
              }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--navy)' }}>
                  Financial Statements (6m Bank)
                </span>
                {docList.some(d => d.type === 'Financial' && d.status === 'VALID') ? (
                  <Badge tone="success">READY</Badge>
                ) : docList.some(d => d.type === 'Financial' && d.status === 'PROCESSING') ? (
                  <Badge tone="warning">PROCESSING</Badge>
                ) : (
                  <Badge tone="danger">MISSING</Badge>
                )}
              </div>

              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px 14px',
                background: '#F8FAFC',
                borderRadius: '8px',
                border: '1px solid var(--line)'
              }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--navy)' }}>
                  Business Registration (Udyam)
                </span>
                {docList.some(d => d.type === 'Business' && d.status === 'VALID') ? (
                  <Badge tone="success">READY</Badge>
                ) : (
                  <Badge tone="warning">REVIEW NEEDED</Badge>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <CardHeader
              title="Secure Access Controls"
              subtitle="Data privacy and statutory compliance summary."
            />
            <ul style={{
              margin: 0,
              paddingLeft: '18px',
              fontSize: '12px',
              lineHeight: '20px',
              color: 'var(--muted)'
            }}>
              <li style={{ marginBottom: '8px' }}>
                <strong>No Public URLs:</strong> File blobs are stored securely and never given static URL endpoints.
              </li>
              <li style={{ marginBottom: '8px' }}>
                <strong>Encrypted at Rest:</strong> AES-256 encryption applied before backend vault storage.
              </li>
              <li style={{ marginBottom: '8px' }}>
                <strong>Strict Sanitization:</strong> File names, headers, and metadata are sanitized to prevent injection vulnerabilities.
              </li>
              <li>
                <strong>Audit Compliance:</strong> All officer view requests trigger timestamped access logs.
              </li>
            </ul>
          </Card>
        </div>
      </div>

      {isModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(11, 25, 44, 0.5)',
          display: 'grid',
          placeItems: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div style={{
            background: 'var(--white)',
            width: 'min(500px, 100%)',
            borderRadius: '16px',
            padding: '28px',
            boxShadow: 'var(--shadow-modal)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
              <h3 style={{ margin: 0, fontSize: '18px', color: 'var(--navy)' }}>Upload Document</h3>
              <button
                className="icon-btn"
                onClick={() => {
                  if (!isUploading) {
                    setIsModalOpen(false);
                    setValidationError(null);
                    setSelectedFile(null);
                  }
                }}
                disabled={isUploading}
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit}>
              <div className="field" style={{ marginBottom: '16px' }}>
                <label>Document Category <em>*</em></label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  disabled={isUploading}
                >
                  <option value="Identity">Identity Proof (Aadhaar, PAN, Passport)</option>
                  <option value="Financial">Financial Statement (Bank Statement, ITR, GST)</option>
                  <option value="Business">Business Registration (Udyam, GSTIN, Shop License)</option>
                  <option value="Project">Project Report / Quotation</option>
                </select>
              </div>

              <div
                style={{
                  border: '2px dashed var(--border-action)',
                  borderRadius: '12px',
                  padding: '24px',
                  textAlign: 'center',
                  background: '#F8FAFC',
                  marginBottom: '16px',
                  cursor: isUploading ? 'not-allowed' : 'pointer'
                }}
                onClick={() => {
                  if (!isUploading) {
                    document.getElementById('modal-file-input')?.click();
                  }
                }}
              >
                <Upload size={32} style={{ color: 'var(--muted)', marginBottom: '8px' }} />
                <p style={{ margin: '0 0 4px', fontSize: '13px', fontWeight: 600, color: 'var(--navy)' }}>
                  {selectedFile ? selectedFile.name : 'Click or drop document file here'}
                </p>
                <p style={{ margin: 0, fontSize: '11px', color: 'var(--muted)' }}>
                  {selectedFile
                    ? `${(selectedFile.size / 1024).toFixed(0)} KB - ${selectedFile.type}`
                    : 'Supported formats: PDF, JPG, JPEG, PNG (Max size: 10MB)'}
                </p>
                <input
                  id="modal-file-input"
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={handleFileSelect}
                  style={{ display: 'none' }}
                  disabled={isUploading}
                />
              </div>

              {validationError && (
                <div style={{
                  padding: '10px 12px',
                  background: '#FEF2F2',
                  border: '1px solid #FECDD3',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: 'var(--red)',
                  marginBottom: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <AlertCircle size={16} style={{ flexShrink: 0 }} />
                  <span>{validationError}</span>
                </div>
              )}

              {isUploading && (
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--muted)', marginBottom: '4px' }}>
                    <span>Encrypting & Uploading...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div style={{ width: '100%', height: '6px', background: '#E2E8F0', borderRadius: '3px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${uploadProgress}%`,
                        height: '100%',
                        background: 'var(--navy)',
                        transition: 'width 0.2s ease'
                      }}
                    />
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', marginTop: '20px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setIsModalOpen(false)}
                  disabled={isUploading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={!selectedFile || isUploading}
                >
                  {isUploading ? (
                    <>
                      <RefreshCw size={14} className="spin" /> Uploading...
                    </>
                  ) : (
                    'Confirm & Upload'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
