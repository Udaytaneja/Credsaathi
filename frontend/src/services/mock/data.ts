import type { Application, DocumentItem, FinancialSnapshot, Scheme, NotificationItem, UserSettings, BankerCustomer, BankerReportMetrics } from '../../types';

export const schemes: Scheme[] = [
 {id:'pmegp',name:"PMEGP: Prime Minister's Employment Generation Programme",purpose:'Business setup and expansion',description:'Indicative credit-linked support for eligible new micro enterprises. Verify current guidelines and lender terms before applying.',matchLabel:'Illustrative criteria match',reasons:['Manufacturing or service activity aligns with the stated purpose.','Applicant profile contains a business capital requirement.','Location and enterprise details can be reviewed against official criteria.','Final terms remain subject to lender and scheme guidelines.'],documents:['Identity document','Address proof','Business/project information'],source:'Official scheme source — verify before relying on this information',lastVerified:'Demo record — connect verified source',status:'Indicative information'},
 {id:'sidbi-4e',name:'SIDBI 4E — End-to-End Energy Efficiency',purpose:'Energy-efficiency upgrades',description:'Indicative financing information for eligible efficiency improvements. Current terms must be verified with the official programme/lender.',matchLabel:'Potential relevance',reasons:['Energy-related expenditure is present in the applicant context.','Proposed equipment can be reviewed for efficiency relevance.'],documents:['Business proof','Equipment quotation','Financial statements'],source:'Official programme source — verify before relying on this information',lastVerified:'Demo record — connect verified source',status:'Indicative information'},
 {id:'mudra',name:'Pradhan Mantri MUDRA Yojana',purpose:'Micro-enterprise financing',description:'Indicative scheme information for eligible micro-enterprise needs. Availability and terms depend on official guidelines and lender discretion.',matchLabel:'Potential relevance',reasons:['Loan purpose can fit micro-enterprise working capital or business needs.','Application can be prepared progressively.'],documents:['Identity document','Address proof','Business details'],source:'Official scheme source — verify before relying on this information',lastVerified:'Demo record — connect verified source',status:'Indicative information'}
];

export const applications: Application[] = [
  {
    id: 'CS-2026-0018',
    customerName: 'Aarohi Sharma',
    enterpriseName: 'Aarohi Precision Engineering & Energy Pvt Ltd',
    schemeName: 'PMEGP',
    amountLabel: '₹25,00,000',
    submittedAt: '07 Oct 2026',
    status: 'UNDER_REVIEW',
    updatedAt: 'Today',
    documentsCount: 4,
    readinessScore: '92%',
    authorizedOrganization: 'State Bank of India — SME Branch'
  },
  {
    id: 'CS-2026-0011',
    customerName: 'Rohan Kulkarni',
    enterpriseName: 'Kulkarni Renewable Components',
    schemeName: 'SIDBI 4E',
    amountLabel: '₹12,00,000',
    submittedAt: '30 Sep 2026',
    status: 'ADDITIONAL_INFO_REQUIRED',
    updatedAt: '2 days ago',
    documentsCount: 3,
    readinessScore: '78%',
    authorizedOrganization: 'State Bank of India — SME Branch'
  },
  {
    id: 'CS-2026-0009',
    customerName: 'Meera Sen',
    enterpriseName: 'Sen Textile Crafts Enterprise',
    schemeName: 'MUDRA',
    amountLabel: '₹8,00,000',
    submittedAt: '25 Sep 2026',
    status: 'SUBMITTED',
    updatedAt: '4 days ago',
    documentsCount: 3,
    readinessScore: '85%',
    authorizedOrganization: 'State Bank of India — SME Branch'
  }
];

export const bankerCustomers: BankerCustomer[] = [
  {
    id: 'CS-CUST-018',
    name: 'Aarohi Sharma',
    enterpriseName: 'Aarohi Precision Engineering & Energy Pvt Ltd',
    udyamNo: 'UDYAM-MH-12-0049281',
    activeApplicationsCount: 2,
    lastActivity: 'Today at 10:30 AM',
    contactEmail: 'aarohi.sharma@credsaathi.example',
    contactPhone: '+91 98765 43210',
    riskCategory: 'LOW',
    verificationStatus: 'VERIFIED'
  },
  {
    id: 'CS-CUST-011',
    name: 'Rohan Kulkarni',
    enterpriseName: 'Kulkarni Renewable Components',
    udyamNo: 'UDYAM-MH-14-0091823',
    activeApplicationsCount: 1,
    lastActivity: 'Yesterday',
    contactEmail: 'rohan.kulkarni@example.com',
    contactPhone: '+91 98123 45678',
    riskCategory: 'LOW',
    verificationStatus: 'VERIFIED'
  },
  {
    id: 'CS-CUST-009',
    name: 'Meera Sen',
    enterpriseName: 'Sen Textile Crafts Enterprise',
    udyamNo: 'UDYAM-WB-03-0012948',
    activeApplicationsCount: 1,
    lastActivity: '4 days ago',
    contactEmail: 'meera.sen@example.com',
    contactPhone: '+91 97654 32109',
    riskCategory: 'MODERATE',
    verificationStatus: 'VERIFIED'
  }
];

