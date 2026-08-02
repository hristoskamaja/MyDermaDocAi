import { useState, useEffect } from 'react';
import { Search, X, ImageIcon, UserCircle } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { analysesAPI } from '../../services/api';
import { useLang } from '../../context/LanguageContext';
import './AnalysisHistory.css';

function SeverityDot({ severity }) {
    const cls = { LOW: 'sev-dot--low', MEDIUM: 'sev-dot--medium', HIGH: 'sev-dot--high' };
    return <span className={`sev-dot ${cls[severity] || 'sev-dot--other'}`} />;
}

function FlagPill({ isLowConfidence, t }) {
    return isLowConfidence
        ? <span className="flag-pill flag-pill--low">{t('analyses.lowConfidenceOnly')}</span>
        : <span className="flag-pill flag-pill--ok">Confident</span>;
}

export default function AnalysisHistory() {
    const location   = useLocation();
    const navigate   = useNavigate();
    const { t }      = useLang();
    const userFilter = location.state?.userId   || null;
    const userName   = location.state?.userName || null;

    const [analyses, setAnalyses] = useState([]);
    const [loading,  setLoading]  = useState(true);
    const [search,   setSearch]   = useState('');
    const [lowConfOnly, setLowConfOnly] = useState(false);

    useEffect(() => { loadAnalyses(); }, []);

    const loadAnalyses = async () => {
        try {
            const res = await analysesAPI.getAll();
            setAnalyses(res.data);
        } catch (err) {
            console.error('Load analyses error:', err);
        } finally {
            setLoading(false);
        }
    };

    const getConditionName = (a) => a.condition_name || a.condition?.name || '';
    const getSeverity      = (a) => a.severity || a.condition?.severity || '';
    const getUserName      = (a) => a.user_name || a.user?.full_name || '—';

    const filtered = analyses
        .filter(a => {
            const q = search.toLowerCase();
            const conditionName = getConditionName(a);
            const matchSearch = (a.analysis_key || '').toLowerCase().includes(q) ||
                conditionName.toLowerCase().includes(q) ||
                getUserName(a).toLowerCase().includes(q);
            const matchLowConf = !lowConfOnly || a.is_low_confidence;
            const matchUser = userFilter ? a.user_id === userFilter : true;
            return matchSearch && matchLowConf && matchUser;
        })
        .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));

    if (loading) return <div className="dash-loading">{t('common.loading')}</div>;

    return (
        <div className="analysis-page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">{t('analyses.title')}</h1>
                    <p className="page-subtitle">{t('analyses.subtitle')}</p>
                </div>
            </div>

            {userFilter && (
                <div className="user-filter-banner">
                    <UserCircle size={16} strokeWidth={1.8} />
                    <span>{t('analyses.showingFor')} <strong>{userName}</strong></span>
                    <button className="user-filter-clear" onClick={() => navigate('/analyses', { replace: true })}>
                        {t('analyses.clearFilter')}
                    </button>
                </div>
            )}

            <div className="ah-filters">
                <div className="dis-search">
                    <Search size={15} color="var(--text-muted)" strokeWidth={1.8} />
                    <input className="dis-search-input" placeholder={t('analyses.searchPlaceholder')}
                           value={search} onChange={e => setSearch(e.target.value)} />
                    {search && <button className="dis-search-clear" onClick={() => setSearch('')}><X size={14} strokeWidth={2} /></button>}
                </div>
                <button
                    className={`toggle-pill ${lowConfOnly ? 'toggle-pill--active' : ''}`}
                    onClick={() => setLowConfOnly(v => !v)}
                >
                    {t('analyses.lowConfidenceOnly')}
                </button>
            </div>

            {filtered.length === 0 ? (
                <div className="dis-empty">
                    <span className="dis-empty-title">{t('analyses.noAnalyses')}</span>
                    <span className="dis-empty-sub">{t('analyses.noAnalysesSub')}</span>
                </div>
            ) : (
                <div className="table-card">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th>{t('common.name')}</th>
                                <th>{t('analyses.condition')}</th>
                                <th>{t('analyses.confidence')}</th>
                                <th>{t('common.status')}</th>
                                <th>{t('common.date')}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map(a => {
                                const conditionName = getConditionName(a) || '—';
                                const confidencePct = a.confidence != null ? `${(a.confidence * 100).toFixed(0)}%` : '—';
                                const dateStr = a.created_at ? a.created_at.slice(0, 10) : '—';
                                return (
                                    <tr key={a.id}>
                                        <td>
                                            <div className="thumb-placeholder">
                                                <ImageIcon size={13} strokeWidth={1.8} />
                                                <span>IMG</span>
                                            </div>
                                        </td>
                                        <td className="cell-muted">{getUserName(a)}</td>
                                        <td>
                                            <div className="condition-cell">
                                                <SeverityDot severity={getSeverity(a)} />
                                                {conditionName}
                                            </div>
                                        </td>
                                        <td className="cell-name">{confidencePct}</td>
                                        <td>
                                            <FlagPill isLowConfidence={a.is_low_confidence} t={t} />
                                        </td>
                                        <td className="cell-muted">{dateStr}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
