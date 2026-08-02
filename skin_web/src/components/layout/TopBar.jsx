import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useLang } from '../../context/LanguageContext';
import './TopBar.css';

const TITLE_BY_PATH = {
    '/dashboard':  'nav.dashboard',
    '/conditions': 'nav.conditions',
    '/users':      'nav.users',
    '/analyses':   'nav.analyses',
    '/statistics': 'nav.statistics',
    '/settings':   'nav.settings',
    '/profile':    'nav.profile',
};

export default function TopBar() {
    const { user } = useAuth();
    const { t } = useLang();
    const location = useLocation();

    const titleKey = TITLE_BY_PATH[location.pathname] || 'nav.dashboard';
    const initial = user?.full_name?.[0]?.toUpperCase() || 'A';

    return (
        <header className="topbar">
            <h1 className="topbar-title">{t(titleKey)}</h1>
            <NavLink to="/profile" className="topbar-avatar" title={t('nav.profile')}>
                {initial}
            </NavLink>
        </header>
    );
}
