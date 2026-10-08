import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
const resources = {
  en: { translation: { brand: 'CredSaathi', dashboard: 'Dashboard', schemes: 'Scheme Discovery', applications: 'Applications', documents: 'Documents', financial: 'Financial Snapshot', assistant: 'AI Assistant', settings: 'Settings', profile: 'Profile', notifications: 'Notifications', loanRequirement: 'Loan Requirement', financialProfile: 'Financial Profile', logout: 'Logout', language: 'हिंदी', search: 'Search', viewDetails: 'View details', apply: 'Start application' } },
  hi: { translation: { brand: 'क्रेडसाथी', dashboard: 'डैशबोर्ड', schemes: 'ऋण योजनाएँ', applications: 'आवेदन', documents: 'दस्तावेज़', financial: 'वित्तीय स्थिति', assistant: 'AI सहायक', settings: 'सेटिंग्स', profile: 'प्रोफ़ाइल', notifications: 'सूचनाएँ', loanRequirement: 'ऋण आवश्यकता', financialProfile: 'वित्तीय प्रोफ़ाइल', logout: 'लॉग आउट', language: 'English', search: 'खोजें', viewDetails: 'विवरण देखें', apply: 'आवेदन शुरू करें' } }
};
i18n.use(initReactI18next).init({ resources, lng: 'en', fallbackLng: 'en', interpolation: { escapeValue: false } });
export default i18n;
