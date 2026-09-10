import { useState, useEffect } from 'react';
import { MapPin, Phone, Globe, StickyNote, Contact } from 'lucide-react';
import { useLang } from '../../context/LanguageContext';
import { dermatologistsAPI } from '../../services/api';
import './FindDermatologist.css';

// Read-only, patient-facing directory. Only ever calls dermatologistsAPI.getAll() -
// no create/update/delete here. The list itself is maintained by hand by an
// admin through the admin panel, not scraped or auto-populated.
export default function FindDermatologist() {
    const { t } = useLang();
    const [dermatologists, setDermatologists] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const res = await dermatologistsAPI.getAll();
                setDermatologists(res.data || []);
            } catch (err) {
                console.error('Failed to load dermatologists:', err);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    if (loading) return <div className="fd-loading">{t('common.loading')}</div>;

    return (
        <div className="find-derm-page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">{t('findDermatologist.title')}</h1>
                    <p className="page-subtitle">{t('findDermatologist.subtitle')}</p>
                </div>
            </div>

            {dermatologists.length === 0 ? (
                <div className="fd-empty">
                    <Contact size={28} strokeWidth={1.5} className="fd-empty-icon" />
                    <span className="fd-empty-title">{t('findDermatologist.empty')}</span>
                    <span className="fd-empty-sub">{t('findDermatologist.emptySub')}</span>
                </div>
            ) : (
                <div className="fd-list">
                    {dermatologists.map((d) => (
                        <div key={d.id} className="fd-card">
                            <div className="fd-card-main">
                                <h3 className="fd-card-name">{d.name}</h3>
                                {d.clinic_name && <div className="fd-card-clinic">{d.clinic_name}</div>}

                                <div className="fd-card-details">
                                    {(d.city || d.address) && (
                                        <div className="fd-card-row">
                                            <MapPin size={14} strokeWidth={1.8} />
                                            <span>{[d.city, d.address].filter(Boolean).join(' · ')}</span>
                                        </div>
                                    )}
                                    {d.notes && (
                                        <div className="fd-card-row">
                                            <StickyNote size={14} strokeWidth={1.8} />
                                            <span>{d.notes}</span>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="fd-card-actions">
                                {d.phone && (
                                    <a className="fd-action-btn" href={`tel:${d.phone}`}>
                                        <Phone size={15} strokeWidth={1.8} />
                                        <span>{t('findDermatologist.call')}</span>
                                    </a>
                                )}
                                {d.website && (
                                    <a
                                        className="fd-action-btn"
                                        href={d.website}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        <Globe size={15} strokeWidth={1.8} />
                                        <span>{t('findDermatologist.website')}</span>
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
