import { useState, useEffect } from 'react';
import {
    LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts';
import { statisticsAPI } from '../../services/api';
import { useLang } from '../../context/LanguageContext';
import './Statistics.css';

const RANGES = ['7D', '30D', '90D', '365D'];

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

export default function Statistics() {
    const { t } = useLang();
    const [range,         setRange]         = useState('30D');
    const [monthlyData,   setMonthlyData]   = useState([]);
    const [userGrowth,    setUserGrowth]    = useState([]);
    const [accuracy,      setAccuracy]      = useState([]);
    const [topConditions, setTopConditions] = useState([]);
    const [loading,       setLoading]       = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const [moRes, ugRes, acRes, tdRes] = await Promise.all([
                    statisticsAPI.getAnalysesByMonth(),
                    statisticsAPI.getUserGrowth(),
                    statisticsAPI.getDetectionAccuracy(),
                    statisticsAPI.getTopDetectedConditions(),
                ]);
                setMonthlyData(moRes.data);
                setUserGrowth(ugRes.data);
                setAccuracy(acRes.data);
                setTopConditions(tdRes.data);
            } catch (err) {
                console.error('Statistics load error:', err);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    if (loading) return <div className="dash-loading">{t('common.loading')}</div>;

    const maxTop = Math.max(1, ...topConditions.map(c => c.count || 0));

    return (
        <div className="statistics-page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">{t('statistics.title')}</h1>
                    <p className="page-subtitle">{t('statistics.subtitle')}</p>
                </div>
            </div>

            {/* ── Range selector pills ─────────────────────────────────────────── */}
            <div className="range-pills">
                {RANGES.map(r => (
                    <button
                        key={r}
                        className={`range-pill ${range === r ? 'range-pill--active' : ''}`}
                        onClick={() => setRange(r)}
                    >
                        {r}
                    </button>
                ))}
            </div>

            {/* ── 2x2 chart grid ───────────────────────────────────────────────── */}
            <div className="stat-grid">
                <div className="dash-card">
                    <div className="dash-card-head">
                        <h2 className="dash-card-title">{t('statistics.analysesOverTime')}</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={220}>
                        <LineChart data={monthlyData} margin={{ top: 6, right: 12, left: -18, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                            <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                            <Tooltip content={<CustomTooltip />} />
                            <Line type="monotone" dataKey="count" stroke="var(--primary)" strokeWidth={2.5}
                                  dot={{ fill: 'var(--primary)', r: 3, strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                <div className="dash-card">
                    <div className="dash-card-head">
                        <h2 className="dash-card-title">{t('statistics.detectionAccuracy')}</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={220}>
                        <LineChart data={accuracy} margin={{ top: 6, right: 12, left: -18, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                            <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                            <Tooltip content={<CustomTooltip />} />
                            <Line type="monotone" dataKey="accuracy" stroke="var(--teal)" strokeWidth={2.5}
                                  dot={{ fill: 'var(--teal)', r: 3, strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                <div className="dash-card">
                    <div className="dash-card-head">
                        <h2 className="dash-card-title">{t('statistics.userGrowth')}</h2>
                    </div>
                    <ResponsiveContainer width="100%" height={220}>
                        <LineChart data={userGrowth} margin={{ top: 6, right: 12, left: -18, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                            <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                            <Tooltip content={<CustomTooltip />} />
                            <Line type="monotone" dataKey="count" stroke="var(--info)" strokeWidth={2.5}
                                  dot={{ fill: 'var(--info)', r: 3, strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                <div className="dash-card">
                    <div className="dash-card-head">
                        <h2 className="dash-card-title">{t('statistics.topDetected')}</h2>
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
