import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ScanLine, Users, Stethoscope, Target, Percent, ArrowRight } from 'lucide-react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { dashboardAPI } from '../../services/api';
import { useLang } from '../../context/LanguageContext';
import './Dashboard.css';

const DIST_COLORS = ['--primary', '--teal', '--med', '--info', '--other', '--high'];

function SeverityBadge({ severity, t }) {
    const cls = { LOW: 'sev-pill--low', MEDIUM: 'sev-pill--medium', HIGH: 'sev-pill--high' };
    const labels = { LOW: t('conditions.low'), MEDIUM: t('conditions.medium'), HIGH: t('conditions.high') };
    return <span className={`sev-pill ${cls[severity] || ''}`}>{labels[severity] || severity || '—'}</span>;
}

const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="chart-tooltip">
                <div className="chart-tooltip-label">{label}</div>
                <div className="chart-tooltip-value">{payload[0].value}</div>
            </div>
        );
    }
    return null;
};

export default function Dashboard() {
    const { t } = useLang();
    const [summary, setSummary] = useState(null);
    const [monthlyTrend, setMonthlyTrend] = useState([]);
    const [conditionDist, setConditionDist] = useState([]);
    const [recentAnalyses, setRecentAnalyses] = useState([]);
    const [topConditions, setTopConditions] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const [sumRes, trendRes, distRes, recentRes, topRes] = await Promise.all([
                    dashboardAPI.getSummary(),
                    dashboardAPI.getMonthlyTrend(),
                    dashboardAPI.getConditionDistribution(),
                    dashboardAPI.getRecentAnalyses(),
                    dashboardAPI.getTopDetectedConditions(),
                ]);
                setSummary(sumRes.data);
                setMonthlyTrend(trendRes.data);
                setConditionDist(distRes.data);
                setRecentAnalyses(recentRes.data);
                setTopConditions(topRes.data);
            } catch (err) {
                console.error('Dashboard load error:', err);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    if (loading) return <div className="dash-loading">{t('common.loading')}</div>;

    const maxDist = Math.max(1, ...conditionDist.map(d => d.value || 0));
    const maxTop  = Math.max(1, ...topConditions.map(c => c.count || 0));

    const kpis = [
        { label: t('dashboard.totalAnalyses'),      value: summary?.total_analyses ?? '—',      Icon: ScanLine,    delta: null },
        { label: t('dashboard.totalUsers'),         value: summary?.total_users ?? '—',         Icon: Users,       delta: null },
        { label: t('dashboard.conditionsDetected'), value: summary?.conditions_detected ?? '—', Icon: Stethoscope, delta: null },
        { label: t('dashboard.accuracyRate'),       value: summary?.accuracy_rate != null ? `${summary.accuracy_rate}%` : '—', Icon: Target, delta: 'accuracy' },
        { label: t('dashboard.lowConfidenceRate'),  value: summary?.low_confidence_rate != null ? `${summary.low_confidence_rate}%` : '—', Icon: Percent, delta: 'low-confidence' },
    ];

    return (
        <div className="dashboard-page">

            {/* ── KPI row ──────────────────────────────────────────────────────── */}
            <div className="kpi-row">
                {kpis.map(({ label, value, Icon, delta }) => (
                    <div className="kpi-card" key={label}>
                        <div className="kpi-card-top">
                            <span className="kpi-label">{label}</span>
                            <Icon size={15} strokeWidth={1.8} className="kpi-icon" />
                        </div>
                        <div className="kpi-value">{value}</div>
                        {delta && <div className="kpi-delta">{delta === 'accuracy' ? t('dashboard.accuracyLabel') : t('dashboard.lowConfidenceRate')}</div>}
                    </div>
                ))}
            </div>

            {/* ── Row 1: trend chart / distribution bars ──────────────────────── */}
            <div className="dash-grid-2">
                <div className="dash-card">
                    <div className="dash-card-head">
                        <h2 className="dash-card-title">{t('dashboard.monthlyTrend')}</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={230}>
                        <LineChart data={monthlyTrend} margin={{ top: 6, right: 12, left: -18, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                            <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                            <Tooltip content={<CustomTooltip />} />
                            <Line type="monotone" dataKey="count" stroke="var(--primary)" strokeWidth={2.5}
                                  dot={{ fill: 'var(--primary)', r: 3, strokeWidth: 0 }}
                                  activeDot={{ r: 5, strokeWidth: 0 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                <div className="dash-card">
                    <div className="dash-card-head">
                        <h2 className="dash-card-title">{t('dashboard.conditionDistribution')}</h2>
                    </div>
                    <div className="dist-list">
                        {conditionDist.length === 0 ? (
                            <div className="dash-empty">{t('common.noResults')}</div>
                        ) : conditionDist.slice(0, 6).map((d, i) => (
                            <div className="dist-row" key={d.name + i}>
                                <div className="dist-row-top">
                                    <span className="dist-row-name">{d.name}</span>
                                    <span className="dist-row-count">{d.value}</span>
                                </div>
                                <div className="dist-row-track">
                                    <div className="dist-row-fill" style={{ width: `${(d.value / maxDist) * 100}%`, background: `var(${DIST_COLORS[i % DIST_COLORS.length]})` }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* ── Row 2: recent analyses / top detected ───────────────────────── */}
            <div className="dash-grid-2">
                <div className="dash-card">
                    <div className="dash-card-head">
                        <h2 className="dash-card-title">{t('dashboard.recentAnalyses')}</h2>
                        <Link to="/analyses" className="dash-view-all">
                            {t('common.viewAll')} <ArrowRight size={13} strokeWidth={2} style={{ display: 'inline', verticalAlign: 'middle' }} />
                        </Link>
                    </div>
                    <div className="recent-list">
                        {recentAnalyses.length === 0 ? (
                            <div className="dash-empty">{t('common.noResults')}</div>
                        ) : recentAnalyses.slice(0, 5).map(row => {
                            const conditionName = row.condition || row.condition_name || '—';
                            const initial = conditionName?.[0]?.toUpperCase() || '?';
                            const confidencePct = row.confidence != null ? `${row.confidence}%` : '—';
                            const dateStr = row.created_at ? new Date(row.created_at).toLocaleDateString() : '—';
                            return (
                                <div key={row.id} className="recent-row">
                                    <div className="recent-avatar">{initial}</div>
                                    <div className="recent-main">
                                        <div className="recent-name">{conditionName}</div>
                                        <div className="recent-sub">{row.analysis_key}</div>
                                    </div>
                                    <SeverityBadge severity={row.severity} t={t} />
                                    <div className="recent-right">
                                        <div className="recent-confidence">{confidencePct}</div>
                                        <div className="recent-date">{dateStr}</div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                <div className="dash-card">
                    <div className="dash-card-head">
                        <h2 className="dash-card-title">{t('dashboard.topDetected')}</h2>
                    </div>
                    <div className="top-list">
                        {topConditions.length === 0 ? (
                            <div className="dash-empty">{t('common.noResults')}</div>
                        ) : topConditions.slice(0, 6).map((c, i) => (
                            <div key={c.name + i} className="top-row">
                                <span className="top-rank">#{i + 1}</span>
                                <div className="top-main">
                                    <div className="top-row-top">
                                        <span className="top-name">{c.name}</span>
                                        <span className="top-count">{c.count}</span>
                                    </div>
                                    <div className="top-track">
                                        <div className="top-fill" style={{ width: `${(c.count / maxTop) * 100}%` }} />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
