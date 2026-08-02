import { useState, useEffect, useRef } from 'react';
import {
    Plus,
    Pencil,
    Trash2,
    X,
    FileText,
    Activity,
    ImageIcon,
    AlertTriangle,
    ClipboardList,
} from 'lucide-react';

import { useLang } from '../../context/LanguageContext';
import { conditionsAPI, recommendationsAPI } from '../../services/api';

import './Conditions.css';

// ── Constants ────────────────────────────────────────────────────────────────
const SEVERITY_OPTIONS = ['LOW', 'MEDIUM', 'HIGH'];
const CATEGORY_OPTIONS = ['BENIGN', 'PRECANCEROUS', 'MALIGNANT', 'INFLAMMATORY', 'OTHER'];
const RECOMMENDATION_TYPES = ['SELF_CARE', 'MEDICAL_CONSULT', 'LIFESTYLE'];

const EMPTY_FORM = {
    key: '',
    name: '',
    category: 'BENIGN',
    severity: 'MEDIUM',
    description: '',
    symptoms: '',
    image_description: '',
};

// ── Badges ───────────────────────────────────────────────────────────────────
function SeverityBadge({ severity, t }) {
    const cls = { LOW: 'sev-pill--low', MEDIUM: 'sev-pill--medium', HIGH: 'sev-pill--high' };
    const labels = { LOW: t('conditions.low'), MEDIUM: t('conditions.medium'), HIGH: t('conditions.high') };
    return <span className={`sev-pill ${cls[severity] || ''}`}>{labels[severity] || severity}</span>;
}

function CategoryBadge({ category }) {
    const cls = `cat-pill--${(category || 'other').toLowerCase()}`;
    return <span className={`cat-pill ${cls}`}>{category}</span>;
}

function RecTypeBadge({ type, t }) {
    const labels = {
        SELF_CARE: t('recommendations.selfCare'),
        MEDICAL_CONSULT: t('recommendations.medical'),
        LIFESTYLE: t('recommendations.lifestyle'),
    };
    const cls = {
        SELF_CARE: 'rec-badge--self',
        MEDICAL_CONSULT: 'rec-badge--medical',
        LIFESTYLE: 'rec-badge--lifestyle',
    };
    return <span className={`rec-badge ${cls[type] || ''}`}>{labels[type] || type}</span>;
}

const REC_GROUP_ORDER = ['MEDICAL_CONSULT', 'SELF_CARE', 'LIFESTYLE'];
const REC_GROUP_LABEL = (t) => ({
    MEDICAL_CONSULT: t('recommendations.medical'),
    SELF_CARE: t('recommendations.selfCare'),
    LIFESTYLE: t('recommendations.lifestyle'),
});

