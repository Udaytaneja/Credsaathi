import type { UserSession } from '../types';
const KEY = 'credsaathi.session';

export function getSession(): UserSession | null { 
  try { 
    if (typeof localStorage === 'undefined') return null;
    const raw = localStorage.getItem(KEY); 
    return raw ? JSON.parse(raw) : null; 
  } catch { 
    return null; 
  } 
}

export function setSession(session: UserSession) { 
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(KEY, JSON.stringify(session)); 
    }
  } catch {
    // Ignore storage quota errors in SSR environment
  }
}

export function clearSession() { 
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(KEY); 
    }
  } catch {
    // Ignore storage errors
  }
}
