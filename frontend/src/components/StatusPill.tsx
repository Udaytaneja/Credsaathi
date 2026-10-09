import Badge from './Badge';

export interface StatusPillProps {
  status: string;
  className?: string;
}

export default function StatusPill({ status, className = '' }: StatusPillProps) {
  const upper = (status || '').toUpperCase();
  
  let tone: 'success' | 'danger' | 'warning' | 'neutral' | 'navy' = 'neutral';
  
  if (upper.includes('ACCEPT') || upper.includes('APPROVED') || upper === 'VALID' || upper === 'VERIFIED') {
    tone = 'success';
  } else if (upper.includes('REJECT') || upper === 'FAILED' || upper === 'CLOSED') {
    tone = 'danger';
  } else if (upper.includes('REVIEW') || upper.includes('PROCESS') || upper.includes('REQUIRED') || upper === 'UPLOADING') {
    tone = 'warning';
  } else if (upper === 'SUBMITTED' || upper === 'DRAFT') {
    tone = 'navy';
  }

  const label = upper
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/(^|\s)\w/g, (m) => m.toUpperCase());

  return <Badge tone={tone} className={className}>{label}</Badge>;
}
