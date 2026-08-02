import { useState } from 'react';
import { useTheme } from '../../context/ThemeContext';
import { useLang } from '../../context/LanguageContext';
import './Settings.css';

function ToggleRow({ label, sub, checked, onChange }) {
    return (
        <div className="toggle-row">
            <div>
                <div className="toggle-label">{label}</div>
                {sub && <div className="toggle-sub">{sub}</div>}
            </div>
            <button
                className={`toggle ${checked ? 'toggle--on' : ''}`}
                onClick={() => onChange(!checked)}
                role="switch"
                aria-checked={checked}
            >
                <span className="toggle-thumb" />
            </button>
        </div>
    );
}

export default function Settings() {
    const { isDark, toggleTheme } = useTheme();
    const { lang, setLang, t }    = useLang();

    const [emailNotif, setEmailNotif] = useState(true);
    const [pushNotif,  setPushNotif]  = useState(false);

    return (
        <div className="settings-page">

            <div className="page-header">
                <div>
                    <h1 className="page-title">{t('settings.title')}</h1>
                    <p className="page-subtitle">{t('settings.subtitle')}</p>
                </div>
            </div>

            <div className="settings-sections">

                {/* Language */}
                <div className="settings-card">
                    <div className="settings-card-header">
                        <h2 className="settings-card-title">{t('settings.language')}</h2>
                        <p className="settings-card-desc">{t('settings.languageDesc')}</p>
                    </div>
                    <div className="settings-card-body">
                        <div className="option-pills">
                            <button
                                className={`option-pill ${lang === 'en' ? 'option-pill--active' : ''}`}
                                onClick={() => setLang('en')}
                            >
                                English
                            </button>
                            <button
                                className={`option-pill ${lang === 'mk' ? 'option-pill--active' : ''}`}
                                onClick={() => setLang('mk')}
                            >
                                Македонски
                            </button>
                        </div>
                    </div>
                </div>

                {/* Theme */}
                <div className="settings-card">
                    <div className="settings-card-header">
                        <h2 className="settings-card-title">{t('settings.appearance')}</h2>
                        <p className="settings-card-desc">{t('settings.appearanceDesc')}</p>
                    </div>
                    <div className="settings-card-body">
                        <div className="option-pills">
                            <button
                                className={`option-pill ${!isDark ? 'option-pill--active' : ''}`}
                                onClick={() => isDark && toggleTheme()}
                            >
                                {t('settings.lightMode')}
                            </button>
                            <button
                                className={`option-pill ${isDark ? 'option-pill--active' : ''}`}
                                onClick={() => !isDark && toggleTheme()}
                            >
                                {t('settings.darkMode')}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Notifications */}
                <div className="settings-card">
                    <div className="settings-card-header">
                        <h2 className="settings-card-title">{t('settings.notifications')}</h2>
                        <p className="settings-card-desc">{t('settings.notificationsDesc')}</p>
                    </div>
                    <div className="settings-card-body">
                        <ToggleRow
                            label={t('settings.emailNotif')}
                            sub={t('settings.emailNotifSub')}
                            checked={emailNotif}
                            onChange={setEmailNotif}
                        />
                        <div className="settings-divider" />
                        <ToggleRow
                            label={t('settings.pushNotif')}
                            sub={t('settings.pushNotifSub')}
                            checked={pushNotif}
                            onChange={setPushNotif}
                        />
                    </div>
                </div>

            </div>

        </div>
    );
}