export const bankerReportMetrics: BankerReportMetrics = {
  totalSubmitted: 11,
  underReview: 8,
  additionalInfoRequired: 5,
  closed: 19,
  pipelineBreakdown: [
    { label: 'Submitted & Pending Initial Review', percentage: '25%', count: 11 },
    { label: 'Under Detailed Verification', percentage: '18%', count: 8 },
    { label: 'Additional Information Requested', percentage: '11%', count: 5 },
    { label: 'Sanctioned / Formally Closed', percentage: '43%', count: 19 }
  ],
  authorizedOrganization: 'State Bank of India — SME Branch',
  lastUpdated: '08 Oct 2026, 22:30 IST',
  disclaimer: 'Operational analytics represent organization-scoped application pipeline metrics. Official credit decisioning and underwriting remains within core banking ledger systems.'
};

export const documents: DocumentItem[] = [
  {id:'1',name:'Aadhaar / Identity proof',type:'Identity',size:'PDF',status:'VALID',updatedAt:'Today'},
  {id:'2',name:'Bank statement — last 6 months',type:'Financial',size:'PDF',status:'PROCESSING',updatedAt:'Today'},
  {id:'3',name:'Business registration',type:'Business',size:'PDF',status:'NEEDS_REVIEW',updatedAt:'Yesterday'}
];

export const financial: FinancialSnapshot = {
  monthlyIncome:'₹1,80,000',
  monthlyExpenses:'₹92,000',
  existingDebt:'₹24,000 / month',
  remainingCashFlow:'₹64,000',
  sourceNote:'Illustrative demo values. Official financial metrics must come from the backend financial engine.'
};

export const notifications: NotificationItem[] = [
  {
    id: 'n1',
    category: 'ADDITIONAL_DOCUMENTS',
    title: 'Additional Document Required: GST Return Q3',
    message: 'Underwriting desk requested updated GST returns for SIDBI 4E application CS-2026-0011.',
    timestamp: 'Today at 10:30 AM',
    isRead: false,
    actionUrl: '/applicant/documents',
    actionLabel: 'Upload Document'
  },
  {
    id: 'n2',
    category: 'APPLICATION_TRANSMISSION',
    title: 'Application Transmitted to State Bank of India',
    message: 'Your PMEGP application CS-2026-0018 was successfully routed to State Bank of India, SME Branch.',
    timestamp: '07 Oct 2026',
    isRead: false,
    actionUrl: '/applicant/applications/CS-2026-0018',
    actionLabel: 'View Status'
  },
  {
    id: 'n3',
    category: 'DOCUMENT_UPLOAD_CONFIRMATION',
    title: 'Identity Verification Completed',
    message: 'Aadhaar / Identity proof document has passed automated structural validity checks.',
    timestamp: '06 Oct 2026',
    isRead: true,
    actionUrl: '/applicant/documents',
    actionLabel: 'View Vault'
  },
  {
    id: 'n4',
    category: 'SCHEME_POLICY_INFO',
    title: 'PMEGP Subsidy Rate Revision Notice',
    message: 'Ministry of MSME published updated subsidy allocation norms for rural general enterprise applicants.',
    timestamp: '04 Oct 2026',
    isRead: true,
    actionUrl: '/applicant/schemes/pmegp',
    actionLabel: 'View Scheme'
  }
];

export const settingsData: UserSettings = {
  applicantName: 'Aarohi Sharma',
  entityName: 'Aarohi Precision Engineering & Energy Pvt Ltd',
  udyamRegistrationNo: 'UDYAM-MH-12-0049281',
  email: 'aarohi.sharma@credsaathi.example',
  phone: '+91 98765 43210',
  verifiedCredentials: {
    identityVerified: true,
    businessVerified: true,
    financialsVerified: true
  },
  consentLenderSharing: true,
  consentProductAnalytics: false,
  language: 'en',
  activeConsents: [
    {
      id: 'c-001',
      title: 'Explicit Lender Data Transmission Consent',
      purpose: 'Authorizes CredSaathi to securely package and transmit applicant business profile and vault documents to participating public sector lenders.',
      grantedAt: '07 Oct 2026, 14:22 IST',
      status: 'ACTIVE',
      scope: ['Business Identity', 'Financial Statements', 'Document Vault']
    },
    {
      id: 'c-002',
      title: 'Automated Document Verification Authorization',
      purpose: 'Authorizes automated structural validation and OCR checksum verification of uploaded GST and Udyam certificates.',
      grantedAt: '01 Oct 2026, 09:15 IST',
      status: 'ACTIVE',
      scope: ['Document Vault Metadata', 'Udyam Checksum']
    }
  ]
};
