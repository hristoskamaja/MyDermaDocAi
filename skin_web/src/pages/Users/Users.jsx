import { useState, useEffect } from 'react';
import {
    Search, X, Trash2, Pencil, Plus,
    AlertTriangle, FlaskConical
} from 'lucide-react';
import { useLang } from '../../context/LanguageContext';
import { usersAPI } from '../../services/api';
import './Users.css';

const ROLE_OPTIONS = ['ADMIN', 'USER'];
const EMPTY_FORM   = { full_name: '', email: '', username: '', role: 'USER' };

function RoleBadge({ role, t }) {
    return <span className={`role-pill ${role === 'ADMIN' ? 'role-pill--admin' : 'role-pill--user'}`}>{role === 'ADMIN' ? t('users.admin') : t('users.user')}</span>;
}

function FormModal({ user, onSave, onClose, t }) {
    const isEdit = !!user?.id;
    const [form, setForm] = useState(
        isEdit
            ? { full_name: user.full_name, email: user.email, username: user.username, role: user.role }
            : { ...EMPTY_FORM }
    );
    const [password, setPassword] = useState('');
    const [errors,   setErrors]   = useState({});
    const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

    const validate = () => {
        const e = {};
        if (!form.full_name.trim()) e.full_name = t('profile.fullName') + ' is required';
        if (!form.email.trim())     e.email     = t('common.email') + ' is required';
        else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Invalid email format';
        if (!isEdit && !password.trim()) e.password = 'Password is required';
        setErrors(e);
        return Object.keys(e).length === 0;
    };

    const handleSave = () => {
        if (!validate()) return;
        const data = { ...form };
        if (!isEdit) data.password = password;
        onSave({ id: user?.id, data });
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-box" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h3 className="modal-title">{isEdit ? t('common.edit') : t('users.addBtn')}</h3>
                    <button className="modal-close" onClick={onClose}><X size={18} strokeWidth={2} /></button>
                </div>
                <div className="modal-body">
                    <div className="form-field">
                        <label className="form-label">{t('profile.fullName')} *</label>
                        <input className={`form-input ${errors.full_name ? 'form-input--error' : ''}`} value={form.full_name} onChange={e => set('full_name', e.target.value)} placeholder="e.g. John Doe" />
                        {errors.full_name && <span className="form-error">{errors.full_name}</span>}
                    </div>
                    <div className="form-field">
                        <label className="form-label">{t('common.email')} *</label>
                        <input className={`form-input ${errors.email ? 'form-input--error' : ''}`} type="email" value={form.email} onChange={e => set('email', e.target.value)} placeholder="e.g. john@dermascanai.ai" />
                        {errors.email && <span className="form-error">{errors.email}</span>}
                    </div>
                    {!isEdit && (
                        <div className="form-field">
                            <label className="form-label">{t('users.username')}</label>
                            <input className="form-input" value={form.username} onChange={e => set('username', e.target.value)} placeholder="e.g. johndoe" />
                        </div>
                    )}
                    <div className="form-field">
                        <label className="form-label">{t('users.role')} *</label>
                        <select className="form-input" value={form.role} onChange={e => set('role', e.target.value)}>
                            {ROLE_OPTIONS.map(r => <option key={r} value={r}>{r}</option>)}
                        </select>
                    </div>
                    {!isEdit && (
                        <div className="form-field">
                            <label className="form-label">{t('login.passwordLabel')} *</label>
                            <input className={`form-input ${errors.password ? 'form-input--error' : ''}`} type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Temporary password" />
                            {errors.password ? <span className="form-error">{errors.password}</span> : <span className="form-hint">User will be asked to change on first login.</span>}
                        </div>
                    )}
                </div>
                <div className="modal-footer">
                    <button className="btn btn--secondary" onClick={onClose}>{t('common.cancel')}</button>
                    <button className="btn btn--primary" onClick={handleSave}>{isEdit ? t('common.save') : t('users.addBtn')}</button>
                </div>
            </div>
        </div>
    );
}

