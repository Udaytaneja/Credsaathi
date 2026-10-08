import { Link } from 'react-router-dom';
import { Languages } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import Logo from './Logo';

export default function PublicHeader() {
  const { t, i18n } = useTranslation();

  return (
    <header className="public-header">
      <Link to="/" aria-label="CredSaathi Home">
        <Logo />
      </Link>
      
      <nav>
        <a href="#how">How it works</a>
        <a href="#trust">Trust &amp; security</a>
        <a href="#faq">FAQ</a>
      </nav>

      <div className="header-actions">
        <button
          className="lang-btn"
          onClick={() => i18n.changeLanguage(i18n.language === 'en' ? 'hi' : 'en')}
          type="button"
        >
          <Languages size={16} />
          {i18n.language === 'en' ? 'हिंदी' : 'English'}
        </button>

        <Link className="btn btn-secondary" to="/login">
          {t('logout') === 'लॉग आउट' ? 'लॉग इन' : 'Log in'}
        </Link>
        
        <Link className="btn btn-primary" to="/register">
          {t('apply') === 'आवेदन शुरू करें' ? 'शुरू करें' : 'Get started'}
        </Link>
      </div>
    </header>
  );
}