// ── Inline recommendations manager (used inside drawer / form) ───────────────
function RecommendationsManager({ condition, t, grouped, onCountChange }) {
    const [linked, setLinked]         = useState([]);
    const [allRecs, setAllRecs]       = useState([]);
    const [loading, setLoading]       = useState(true);
    const [selectedId, setSelectedId] = useState('');
    const [showNewForm, setShowNewForm] = useState(false);
    const [newRec, setNewRec] = useState({ name: '', description: '', type: 'SELF_CARE' });
    const [busy, setBusy] = useState(false);

    const load = async () => {
        try {
            setLoading(true);
            const [linkedRes, allRes] = await Promise.all([
                conditionsAPI.getRecommendations(condition.id),
                recommendationsAPI.getAll(),
            ]);
            setLinked(linkedRes.data);
            setAllRecs(allRes.data);
            onCountChange?.(condition.id, linkedRes.data.length);
        } catch (err) {
            console.error('Failed to load recommendations:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { if (condition?.id) load(); /* eslint-disable-next-line */ }, [condition?.id]);

    const linkedIds = new Set(linked.map(r => r.id));
    const available = allRecs.filter(r => !linkedIds.has(r.id));

    const handleAddExisting = async () => {
        if (!selectedId) return;
        setBusy(true);
        try {
            await conditionsAPI.addRecommendation(condition.id, { recommendation_id: Number(selectedId) });
            setSelectedId('');
            await load();
        } catch (err) {
            console.error('Failed to add recommendation:', err);
        } finally {
            setBusy(false);
        }
    };

    const handleCreateNew = async () => {
        if (!newRec.name.trim() || !newRec.description.trim()) return;
        setBusy(true);
        try {
            const res = await recommendationsAPI.create(newRec);
            const created = res.data.recommendation || res.data;
            await conditionsAPI.addRecommendation(condition.id, { recommendation_id: created.id });
            setNewRec({ name: '', description: '', type: 'SELF_CARE' });
            setShowNewForm(false);
            await load();
        } catch (err) {
            console.error('Failed to create recommendation:', err);
        } finally {
            setBusy(false);
        }
    };

    const handleRemove = async (recId) => {
        setBusy(true);
        try {
            await conditionsAPI.removeRecommendation(condition.id, recId);
            await load();
        } catch (err) {
            console.error('Failed to remove recommendation:', err);
        } finally {
            setBusy(false);
        }
    };

    if (loading) return <div className="rec-manager-loading">{t('common.loading')}</div>;

    return (
        <div className="rec-manager">
            {linked.length === 0 ? (
                <div className="rec-empty">{t('conditions.noRecommendations')}</div>
            ) : grouped ? (
                REC_GROUP_ORDER.map(type => {
                    const items = linked.filter(r => r.type === type);
                    if (items.length === 0) return null;
                    return (
                        <div className="rec-group" key={type}>
                            <div className={`rec-group-header rec-group-header--${type.toLowerCase()}`}>
                                {REC_GROUP_LABEL(t)[type]}
                            </div>
                            <div className="rec-list">
                                {items.map(r => (
                                    <div key={r.id} className="rec-item">
                                        <span className="rec-item-name">{r.name}</span>
                                        <button
                                            className="rec-remove-btn"
                                            disabled={busy}
                                            onClick={() => handleRemove(r.id)}
                                            title={t('common.remove')}
                                        >
                                            <X size={13} strokeWidth={2} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    );
                })
            ) : (
                <div className="rec-list">
                    {linked.map(r => (
                        <div key={r.id} className="rec-item">
                            <div className="rec-item-main">
                                <div className="rec-item-name">{r.name}</div>
                                <div className="rec-item-desc">{r.description}</div>
                                <RecTypeBadge type={r.type} t={t} />
                            </div>
                            <button
                                className="rec-remove-btn"
                                disabled={busy}
                                onClick={() => handleRemove(r.id)}
                                title={t('common.remove')}
                            >
                                <X size={14} strokeWidth={2} />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            <div className="rec-add-row">
                <select
                    className="form-input"
                    value={selectedId}
                    onChange={(e) => setSelectedId(e.target.value)}
                >
                    <option value="">{t('conditions.selectRecommendation')}</option>
                    {available.map(r => (
                        <option key={r.id} value={r.id}>{r.name}</option>
                    ))}
                </select>
                <button className="btn btn--secondary" disabled={!selectedId || busy} onClick={handleAddExisting}>
                    <Plus size={14} strokeWidth={2} /> {t('conditions.addExisting')}
                </button>
            </div>

            {!showNewForm ? (
                <button className="rec-create-toggle" onClick={() => setShowNewForm(true)}>
                    <Plus size={13} strokeWidth={2} /> {t('conditions.createNew')}
                </button>
            ) : (
                <div className="rec-new-form">
                    <input
                        className="form-input"
                        placeholder={t('recommendations.name')}
                        value={newRec.name}
                        onChange={(e) => setNewRec(f => ({ ...f, name: e.target.value }))}
                    />
                    <textarea
                        className="form-input form-textarea"
                        rows={2}
                        placeholder={t('recommendations.description')}
                        value={newRec.description}
                        onChange={(e) => setNewRec(f => ({ ...f, description: e.target.value }))}
                    />
                    <select
                        className="form-input"
                        value={newRec.type}
                        onChange={(e) => setNewRec(f => ({ ...f, type: e.target.value }))}
                    >
                        {RECOMMENDATION_TYPES.map(rt => <option key={rt} value={rt}>{rt}</option>)}
                    </select>
                    <div className="rec-new-form-actions">
                        <button className="btn btn--secondary" onClick={() => setShowNewForm(false)}>{t('common.cancel')}</button>
                        <button className="btn btn--primary" disabled={busy} onClick={handleCreateNew}>{t('common.create')}</button>
                    </div>
                </div>
            )}
        </div>
    );
}

// ── Detail drawer (right-side slide-in) ───────────────────────────────────────
function DetailDrawer({ condition, onEdit, onClose, t, onCountChange }) {
    if (!condition) return null;

    return (
        <div className="drawer-overlay" onClick={onClose}>
            <div className="drawer" onClick={(e) => e.stopPropagation()}>

                <div className="drawer-header">
                    <div>
                        <h3 className="drawer-title">{condition.name}</h3>
                        <div className="drawer-key">{condition.key}</div>
                    </div>
                    <button className="drawer-close" onClick={onClose}>
                        <X size={18} strokeWidth={2} />
                    </button>
                </div>

                <div className="drawer-body">
                    <div className="drawer-pills">
                        <SeverityBadge severity={condition.severity} t={t} />
                        <CategoryBadge category={condition.category} />
                    </div>

                    <div className="drawer-image-placeholder">
                        {condition.image
                            ? <img src={condition.image} alt={condition.image_description || condition.name} className="drawer-image" />
                            : <ImageIcon size={28} strokeWidth={1.5} />}
                    </div>

                    <div className="detail-section">
                        <div className="detail-section-title">
                            <FileText size={13} strokeWidth={1.8} />
                            Description
                        </div>
                        <p className="detail-text">{condition.description}</p>
                    </div>

                    <div className="detail-section">
                        <div className="detail-section-title">
                            <Activity size={13} strokeWidth={1.8} />
                            {t('conditions.symptoms')}
                        </div>
                        <p className="detail-text">{condition.symptoms}</p>
                    </div>

                    <div className="detail-section">
                        <div className="detail-section-title">
                            <ClipboardList size={13} strokeWidth={1.8} />
                            {t('conditions.recommendations')}
                        </div>
                        <RecommendationsManager condition={condition} t={t} grouped onCountChange={onCountChange} />
                    </div>
                </div>

                <div className="drawer-footer">
                    <button className="btn btn--secondary" onClick={onClose}>
                        {t('common.close')}
                    </button>
                    <button className="btn btn--primary" onClick={() => onEdit(condition)}>
                        <Pencil size={14} strokeWidth={1.8} />
                        {t('common.edit')}
                    </button>
                </div>

            </div>
        </div>
    );
}

// ── Form modal (add / edit) ───────────────────────────────────────────────────
function FormModal({ condition, onSave, onClose, t }) {
    const isEdit = !!condition?.id;
    const fileInputRef = useRef(null);

    const [form, setForm] = useState(
        isEdit
            ? {
                key:               condition.key               || '',
                name:              condition.name               || '',
                category:          condition.category           || 'BENIGN',
                severity:          condition.severity           || 'MEDIUM',
                description:       condition.description        || '',
                symptoms:          condition.symptoms           || '',
                image_description: condition.image_description  || '',
            }
            : { ...EMPTY_FORM }
    );

    const [imageFile,    setImageFile]    = useState(null);
    const [imagePreview, setImagePreview] = useState(condition?.image || null);
    const [errors,       setErrors]       = useState({});

    const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        setImageFile(file);
        setImagePreview(URL.createObjectURL(file));
    };

    const handleRemoveImage = () => {
        setImageFile(null);
        setImagePreview(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const validate = () => {
        const e = {};
        if (!form.name.trim())        e.name        = 'Name is required';
        if (!isEdit && !form.key.trim()) e.key      = 'Key is required';
        if (!form.description.trim()) e.description = 'Description is required';
        if (!form.symptoms.trim())    e.symptoms    = 'Symptoms are required';
        setErrors(e);
        return Object.keys(e).length === 0;
    };

    const handleSave = () => {
        if (!validate()) return;

        const formData = new FormData();
        if (!isEdit) formData.append('key', form.key);
        formData.append('name',              form.name);
        formData.append('category',          form.category);
        formData.append('severity',          form.severity);
        formData.append('description',       form.description);
        formData.append('symptoms',          form.symptoms);
        formData.append('image_description', form.image_description);

        if (imageFile) {
            formData.append('image', imageFile);
        }

        onSave({ id: condition?.id, formData });
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-box" onClick={(e) => e.stopPropagation()}>

                <div className="modal-header">
                    <h3 className="modal-title">
                        {isEdit ? t('conditions.editTitle') : t('conditions.addTitle')}
                    </h3>
                    <button className="modal-close" onClick={onClose}>
                        <X size={18} strokeWidth={2} />
                    </button>
                </div>

                <div className="modal-body">

                    {/* Key */}
                    <div className="form-field">
                        <label className="form-label">
                            {t('conditions.key')}
                            {isEdit && <span className="form-optional">({t('conditions.optional')} — {t('common.edit')} disabled)</span>}
                        </label>
                        <input
                            className={`form-input ${errors.key ? 'form-input--error' : ''}`}
                            value={form.key}
                            disabled={isEdit}
                            onChange={(e) => set('key', e.target.value)}
                            placeholder="e.g. melanoma"
                        />
                        {errors.key && <span className="form-error">{errors.key}</span>}
                        {!isEdit && <span className="form-hint">{t('conditions.keyHint')}</span>}
                    </div>

                    {/* Name */}
                    <div className="form-field">
                        <label className="form-label">{t('conditions.conditionName')}</label>
                        <input
                            className={`form-input ${errors.name ? 'form-input--error' : ''}`}
                            value={form.name}
                            onChange={(e) => set('name', e.target.value)}
                        />
                        {errors.name && <span className="form-error">{errors.name}</span>}
                    </div>

                    {/* Category + Severity */}
                    <div className="form-row">
                        <div className="form-field">
                            <label className="form-label">{t('conditions.conditionCategory')}</label>
                            <select
                                className="form-input"
                                value={form.category}
                                onChange={(e) => set('category', e.target.value)}
                            >
                                {CATEGORY_OPTIONS.map((c) => (
                                    <option key={c} value={c}>{c}</option>
                                ))}
                            </select>
                        </div>

                        <div className="form-field">
                            <label className="form-label">{t('conditions.severity')}</label>
                            <select
                                className="form-input"
                                value={form.severity}
                                onChange={(e) => set('severity', e.target.value)}
                            >
                                {SEVERITY_OPTIONS.map((s) => (
                                    <option key={s} value={s}>{s}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Description */}
                    <div className="form-field">
                        <label className="form-label">Description</label>
                        <textarea
                            className={`form-input form-textarea ${errors.description ? 'form-input--error' : ''}`}
                            rows={3}
                            value={form.description}
                            onChange={(e) => set('description', e.target.value)}
                        />
                        {errors.description && <span className="form-error">{errors.description}</span>}
                    </div>

                    {/* Symptoms */}
                    <div className="form-field">
                        <label className="form-label">{t('conditions.symptoms')}</label>
                        <textarea
                            className={`form-input form-textarea ${errors.symptoms ? 'form-input--error' : ''}`}
                            rows={3}
                            value={form.symptoms}
                            onChange={(e) => set('symptoms', e.target.value)}
                        />
                        {errors.symptoms && <span className="form-error">{errors.symptoms}</span>}
                    </div>

                    {/* Image upload */}
                    <div className="form-field">
                        <label className="form-label">
                            Image
                            <span className="form-optional">({t('conditions.optional')})</span>
                        </label>

                        {imagePreview ? (
                            <div className="img-preview-wrap">
                                <img src={imagePreview} alt="preview" className="img-preview" />
                                <button className="img-remove" onClick={handleRemoveImage}>
                                    <X size={12} /> Remove
                                </button>
                            </div>
                        ) : (
                            <div
                                className="img-upload-zone"
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <ImageIcon size={24} strokeWidth={1.5} className="img-upload-icon" />
                                <span className="img-upload-text">Click to upload image</span>
                                <span className="img-upload-sub">PNG, JPG, WEBP up to 10MB</span>
                            </div>
                        )}

                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            className="img-upload-input"
                            onChange={handleFileChange}
                        />
                    </div>

                    {/* Image description */}
                    <div className="form-field">
                        <label className="form-label">
                            Image Description
                            <span className="form-optional">({t('conditions.optional')})</span>
                        </label>
                        <textarea
                            className="form-input form-textarea"
                            rows={2}
                            value={form.image_description}
                            onChange={(e) => set('image_description', e.target.value)}
                        />
                    </div>

                    {isEdit && (
                        <div className="form-field">
                            <label className="form-label">{t('conditions.recommendations')}</label>
                            <RecommendationsManager condition={condition} t={t} />
                        </div>
                    )}

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
function DeleteModal({ condition, onConfirm, onCancel, t }) {
    if (!condition) return null;
    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal-box modal-box--sm" onClick={e => e.stopPropagation()}>
                <div className="modal-warn-icon"><AlertTriangle size={26} color="var(--high)" strokeWidth={1.8} /></div>
                <h3 className="modal-warn-title">{t('conditions.deleteTitle')}</h3>
                <p className="modal-warn-desc">{t('conditions.deleteDesc')} <strong>{condition.name}</strong>? {t('conditions.deleteWarn')}</p>
                <div className="modal-warn-actions">
                    <button className="btn btn--secondary" onClick={onCancel}>{t('common.cancel')}</button>
                    <button className="btn btn--danger" onClick={onConfirm}>{t('common.delete')}</button>
                </div>
            </div>
        </div>
    );
}

// ── Main page ────────────────────────────────────────────────────────────────
export default function Conditions() {

    const { t } = useLang();

    const [conditions, setConditions] = useState([]);
    const [loading,  setLoading]  = useState(true);
    const [recCounts, setRecCounts] = useState({});

    const [modal,    setModal]    = useState(null);
    const [selected, setSelected] = useState(null);

    // ── Fetch ────────────────────────────────────────────────────────────────
    useEffect(() => { fetchConditions(); }, []);

    const fetchConditions = async () => {
        try {
            setLoading(true);
            const response = await conditionsAPI.getAll();
            setConditions(response.data);
        } catch (error) {
            console.error('Failed to fetch conditions:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCountChange = (id, count) => {
        setRecCounts(prev => ({ ...prev, [id]: count }));
    };

    // ── Save ─────────────────────────────────────────────────────────────────
    const handleSave = async ({ id, formData }) => {
        try {
            if (id) {
                await conditionsAPI.partialUpdate(id, formData);
            } else {
                await conditionsAPI.create(formData);
            }
            await fetchConditions();
            setModal(null);
            setSelected(null);
        } catch (error) {
            console.error('Save failed:', error);
        }
    };

    // ── Delete ───────────────────────────────────────────────────────────────
    const handleDelete = async () => {
        try {
            await conditionsAPI.delete(selected.id);
            await fetchConditions();
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
        <div className="conditions-page">

            <div className="page-header">
                <p className="page-subtitle-lg">{conditions.length} {t('conditions.title').toLowerCase()} detected by the model</p>
                <button
                    className="btn btn--primary"
                    onClick={() => { setSelected(null); setModal('form'); }}
                >
                    <Plus size={16} />
                    {t('conditions.addBtn')}
                </button>
            </div>

            {conditions.length === 0 ? (
                <div className="dis-empty">
                    <span className="dis-empty-title">{t('conditions.noConditionsTitle')}</span>
                    <span className="dis-empty-sub">{t('conditions.noConditionsSub')}</span>
                </div>
            ) : (
                <div className="cond-grid">
                    {conditions.map((d) => (
                        <div
                            key={d.id}
                            className={`cond-card ${selected?.id === d.id && modal === 'detail' ? 'cond-card--selected' : ''}`}
                            onClick={() => { setSelected(d); setModal('detail'); }}
                        >
                            <div className="cond-card-top">
                                <SeverityBadge severity={d.severity} t={t} />
                                <CategoryBadge category={d.category} />
                            </div>

                            <h3 className="cond-card-name">{d.name}</h3>
                            <div className="cond-card-key">{d.key}</div>

                            {d.description && (
                                <p className="cond-card-desc">{d.description}</p>
                            )}

                            <div className="cond-card-footer">
                                <span className="cond-card-rec-count">
                                    {recCounts[d.id] != null ? recCounts[d.id] : '—'} {t('conditions.recommendations').toLowerCase()}
                                </span>
                                <div className="cond-card-actions" onClick={(e) => e.stopPropagation()}>
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
                    condition={selected}
                    onSave={handleSave}
                    onClose={() => { setModal(null); setSelected(null); }}
                    t={t}
                />
            )}

            {modal === 'detail' && (
                <DetailDrawer
                    condition={selected}
                    onEdit={(d) => { setSelected(d); setModal('form'); }}
                    onClose={() => { setModal(null); setSelected(null); }}
                    onCountChange={handleCountChange}
                    t={t}
                />
            )}

            {modal === 'delete' && (
                <DeleteModal
                    condition={selected}
                    onConfirm={handleDelete}
                    onCancel={() => { setModal(null); setSelected(null); }}
                    t={t}
                />
            )}

        </div>
    );
}
