import { useState, useEffect } from 'react';
import {
    Plus,
    Pencil,
    Trash2,
    X,
    MapPin,
    Phone,
    Globe,
    StickyNote,
    AlertTriangle,
} from 'lucide-react';

import { useLang } from '../../context/LanguageContext';
import { dermatologistsAPI } from '../../services/api';

import './Dermatologists.css';

// ── Constants ────────────────────────────────────────────────────────────────
const EMPTY_FORM = {
    name: '',
    clinic_name: '',
    city: '',
    address: '',
    phone: '',
    website: '',
    notes: '',
    is_active: true,
};

// ── Form modal (add / edit) ───────────────────────────────────────────────────
function FormModal({ dermatologist, onSave, onClose, t }) {
    const isEdit = !!dermatologist?.id;

    const [form, setForm] = useState(
        isEdit
            ? {
                name:        dermatologist.name        || '',
                clinic_name: dermatologist.clinic_name || '',
                city:        dermatologist.city        || '',
                address:     dermatologist.address      || '',
                phone:       dermatologist.phone        || '',
                website:     dermatologist.website       || '',
                notes:       dermatologist.notes        || '',
                is_active:   dermatologist.is_active !== undefined ? dermatologist.is_active : true,
            }
            : { ...EMPTY_FORM }
    );

    const [errors, setErrors] = useState({});

    const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

    const validate = () => {
        const e = {};
        if (!form.name.trim()) e.name = 'Name is required';
        setErrors(e);
        return Object.keys(e).length === 0;
    };

    const handleSave = () => {
        if (!validate()) return;

        const payload = {
            name:        form.name,
            clinic_name: form.clinic_name || null,
            city:        form.city || null,
            address:     form.address || null,
            phone:       form.phone || null,
            website:     form.website || null,
            notes:       form.notes || null,
            is_active:   form.is_active,
        };

        onSave({ id: dermatologist?.id, data: payload });
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-box" onClick={(e) => e.stopPropagation()}>

                <div className="modal-header">
                    <h3 className="modal-title">
                        {isEdit ? t('dermatologists.editTitle') : t('dermatologists.addTitle')}
                    </h3>
                    <button className="modal-close" onClick={onClose}>
                        <X size={18} strokeWidth={2} />
                    </button>
                </div>

                <div className="modal-body">

                    {/* Name */}
                    <div className="form-field">
                        <label className="form-label">{t('dermatologists.name')}</label>
                        <input
                            className={`form-input ${errors.name ? 'form-input--error' : ''}`}
                            value={form.name}
                            onChange={(e) => set('name', e.target.value)}
                        />
                        {errors.name && <span className="form-error">{errors.name}</span>}
                    </div>

                    {/* Clinic name */}
                    <div className="form-field">
                        <label className="form-label">
                            {t('dermatologists.clinicName')}
                            <span className="form-optional">({t('dermatologists.optional')})</span>
                        </label>
                        <input
                            className="form-input"
                            value={form.clinic_name}
                            onChange={(e) => set('clinic_name', e.target.value)}
                        />
                    </div>

                    {/* City + Phone */}
                    <div className="form-row">
                        <div className="form-field">
                            <label className="form-label">
                                {t('dermatologists.city')}
                                <span className="form-optional">({t('dermatologists.optional')})</span>
                            </label>
                            <input
                                className="form-input"
                                value={form.city}
                                onChange={(e) => set('city', e.target.value)}
                            />
                        </div>

                        <div className="form-field">
                            <label className="form-label">
                                {t('dermatologists.phone')}
                                <span className="form-optional">({t('dermatologists.optional')})</span>
                            </label>
                            <input
                                className="form-input"
                                value={form.phone}
                                onChange={(e) => set('phone', e.target.value)}
                            />
                        </div>
                    </div>

                    {/* Address */}
                    <div className="form-field">
                        <label className="form-label">
                            {t('dermatologists.address')}
                            <span className="form-optional">({t('dermatologists.optional')})</span>
                        </label>
                        <input
                            className="form-input"
                            value={form.address}
                            onChange={(e) => set('address', e.target.value)}
                        />
                    </div>

                    {/* Website */}
                    <div className="form-field">
                        <label className="form-label">
                            {t('dermatologists.website')}
                            <span className="form-optional">({t('dermatologists.optional')})</span>
                        </label>
                        <input
                            className="form-input"
                            value={form.website}
                            placeholder="https://…"
                            onChange={(e) => set('website', e.target.value)}
                        />
                    </div>

                    {/* Notes */}
                    <div className="form-field">
                        <label className="form-label">
                            {t('dermatologists.notes')}
                            <span className="form-optional">({t('dermatologists.optional')})</span>
                        </label>
                        <textarea
                            className="form-input form-textarea"
                            rows={3}
                            value={form.notes}
                            onChange={(e) => set('notes', e.target.value)}
                        />
                    </div>

                    {/* Active toggle */}
                    <div className="form-field">
                        <label className="derm-toggle-row">
                            <input
                                type="checkbox"
                                checked={form.is_active}
                                onChange={(e) => set('is_active', e.target.checked)}
                            />
                            <span>{t('dermatologists.isActive')}</span>
                        </label>
                    </div>

                </div>

                <div className="modal-footer">
                    <button className="btn btn--secondary" onClick={onClose}>
                        {t('common.cancel')}
                    </button>
                    <button className="btn btn--primary" onClick={handleSave}>
                        {t('common.save')}
                    </button>
                </div>

            </div>
        </div>
    );
}

