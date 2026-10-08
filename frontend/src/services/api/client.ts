const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
export class ApiError extends Error { constructor(public status:number, message:string, public code?:string){ super(message); } }
export async function apiRequest<T>(path:string, init:RequestInit={}) : Promise<T> {
  const res=await fetch(`${BASE_URL}${path}`, { ...init, headers:{ 'Content-Type':'application/json', ...(init.headers||{}) }, credentials:'include' });
  if(!res.ok){ let body: Record<string, string> | null = null; try { body = await res.json(); } catch { /* ignore JSON parse error */ } throw new ApiError(res.status, body?.message || 'Something went wrong. Please try again.', body?.code); }
  return res.status===204 ? (undefined as T) : res.json();
}
export const api = {
  login:(payload:unknown)=>apiRequest('/auth/login',{method:'POST',body:JSON.stringify(payload)}),
  register:(payload:unknown)=>apiRequest('/auth/register',{method:'POST',body:JSON.stringify(payload)}),
  schemes:(query='')=>apiRequest(`/schemes?search=${encodeURIComponent(query)}`),
  applications:()=>apiRequest('/applications'),
  bankerApplications:(query='')=>apiRequest(`/banker/applications?search=${encodeURIComponent(query)}`),
  bankerCustomers:(query='')=>apiRequest(`/banker/customers?search=${encodeURIComponent(query)}`),
  bankerReports:()=>apiRequest('/banker/reports'),
  documents:()=>apiRequest('/documents'),
  financialSnapshot:()=>apiRequest('/financial/snapshot'),
  loanScenario:(payload:unknown)=>apiRequest('/financial/loan-scenarios',{method:'POST',body:JSON.stringify(payload)}),
  assistant:(payload:unknown)=>apiRequest('/ai/assistant/query',{method:'POST',body:JSON.stringify(payload)}),
  notifications:()=>apiRequest('/notifications'),
  markNotificationRead:(id:string)=>apiRequest(`/notifications/${id}/read`,{method:'PATCH'}),
  settings:()=>apiRequest('/applicant/settings'),
  updateConsent:(consentId:string, active:boolean)=>apiRequest(`/applicant/consents/${consentId}`,{method:'PATCH',body:JSON.stringify({active})})
};
