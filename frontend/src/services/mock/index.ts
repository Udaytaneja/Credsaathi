import { applications, documents, financial, schemes, notifications, settingsData, bankerCustomers, bankerReportMetrics } from './data';
import type { UserSession, LoanScenarioRequest, LoanScenarioResponse, NotificationItem, UserSettings, BankerCustomer, BankerReportMetrics } from '../../types';

export const mockApi = {
  async login(email: string): Promise<UserSession> {
    return { id: 'demo-user', name: 'Aarohi Demo', email, role: 'APPLICANT' };
  },
  async register(name: string, email: string): Promise<UserSession> {
    return { id: 'demo-user', name, email, role: 'APPLICANT' };
  },
  async schemes(search = '') {
    return schemes.filter(s => `${s.name} ${s.purpose}`.toLowerCase().includes(search.toLowerCase()));
  },
  async applications() {
    return applications;
  },
  async bankerApplications(search = '') {
    return applications.filter(a => 
      `${a.id} ${a.customerName} ${a.enterpriseName} ${a.schemeName}`.toLowerCase().includes(search.toLowerCase())
    );
  },
  async bankerCustomers(search = ''): Promise<BankerCustomer[]> {
    return bankerCustomers.filter(c =>
      `${c.name} ${c.enterpriseName} ${c.id} ${c.udyamNo}`.toLowerCase().includes(search.toLowerCase())
    );
  },
  async bankerReports(): Promise<BankerReportMetrics> {
    return bankerReportMetrics;
  },
  async documents() {
    return documents;
  },
  async financialSnapshot() {
    return {
      ...financial,
      assets: '₹42,50,000',
      liabilities: '₹14,20,000',
      debtServiceCoverageRatio: '2.67x (Healthy DSCR)',
      trendLabel: '+8.4% Revenue Growth (YoY)',
      verificationStatus: 'SELF_DECLARED' as const
    };
  },
  async loanScenario(req: LoanScenarioRequest): Promise<LoanScenarioResponse> {
    const P = req.amount * 100000;
    const N = req.tenureYears * 12;
    const R = (req.interestRate || 10.5) / 12 / 100;
    
    // Server-side calculation encapsulated strictly in mock service
    const emi = Math.round((P * R * Math.pow(1 + R, N)) / (Math.pow(1 + R, N) - 1));
    const totalPayment = emi * N;
    const totalInterest = totalPayment - P;
    
    const monthlyInc = 180000;
    const existingDebtVal = 24000;
    const newTotalDebt = existingDebtVal + emi;
    const remainingCash = monthlyInc - 92000 - newTotalDebt;
    const impactPct = Math.min(100, Math.round((newTotalTotalDebt(existingDebtVal, emi) / monthlyInc) * 100));

    // Simple amortization table per year
    const breakdown = [];
    let balance = P;
    for (let yr = 1; yr <= req.tenureYears; yr++) {
      let yrInterest = 0;
      let yrPrincipal = 0;
      for (let m = 1; m <= 12; m++) {
        const mInterest = balance * R;
        const mPrincipal = emi - mInterest;
        yrInterest += mInterest;
        yrPrincipal += mPrincipal;
        balance = Math.max(0, balance - mPrincipal);
      }
      breakdown.push({
        year: yr,
        principalPaid: `₹${Math.round(yrPrincipal).toLocaleString('en-IN')}`,
        interestPaid: `₹${Math.round(yrInterest).toLocaleString('en-IN')}`,
        balanceRemaining: `₹${Math.round(balance).toLocaleString('en-IN')}`
      });
    }

    return {
      emiLabel: `₹${emi.toLocaleString('en-IN')} / month`,
      totalRepaymentLabel: `₹${totalPayment.toLocaleString('en-IN')}`,
      totalInterestLabel: `₹${totalInterest.toLocaleString('en-IN')}`,
      monthlyDebtObligationsLabel: `₹${newTotalDebt.toLocaleString('en-IN')} / month`,
      remainingCashFlowPostEmiLabel: `₹${remainingCash.toLocaleString('en-IN')}`,
      cashFlowImpactPercentage: `${impactPct}%`,
      interestRateApplied: `${(req.interestRate || 10.5).toFixed(1)}% p.a. (Indicative)`,
      amortizationBreakdown: breakdown,
      disclaimer: 'Official interest rates, processing fees, and EMI schedules are subject to final bank underwriting.'
    };
  },
  async assistant(message: string) {
    return {
      answer: `Demo assistant response for: “${message}”. Connect Uday’s /ai/assistant/query endpoint before production use.`,
      sources: ['CredSaathi demo context'],
      confidence: 'Demo',
      humanReviewRequired: false
    };
  },
  async notifications(): Promise<NotificationItem[]> {
    return notifications;
  },
  async markNotificationRead(id: string): Promise<{ success: boolean }> {
    const item = notifications.find(n => n.id === id);
    if (item) item.isRead = true;
    return { success: true };
  },
  async settings(): Promise<UserSettings> {
    return settingsData;
  },
  async updateConsent(consentId: string, active: boolean): Promise<{ success: boolean }> {
    const consent = settingsData.activeConsents.find(c => c.id === consentId);
    if (consent) {
      consent.status = active ? 'ACTIVE' : 'REVOKED';
    }
    return { success: true };
  }
};

function newTotalTotalDebt(existing: number, emi: number) {
  return existing + emi;
}