// ── Delete modal ─────────────────────────────────────────────────────────────
function DeleteModal({ dermatologist, onConfirm, onCancel, t }) {
    if (!dermatologist) return null;
    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal-box modal-box--sm" onClick={e => e.stopPropagation()}>
                <div className="modal-warn-icon"><AlertTriangle size={26} color="var(--high)" strokeWidth={1.8} /></div>
                <h3 className="modal-warn-title">{t('dermatologists.deleteTitle')}</h3>
                <p className="modal-warn-desc">{t('dermatologists.deleteDesc')} <strong>{dermatologist.name}</strong>? {t('dermatologists.deleteWarn')}</p>
                <div className="modal-warn-actions">
                    <button className="btn btn--secondary" onClick={onCancel}>{t('common.cancel')}</button>
                    <button className="btn btn--danger" onClick={onConfirm}>{t('common.delete')}</button>
                </div>
            </div>
        </div>
    );
}

// ── Main page ────────────────────────────────────────────────────────────────
export default function Dermatologists() {

    const { t } = useLang();

    const [dermatologists, setDermatologists] = useState([]);
    const [loading, setLoading] = useState(true);

    const [modal,    setModal]    = useState(null);
    const [selected, setSelected] = useState(null);

    // ── Fetch ────────────────────────────────────────────────────────────────
    useEffect(() => { fetchDermatologists(); }, []);

    const fetchDermatologists = async () => {
        try {
            setLoading(true);
            const response = await dermatologistsAPI.getAll();
            setDermatologists(response.data);
        } catch (error) {
            console.error('Failed to fetch dermatologists:', error);
        } finally {
            setLoading(false);
        }
    };

    // ── Save ─────────────────────────────────────────────────────────────────
    const handleSave = async ({ id, data }) => {
        try {
            if (id) {
                await dermatologistsAPI.partialUpdate(id, data);
            } else {
                await dermatologistsAPI.create(data);
            }
            await fetchDermatologists();
            setModal(null);
            setSelected(null);
        } catch (error) {
            console.error('Save failed:', error);
        }
    };

    // ── Delete ───────────────────────────────────────────────────────────────
    const handleDelete = async () => {
        try {
            await dermatologistsAPI.delete(selected.id);
            await fetchDermatologists();
            setModal(null);
            setSelected(null);
        } catch (error) {
            console.error('Delete failed:', error);
        }
    };

    // ── Loading ──────────────────────────────────────────────────────────────
    if (loading) return <div className="dis-loading">{t('common.loading')}</div>;

    // ── Render ───────────────────────────────────────────────────────────────
    return (
        <div className="dermatologists-page">

            <div className="page-header">
                <div>
                    <h1 className="page-title">{t('dermatologists.title')}</h1>
                    <p className="page-subtitle">{t('dermatologists.subtitle')}</p>
                </div>
                <button
                    className="btn btn--primary"
                    onClick={() => { setSelected(null); setModal('form'); }}
                >
                    <Plus size={16} />
                    {t('dermatologists.addBtn')}
                </button>
            </div>

            {dermatologists.length === 0 ? (
                <div className="dis-empty">
                    <span className="dis-empty-title">{t('dermatologists.noDermatologistsTitle')}</span>
                    <span className="dis-empty-sub">{t('dermatologists.noDermatologistsSub')}</span>
                </div>
            ) : (
                <div className="derm-grid">
                    {dermatologists.map((d) => (
                        <div key={d.id} className="derm-card">
                            <div className="derm-card-top">
                                <h3 className="derm-card-name">{d.name}</h3>
                                <span className={`derm-status-pill ${d.is_active ? 'derm-status-pill--active' : 'derm-status-pill--inactive'}`}>
                                    {d.is_active ? t('dermatologists.active') : t('dermatologists.inactive')}
                                </span>
                            </div>

                            {d.clinic_name && <div className="derm-card-clinic">{d.clinic_name}</div>}

                            <div className="derm-card-details">
                                {(d.city || d.address) && (
                                    <div className="derm-card-row">
                                        <MapPin size={13} strokeWidth={1.8} />
                                        <span>{[d.city, d.address].filter(Boolean).join(' · ')}</span>
                                    </div>
                                )}
                                {d.phone && (
                                    <div className="derm-card-row">
                                        <Phone size={13} strokeWidth={1.8} />
                                        <span>{d.phone}</span>
                                    </div>
                                )}
                                {d.website && (
                                    <div className="derm-card-row">
                                        <Globe size={13} strokeWidth={1.8} />
                                        <span className="derm-card-website">{d.website}</span>
                                    </div>
                                )}
                                {d.notes && (
                                    <div className="derm-card-row">
                                        <StickyNote size={13} strokeWidth={1.8} />
                                        <span>{d.notes}</span>
                                    </div>
                                )}
                            </div>

                            <div className="derm-card-footer">
                                <div className="derm-card-actions">
                                    <button
                                        className="dis-action-btn dis-action-btn--edit"
                                        onClick={() => { setSelected(d); setModal('form'); }}
                                    >
                                        <Pencil size={13} />
                                    </button>
                                    <button
                                        className="dis-action-btn dis-action-btn--delete"
                                        onClick={() => { setSelected(d); setModal('delete'); }}
                                    >
                                        <Trash2 size={13} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {modal === 'form' && (
                <FormModal
                    dermatologist={selected}
                    onSave={handleSave}
                    onClose={() => { setModal(null); setSelected(null); }}
                    t={t}
                />
            )}

            {modal === 'delete' && (
                <DeleteModal
                    dermatologist={selected}
                    onConfirm={handleDelete}
                    onCancel={() => { setModal(null); setSelected(null); }}
                    t={t}
                />
            )}

        </div>
    );
}
