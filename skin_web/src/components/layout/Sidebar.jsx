import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useLang } from '../../context/LanguageContext';
import {
    LayoutDashboard, Stethoscope,
    Users, FlaskConical, BarChart2,
    Settings, UserCircle, LogOut, Contact
} from 'lucide-react';
import './Sidebar.css';

export default function Sidebar() {
    const { logout, user } = useAuth();
    const { t }       = useLang();
    const navigate    = useNavigate();

    const NAV = [
        { to: '/dashboard',      label: t('nav.dashboard'),      Icon: LayoutDashboard },
        { to: '/conditions',     label: t('nav.conditions'),     Icon: Stethoscope     },
        { to: '/dermatologists', label: t('nav.dermatologists'), Icon: Contact         },
        { to: '/users',          label: t('nav.users'),          Icon: Users           },
        { to: '/analyses',       label: t('nav.analyses'),       Icon: FlaskConical    },
        { to: '/statistics',     label: t('nav.statistics'),     Icon: BarChart2       },
    ];

    const BOTTOM_NAV = [
        { to: '/settings', label: t('nav.settings'), Icon: Settings   },
        { to: '/profile',  label: t('nav.profile'),  Icon: UserCircle },
    ];

    const initial = user?.full_name?.[0]?.toUpperCase() || 'A';
    const name    = user?.full_name || 'Admin';
    const roleLabel = user?.role === 'ADMIN' ? t('users.admin') : t('users.user');

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon">D</div>
                <span className="sidebar-logo-text">DermaScanAI</span>
            </div>

            <nav className="sidebar-nav">
                {NAV.map(({ to, label, Icon }) => (
                    <NavLink key={to} to={to}
                             className={({ isActive }) => `sidebar-link${isActive ? ' sidebar-link--active' : ''}`}>
                        <Icon size={18} className="sidebar-link-icon" strokeWidth={1.8} />
                        <span>{label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="sidebar-spacer" />

            <div className="sidebar-profile">
                <div className="sidebar-profile-avatar">{initial}</div>
                <div className="sidebar-profile-info">
                    <div className="sidebar-profile-name">{name}</div>
                    <div className="sidebar-profile-role">{roleLabel}</div>
                </div>
            </div>

            <div className="sidebar-bottom">
                {BOTTOM_NAV.map(({ to, label, Icon }) => (
                    <NavLink key={to} to={to}
                             className={({ isActive }) => `sidebar-link${isActive ? ' sidebar-link--active' : ''}`}>
                        <Icon size={18} className="sidebar-link-icon" strokeWidth={1.8} />
                        <span>{label}</span>
                    </NavLink>
                ))}
                <button className="sidebar-logout" onClick={() => { logout(); navigate('/login'); }}>
                    <LogOut size={18} strokeWidth={1.8} />
                    <span>{t('nav.logout')}</span>
                </button>
            </div>
        </aside>
    );
}
