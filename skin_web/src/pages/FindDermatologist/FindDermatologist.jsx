import { useState, useEffect } from 'react';
import { MapPin, Phone, Globe, StickyNote, Contact, Navigation } from 'lucide-react';
import { useLang } from '../../context/LanguageContext';
import { dermatologistsAPI } from '../../services/api';
import PageHeroWave from '../../components/decor/PageHeroWave';
import './FindDermatologist.css';

// Same 11 cities core/services/geo.py's MK_CITY_COORDS knows about (and
// scrape_dermatologists.py has listings for) - kept in sync by hand since
// there's no API endpoint just for "which cities do you support".
const MK_CITIES = [
    'Скопје', 'Битола', 'Штип', 'Куманово', 'Прилеп',
    'Охрид', 'Струмица', 'Гевгелија', 'Кочани', 'Неготино', 'Радовиш',
];

const CITY_STORAGE_KEY = 'skinscan-derm-city';

// Read-only, patient-facing directory. Only ever calls dermatologistsAPI.getAll() -
// no create/update/delete here. The list can come from the admin typing rows
// in by hand, or from scrape_dermatologists.py (see core/models.py).
//
// No browser geolocation here - it needs HTTPS, which this app doesn't have
// yet in dev (plain http://<lan-ip>:8000). Instead the user picks their city
// once (persisted in localStorage) and the backend sorts every dermatologist
// - in any city - by real distance from that city's center coordinates (see
// core/services/geo.py). Mobile uses actual GPS instead (see
// dermatologist_list_screen.dart) since native location permissions don't
// have the HTTPS restriction.
export default function FindDermatologist() {
    const { t } = useLang();
    const [dermatologists, setDermatologists] = useState([]);
    const [loading, setLoading] = useState(true);
    const [city, setCity] = useState(() => localStorage.getItem(CITY_STORAGE_KEY) || '');

    useEffect(() => {
        let cancelled = false;
        const load = async () => {
            setLoading(true);
            try {
                const res = await dermatologistsAPI.getAll(city ? { near_city: city } : undefined);
                if (!cancelled) setDermatologists(res.data || []);
            } catch (err) {
                console.error('Failed to load dermatologists:', err);
            } finally {
                if (!cancelled) setLoading(false);
            }
        };
        load();
        return () => { cancelled = true; };
    }, [city]);

    const handleCityChange = (e) => {
        const next = e.target.value;
        setCity(next);
        if (next) localStorage.setItem(CITY_STORAGE_KEY, next);
        else localStorage.removeItem(CITY_STORAGE_KEY);
    };

    if (loading && dermatologists.length === 0) {
        return <div className="fd-loading">{t('common.loading')}</div>;
    }

    return (
        <div className="find-derm-page">
            <div className="page-hero-band">
                <PageHeroWave />
                <div className="page-hero-inner">
                    <div className="page-header">
                        <div>
                            <h1 className="page-title">{t('findDermatologist.title')}</h1>
                            <p className="page-subtitle">{t('findDermatologist.subtitle')}</p>
                        </div>
                    </div>

                </div>
            </div>

            <div className="fd-filter-bar">
                <div className="fd-city-picker">
                    <Navigation size={15} strokeWidth={1.8} />
                    <label htmlFor="fd-city-select">{t('findDermatologist.yourCity')}</label>
                    <select id="fd-city-select" value={city} onChange={handleCityChange}>
                        <option value="">{t('findDermatologist.anyCity')}</option>
                        {MK_CITIES.map((c) => (
                            <option key={c} value={c}>{c}</option>
                        ))}
                    </select>
                </div>
                {city && (
                    <span className="fd-filter-hint">{t('findDermatologist.sortedByDistance')}</span>
                )}
            </div>

            {dermatologists.length === 0 ? (
                <div className="fd-empty">
                    <div className="fd-empty-icon"><Contact size={24} strokeWidth={1.6} /></div>
                    <span className="fd-empty-title">{t('findDermatologist.empty')}</span>
                    <span className="fd-empty-sub">{t('findDermatologist.emptySub')}</span>
                </div>
            ) : (
                <div className="fd-list">
                    {dermatologists.map((d) => (
                        <div key={d.id} className="fd-card">
                            <div className="fd-card-main">
                                <div className="fd-card-name-row">
                                    <h3 className="fd-card-name">{d.name}</h3>
                                    {d.distance_km != null && (
                                        <span className="fd-distance-pill">{d.distance_km} км</span>
                                    )}
                                </div>
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
