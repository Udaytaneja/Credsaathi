import { api } from './api/client';
import { mockApi } from './mock';
import type { LoanScenarioRequest } from '../types';

const demo = import.meta.env.VITE_DEMO_MODE === 'true';

export const services = {
  async login(email: string, password: string) {
    if (demo) return mockApi.login(email);
    return api.login({ email, password });
  },
  async register(name: string, email: string, password: string, role?: string) {
    if (demo) return mockApi.register(name, email);
    return api.register({ name, email, password, role });
  },
  async schemes(search = '') {
    if (demo) return mockApi.schemes(search);
    return api.schemes(search);
  },
  async applications() {
    if (demo) return mockApi.applications();
    return api.applications();
  },
  async bankerApplications(search = '') {
    if (demo) return mockApi.bankerApplications(search);
    return api.bankerApplications(search);
  },
  async bankerCustomers(search = '') {
    if (demo) return mockApi.bankerCustomers(search);
    return api.bankerCustomers(search);
  },
  async bankerReports() {
    if (demo) return mockApi.bankerReports();
    return api.bankerReports();
  },
  async documents() {
    if (demo) return mockApi.documents();
    return api.documents();
  },
  async financialSnapshot() {
    if (demo) return mockApi.financialSnapshot();
    return api.financialSnapshot();
  },
  async loanScenario(req: LoanScenarioRequest) {
    if (demo) return mockApi.loanScenario(req);
    return api.loanScenario(req);
  },
  async assistant(message: string, applicationId?: string) {
    if (demo) return mockApi.assistant(message);
    return api.assistant({ message, applicationId });
  },
  async notifications() {
    if (demo) return mockApi.notifications();
    return api.notifications();
  },
  async markNotificationRead(id: string) {
    if (demo) return mockApi.markNotificationRead(id);
    return api.markNotificationRead(id);
  },
  async settings() {
    if (demo) return mockApi.settings();
    return api.settings();
  },
  async updateConsent(consentId: string, active: boolean) {
    if (demo) return mockApi.updateConsent(consentId, active);
    return api.updateConsent(consentId, active);
  },
};