function HistoryDrawer({ user, onClose, t }) {
    const [analyses, setAnalyses] = useState([]);
    const [loading,  setLoading]  = useState(true);

    useEffect(() => {
        if (!user) return;
        const fetchAnalyses = async () => {
            try {
                setLoading(true);
                const response = await usersAPI.getAnalyses(user.id);
                const data = response.data;
                setAnalyses(Array.isArray(data) ? data : (data.analyses ?? []));
            } catch (error) {
                console.error('Failed to fetch user analyses:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalyses();
    }, [user.id]);

    if (!user) return null;

    return (
        <div className="drawer-overlay" onClick={onClose}>
            <div className="drawer" onClick={e => e.stopPropagation()}>
                <div className="drawer-header">
                    <div>
                        <h3 className="drawer-title">{user.full_name}</h3>
                        <div className="drawer-sub">{loading ? t('common.loading') : `${analyses.length} ${t('users.analyses')}`}</div>
                    </div>
                    <button className="drawer-close" onClick={onClose}><X size={18} strokeWidth={2} /></button>
                </div>
                <div className="drawer-body">
                    {loading ? (
                        <div className="drawer-empty">{t('common.loading')}</div>
                    ) : analyses.length === 0 ? (
                        <div className="drawer-empty">
                            <FlaskConical size={30} color="var(--text-light)" strokeWidth={1.5} />
                            <div className="drawer-empty-title">{t('analyses.noAnalyses')}</div>
                            <div className="drawer-empty-sub">{t('analyses.noAnalysesSub')}</div>
                        </div>
                    ) : (
                        <div className="history-list">
                            {analyses.map(a => {
                                const conditionName = a.condition_name || a.condition?.name || a.condition || '—';
                                const confidence = a.confidence != null ? `${(a.confidence * 100).toFixed(0)}%` : '—';
                                const dateStr = a.created_at ? a.created_at.slice(0, 10) : '—';
                                return (
                                    <div key={a.id} className="history-row">
                                        <div className="history-row-left">
                                            <div className="history-row-name">{conditionName}</div>
                                            <div className="history-row-date">{dateStr}</div>
                                        </div>
                                        <div className="history-row-confidence">{confidence}</div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function DeleteModal({ user, onConfirm, onCancel, t }) {
    if (!user) return null;
    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal-box modal-box--sm" onClick={e => e.stopPropagation()}>
                <div className="modal-warn-icon"><AlertTriangle size={26} color="var(--high)" strokeWidth={1.8} /></div>
                <h3 className="modal-warn-title">{t('users.deleteTitle')}</h3>
                <p className="modal-warn-desc">{t('users.deleteDesc')} <strong>{user.full_name}</strong>? {t('users.deleteWarn')}</p>
                <div className="modal-warn-actions">
                    <button className="btn btn--secondary" onClick={onCancel}>{t('common.cancel')}</button>
                    <button className="btn btn--danger" onClick={onConfirm}>{t('common.delete')}</button>
                </div>
            </div>
        </div>
    );
}

export default function Users() {
    const { t }      = useLang();
    const [users,   setUsers]   = useState([]);
    const [loading, setLoading] = useState(true);
    const [search,  setSearch]  = useState('');
    const [scanCounts, setScanCounts] = useState({});
    const [modal,    setModal]    = useState(null);
    const [selected, setSelected] = useState(null);

    useEffect(() => { fetchUsers(); }, []);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const response = await usersAPI.getAll();
            setUsers(response.data);
            loadScanCounts(response.data);
        } catch (error) {
            console.error('Failed to fetch users:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadScanCounts = async (userList) => {
        try {
            const results = await Promise.all(
                userList.map(u => usersAPI.getAnalyses(u.id).then(res => {
                    const data = res.data;
                    const list = Array.isArray(data) ? data : (data.analyses ?? []);
                    return [u.id, list.length];
                }).catch(() => [u.id, null]))
            );
            setScanCounts(Object.fromEntries(results));
        } catch (error) {
            console.error('Failed to load scan counts:', error);
        }
    };

    const handleSave = async ({ id, data }) => {
        try {
            if (id) await usersAPI.update(id, data);
            else    await usersAPI.create(data);
            await fetchUsers();
            setModal(null); setSelected(null);
        } catch (error) { console.error('Save failed:', error); }
    };

    const handleDelete = async () => {
        try {
            await usersAPI.delete(selected.id);
            await fetchUsers();
            setModal(null); setSelected(null);
        } catch (error) { console.error('Delete failed:', error); }
    };

    const filtered = users.filter(u => {
        const q = search.toLowerCase();
        return u.full_name?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q) || u.username?.toLowerCase().includes(q);
    });

    if (loading) return <div className="dash-loading">{t('common.loading')}</div>;

    return (
        <div className="users-page">
            <div className="page-header">
                <div className="dis-search">
                    <Search size={15} color="var(--text-muted)" strokeWidth={1.8} />
                    <input className="dis-search-input" placeholder={t('users.searchPlaceholder')} value={search} onChange={e => setSearch(e.target.value)} />
                    {search && <button className="dis-search-clear" onClick={() => setSearch('')}><X size={14} strokeWidth={2} /></button>}
                </div>
                <button className="btn btn--primary" onClick={() => { setSelected(null); setModal('form'); }}>
                    <Plus size={16} strokeWidth={2.2} /> {t('users.addBtn')}
                </button>
            </div>

            {filtered.length === 0 ? (
                <div className="dis-empty">
                    <span className="dis-empty-title">{t('users.noUsersTitle')}</span>
                    <span className="dis-empty-sub">{t('users.noUsersSub')}</span>
                </div>
            ) : (
                <div className="table-card">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>{t('common.name')}</th>
                                <th>{t('common.email')}</th>
                                <th>{t('users.role')}</th>
                                <th>{t('users.joined')}</th>
                                <th>Scans</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map(u => (
                                <tr key={u.id}>
                                    <td className="cell-name">{u.full_name}</td>
                                    <td className="cell-muted">{u.email}</td>
                                    <td><RoleBadge role={u.role} t={t} /></td>
                                    <td className="cell-muted">{u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</td>
                                    <td className="cell-muted">{scanCounts[u.id] != null ? scanCounts[u.id] : '—'}</td>
                                    <td className="cell-actions">
                                        <button className="btn btn--secondary btn--sm" onClick={() => { setSelected(u); setModal('history'); }}>
                                            {t('users.viewAnalyses')}
                                        </button>
                                        <button className="dis-action-btn dis-action-btn--edit" onClick={() => { setSelected(u); setModal('form'); }} title={t('common.edit')}><Pencil size={13} strokeWidth={1.8} /></button>
                                        <button className="dis-action-btn dis-action-btn--delete" onClick={() => { setSelected(u); setModal('delete'); }} title={t('common.delete')}><Trash2 size={13} strokeWidth={1.8} /></button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {modal === 'history' && <HistoryDrawer user={selected} t={t} onClose={() => { setModal(null); setSelected(null); }} />}
            {modal === 'form'    && <FormModal     user={selected} t={t} onSave={handleSave} onClose={() => { setModal(null); setSelected(null); }} />}
            {modal === 'delete'  && <DeleteModal   user={selected} t={t} onConfirm={handleDelete} onCancel={() => { setModal(null); setSelected(null); }} />}
        </div>
    );
}
