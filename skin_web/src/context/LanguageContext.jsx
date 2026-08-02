import { createContext, useContext, useState } from 'react';

// ─────────────────────────────────────────────────────────────────────────────
// LanguageContext — MK / EN
// Usage:
//   const { lang, setLang, t } = useLang();
//   t('dashboard.title')  → 'Dashboard' or 'Контролна табла'
//
// Wrap your app root with <LanguageProvider>.
// ─────────────────────────────────────────────────────────────────────────────

const TRANSLATIONS = {
    en: {
        // ── Navigation ───────────────────────────────────────────────────────────
        nav: {
            dashboard:       'Dashboard',
            analyses:        'Analysis History',
            conditions:      'Conditions',
            users:           'Users',
            statistics:      'Statistics',
            settings:        'Settings',
            profile:         'Profile',
            logout:          'Log out',
        },

        // ── Common ────────────────────────────────────────────────────────────────
        common: {
            save:            'Save',
            cancel:          'Cancel',
            delete:          'Delete',
            edit:            'Edit',
            add:             'Add',
            search:          'Search',
            close:           'Close',
            export:          'Export',
            viewAll:         'View All',
            actions:         'Actions',
            loading:         'Loading…',
            noResults:       'No results found',
            confirm:         'Confirm',
            yes:             'Yes',
            no:              'No',
            total:           'Total',
            status:          'Status',
            name:            'Name',
            email:           'Email',
            date:            'Date',
            type:            'Type',
            all:             'All',
            remove:          'Remove',
            create:          'Create',
        },

        // ── Dashboard ─────────────────────────────────────────────────────────────
        dashboard: {
            title:               'Dashboard',
            subtitle:             "Welcome back, Admin. Here's what's happening.",
            totalAnalyses:        'Total Analyses',
            totalUsers:           'Total Users',
            conditionsDetected:   'Conditions Detected',
            accuracyRate:         'Accuracy Rate',
            monthlyTrend:         'Monthly Trend',
            conditionDistribution:'Condition Distribution',
            recentAnalyses:       'Recent Analyses',
            topDetected:          'Top Detected Conditions',
            lowConfidenceRate:    'Low Confidence Rate',
            greetingMorning:      'Good morning',
            greetingAfternoon:    'Good afternoon',
            greetingEvening:      'Good evening',
            heroCaption:          "Here's your platform snapshot for today.",
            accuracyLabel:        'Model Accuracy',
            quickStats:           'Quick Stats',
        },

        // ── Analysis History ──────────────────────────────────────────────────────
        analyses: {
            title:             'Analysis History',
            subtitle:          'View all previous skin condition analyses',
            healthy:           'Healthy',
            allResults:        'All Results',
            allSeverity:       'All Severity',
            lowConfidenceOnly: 'Low Confidence',
            searchPlaceholder: 'Search by ID or condition…',
            results:           'results',
            id:                'ID',
            condition:         'Condition',
            severity:          'Severity',
            confidence:        'Confidence',
            result:            'Result',
            noAnalyses:        'No analyses found',
            noAnalysesSub:     'Try adjusting your search or filter',
            aiConfidence:      'AI Confidence',
            showingFor:        'Showing analyses for',
            clearFilter:       'Clear filter ×',
            lowConfidenceWarn: 'Uncertain result — low model confidence. Consider a follow-up scan or professional review.',
            uncertain:         'Uncertain',
        },

        // ── Conditions ────────────────────────────────────────────────────────────
        conditions: {
            title:             'Conditions',
            subtitle:          'Manage all skin conditions in the system',
            addBtn:            'Add Condition',
            searchPlaceholder: 'Search conditions…',
            allSeverity:       'All Severity',
            allCategories:     'All Categories',
            low:               'Low',
            medium:            'Medium',
            high:              'High',
            severity:          'Severity',
            category:          'Category',
            key:               'Key',
            keyHint:           'Must match the AI model class name. Cannot be changed after creation.',
            symptoms:          'Symptoms',
            recommendations:   'Recommendations',
            noConditionsTitle: 'No conditions found',
            noConditionsSub:   'Try adjusting your search or filter',
            deleteTitle:       'Delete Condition',
            deleteDesc:        'Are you sure you want to delete',
            deleteWarn:        'This cannot be undone.',
            addTitle:          'Add Condition',
            editTitle:         'Edit Condition',
            conditionName:     'Condition Name',
            conditionCategory: 'Category',
            optional:          'optional',
            addExisting:       'Add existing recommendation',
            createNew:         'Create new recommendation',
            noRecommendations: 'No recommendations linked yet',
            selectRecommendation: 'Select a recommendation…',
        },

        // ── Recommendations ───────────────────────────────────────────────────────
        recommendations: {
            title:       'Recommendations',
            name:        'Name',
            description: 'Description',
            type:        'Type',
            selfCare:    'Self Care',
            medical:     'Medical Consult',
            lifestyle:   'Lifestyle',
        },

        // ── Users ─────────────────────────────────────────────────────────────────
        users: {
            title:             'Users',
            subtitle:          'Manage all registered users',
            addBtn:            'Add User',
            searchPlaceholder: 'Search users…',
            allUsers:          'All Users',
            admins:            'Admins',
            regularUsers:      'Users',
            admin:             'Admin',
            user:              'User',
            joined:            'Joined',
            role:              'Role',
            noUsersTitle:      'No users found',
            noUsersSub:        'Try adjusting your search or filter',
            deleteTitle:       'Delete User',
            deleteDesc:        'Are you sure you want to delete',
            deleteWarn:        'This cannot be undone.',
            viewAnalyses:      'View Analyses',
            analyses:          'Analyses',
            username:          'Username',
        },

        // ── Statistics ────────────────────────────────────────────────────────────
        statistics: {
            title:             'Statistics',
            subtitle:          'Platform analytics and insights',
            last7days:         'Last 7 days',
            last30days:        'Last 30 days',
            last3months:       'Last 3 months',
            last12months:      'Last 12 months',
            analysesOverTime:  'Analyses Over Time',
            conditionDistribution: 'Condition Distribution',
            totalAnalyses:     'Total Analyses',
            avgConfidence:     'Avg. Confidence',
            lowConfidenceRate: 'Low Confidence Rate',
            userGrowth:        'User Growth',
            topDetected:       'Top Detected Conditions',
            detectionAccuracy: 'Detection Accuracy',
        },

        // ── Settings ──────────────────────────────────────────────────────────────
        settings: {
            title:             'General Settings',
            subtitle:          'System-wide preferences for the admin panel',
            language:          'Language',
            languageDesc:      'Choose the display language for the admin panel interface',
            appearance:        'Appearance',
            appearanceDesc:    'Toggle between dark and light theme',
            notifications:     'Notifications',
            notificationsDesc: 'Control how and when you receive alerts',
            security:          'Security',
            securityDesc:      'Account security and session preferences',
            emailNotif:        'Email Notifications',
            emailNotifSub:     'Receive email alerts for new analyses',
            pushNotif:         'Push Notifications',
            pushNotifSub:      'Browser push notifications for critical alerts',
            twoFactor:         'Two-Factor Authentication',
            twoFactorSub:      'Require a verification code on every login',
            sessionLog:        'Session Activity Log',
            sessionLogSub:     'Keep a log of all admin login sessions',
            saveBtn:           'Save All Changes',
            savedBtn:          'Changes Saved!',
            darkMode:          'Dark Mode',
            darkModeSub:       'Switch between dark and light interface',
            lightMode:         'Light Mode',
        },

        // ── Profile ───────────────────────────────────────────────────────────────
        profile: {
            title:             'Admin Profile',
            subtitle:          'Manage your personal information and password',
            fullName:          'Full Name',
            phone:             'Phone',
            bio:               'Bio',
            updateBtn:         'Update Profile',
            savedBtn:          'Saved',
            changePassword:    'Change Password',
            currentPw:         'Current Password',
            newPw:             'New Password',
            confirmPw:         'Confirm Password',
            changePwBtn:       'Change Password',
            pwSuccess:         'Password changed successfully!',
            pwErrorRequired:   'All password fields are required.',
            pwErrorLength:     'New password must be at least 6 characters.',
            pwErrorMatch:      'New passwords do not match.',
        },

        // ── Login ─────────────────────────────────────────────────────────────────
        login: {
            title:             'Admin Login',
            subtitle:          'Sign in to your admin account',
            emailLabel:        'Email address',
            passwordLabel:     'Password',
            forgotPassword:    'Forgot password?',
            signInBtn:         'Sign In',
            signingIn:         'Signing in…',
            errorEmpty:        'Please fill in all fields.',
            feature1:          'AI Skin Condition Detection',
            feature2:          'Real-time Analytics',
            feature3:          'User Management',
            feature4:          'Analysis History',
            heroTitle:         'Intelligent Skin Condition Detection',
            heroSub:           'AI-powered admin panel for managing conditions, users and analysis history.',
            headline:          'Clinical oversight for AI-assisted skin screening',
            headlineSub:       'Manage conditions, review analyses, and monitor model performance across your platform.',
        },

        // ── Disclaimer ────────────────────────────────────────────────────────────
        disclaimer: {
            text: 'AI-generated results — not a substitute for professional medical diagnosis.',
        },
    },

    // ══════════════════════════════════════════════════════════════════════════
    mk: {
        // ── Навигација ────────────────────────────────────────────────────────────
        nav: {
            dashboard:       'Контролна табла',
            analyses:        'Историја на анализи',
            conditions:      'Состојби',
            users:           'Корисници',
            statistics:      'Статистики',
            settings:        'Поставки',
            profile:         'Профил',
            logout:          'Одјава',
        },

        // ── Општо ─────────────────────────────────────────────────────────────────
        common: {
            save:            'Зачувај',
            cancel:          'Откажи',
            delete:          'Избриши',
            edit:            'Уреди',
            add:             'Додај',
            search:          'Пребарај',
            close:           'Затвори',
            export:          'Извоз',
            viewAll:         'Прикажи сè',
            actions:         'Акции',
            loading:         'Вчитување…',
            noResults:       'Нема резултати',
            confirm:         'Потврди',
            yes:             'Да',
            no:              'Не',
            total:           'Вкупно',
            status:          'Статус',
            name:            'Име',
            email:           'Е-пошта',
            date:            'Датум',
            type:            'Тип',
            all:             'Сите',
            remove:          'Отстрани',
            create:          'Креирај',
        },

        // ── Контролна табла ───────────────────────────────────────────────────────
        dashboard: {
            title:               'Контролна табла',
            subtitle:             'Добредојдовте, Администратор. Еве што се случува.',
            totalAnalyses:        'Вкупно анализи',
            totalUsers:           'Вкупно корисници',
            conditionsDetected:   'Откриени состојби',
            accuracyRate:         'Точност',
            monthlyTrend:         'Месечен тренд',
            conditionDistribution:'Распределба на состојби',
            recentAnalyses:       'Последни анализи',
            topDetected:          'Најчесто откривани состојби',
            lowConfidenceRate:    'Стапка на ниска доверливост',
            greetingMorning:      'Добро утро',
            greetingAfternoon:    'Добар ден',
            greetingEvening:      'Добра вечер',
            heroCaption:          'Еве преглед на платформата за денес.',
            accuracyLabel:        'Точност на моделот',
            quickStats:           'Брзи статистики',
        },

        // ── Историја на анализи ───────────────────────────────────────────────────
        analyses: {
            title:             'Историја на анализи',
            subtitle:          'Прегледај ги сите претходни анализи на состојби на кожа',
            healthy:           'Здраво',
            allResults:        'Сите резултати',
            allSeverity:       'Сите тежини',
            lowConfidenceOnly: 'Ниска доверливост',
            searchPlaceholder: 'Пребарај по ID или состојба…',
            results:           'резултати',
            id:                'ID',
            condition:         'Состојба',
            severity:          'Тежина',
            confidence:        'Доверливост',
            result:            'Резултат',
            noAnalyses:        'Нема пронајдени анализи',
            noAnalysesSub:     'Обидете се да ги прилагодите вашите филтри',
            aiConfidence:      'AI доверливост',
            showingFor:        'Прикажување анализи за',
            clearFilter:       'Отстрани филтер ×',
            lowConfidenceWarn: 'Несигурен резултат — ниска доверливост на моделот. Разгледајте повторно скенирање или стручен преглед.',
            uncertain:         'Несигурно',
        },

        // ── Состојби ───────────────────────────────────────────────────────────────
        conditions: {
            title:             'Состојби',
            subtitle:          'Управувај со сите состојби на кожа во системот',
            addBtn:            'Додај состојба',
            searchPlaceholder: 'Пребарај состојби…',
            allSeverity:       'Сите тежини',
            allCategories:     'Сите категории',
            low:               'Ниска',
            medium:            'Средна',
            high:              'Висока',
            severity:          'Тежина',
            category:          'Категорија',
            key:               'Клуч',
            keyHint:           'Мора да се совпаѓа со класата на AI моделот. Не може да се менува по креирање.',
            symptoms:          'Симптоми',
            recommendations:   'Препораки',
            noConditionsTitle: 'Нема пронајдени состојби',
            noConditionsSub:   'Обидете се да ги прилагодите вашите филтри',
            deleteTitle:       'Избриши состојба',
            deleteDesc:        'Дали сте сигурни дека сакате да ја избришете',
            deleteWarn:        'Ова не може да се поврати.',
            addTitle:          'Додај состојба',
            editTitle:         'Уреди состојба',
            conditionName:     'Име на состојба',
            conditionCategory: 'Категорија',
            optional:          'опционално',
            addExisting:       'Додај постоечка препорака',
            createNew:         'Креирај нова препорака',
            noRecommendations: 'Нема поврзани препораки',
            selectRecommendation: 'Изберете препорака…',
        },

        // ── Препораки ─────────────────────────────────────────────────────────────
        recommendations: {
            title:       'Препораки',
            name:        'Име',
            description: 'Опис',
            type:        'Тип',
            selfCare:    'Само-нега',
            medical:     'Медицинска консултација',
            lifestyle:   'Начин на живот',
        },

        // ── Корисници ─────────────────────────────────────────────────────────────
        users: {
            title:             'Корисници',
            subtitle:          'Управувај со сите регистрирани корисници',
            addBtn:            'Додај корисник',
            searchPlaceholder: 'Пребарај корисници…',
            allUsers:          'Сите корисници',
            admins:            'Администратори',
            regularUsers:      'Корисници',
            admin:             'Администратор',
            user:              'Корисник',
            joined:            'Зачленет',
            role:              'Улога',
            noUsersTitle:      'Нема пронајдени корисници',
            noUsersSub:        'Обидете се да ги прилагодите вашите филтри',
            deleteTitle:       'Избриши корисник',
            deleteDesc:        'Дали сте сигурни дека сакате да го избришете',
            deleteWarn:        'Ова не може да се поврати.',
            viewAnalyses:      'Прикажи анализи',
            analyses:          'Анализи',
            username:          'Корисничко име',
        },

        // ── Статистики ────────────────────────────────────────────────────────────
        statistics: {
            title:             'Статистики',
            subtitle:          'Аналитика и увиди за платформата',
            last7days:         'Последни 7 дена',
            last30days:        'Последни 30 дена',
            last3months:       'Последни 3 месеци',
            last12months:      'Последни 12 месеци',
            analysesOverTime:  'Анализи низ времето',
            conditionDistribution: 'Распределба на состојби',
            totalAnalyses:     'Вкупно анализи',
            avgConfidence:     'Просечна доверливост',
            lowConfidenceRate: 'Стапка на ниска доверливост',
            userGrowth:        'Раст на корисници',
            topDetected:       'Најчесто откривани состојби',
            detectionAccuracy: 'Точност на детекција',
        },

        // ── Поставки ──────────────────────────────────────────────────────────────
        settings: {
            title:             'Општи поставки',
            subtitle:          'Системски преференци за административниот панел',
            language:          'Јазик',
            languageDesc:      'Изберете јазик за приказ на административниот панел',
            appearance:        'Изглед',
            appearanceDesc:    'Префрлете помеѓу темна и светла тема',
            notifications:     'Известувања',
            notificationsDesc: 'Контролирајте кога и како добивате известувања',
            security:          'Безбедност',
            securityDesc:      'Безбедност на сметката и сесиски преференци',
            emailNotif:        'Известувања по е-пошта',
            emailNotifSub:     'Примај известувања по е-пошта за нови анализи',
            pushNotif:         'Push известувања',
            pushNotifSub:      'Известувања во прелистувачот за критични предупредувања',
            twoFactor:         'Двофакторска автентикација',
            twoFactorSub:      'Побарај верификациски код на секоја најава',
            sessionLog:        'Дневник на активноста на сесии',
            sessionLogSub:     'Чувај дневник на сите администраторски сесии',
            saveBtn:           'Зачувај ги промените',
            savedBtn:          'Промените се зачувани!',
            darkMode:          'Темен режим',
            darkModeSub:       'Префрлете помеѓу темен и светол интерфејс',
            lightMode:         'Светол режим',
        },

        // ── Профил ────────────────────────────────────────────────────────────────
        profile: {
            title:             'Администраторски профил',
            subtitle:          'Управувај со личните информации и лозинката',
            fullName:          'Целосно име',
            phone:             'Телефон',
            bio:               'Биографија',
            updateBtn:         'Ажурирај профил',
            savedBtn:          'Зачувано',
            changePassword:    'Промени лозинка',
            currentPw:         'Тековна лозинка',
            newPw:             'Нова лозинка',
            confirmPw:         'Потврди лозинка',
            changePwBtn:       'Промени лозинка',
            pwSuccess:         'Лозинката е успешно сменета!',
            pwErrorRequired:   'Сите полиња за лозинка се задолжителни.',
            pwErrorLength:     'Новата лозинка мора да содржи најмалку 6 знаци.',
            pwErrorMatch:      'Новите лозинки не се совпаѓаат.',
        },

        // ── Најава ────────────────────────────────────────────────────────────────
        login: {
            title:             'Администраторска најава',
            subtitle:          'Најавете се на вашата администраторска сметка',
            emailLabel:        'Е-пошта адреса',
            passwordLabel:     'Лозинка',
            forgotPassword:    'Заборавена лозинка?',
            signInBtn:         'Најави се',
            signingIn:         'Најавување…',
            errorEmpty:        'Ве молиме пополнете ги сите полиња.',
            feature1:          'AI Откривање состојби на кожа',
            feature2:          'Аналитика во реално време',
            feature3:          'Управување со корисници',
            feature4:          'Историја на анализи',
            heroTitle:         'Интелигентно откривање состојби на кожа',
            heroSub:           'AI-базиран административен панел за управување со состојби, корисници и историја на анализи.',
            headline:          'Клинички надзор за AI-асистирано скенирање на кожа',
            headlineSub:       'Управувајте со состојби, прегледувајте анализи и следете ги перформансите на моделот низ вашата платформа.',
        },

        // ── Одрекување ────────────────────────────────────────────────────────────
        disclaimer: {
            text: 'Резултати генерирани со AI — не претставуваат замена за професионална медицинска дијагноза.',
        },
    },
};

// ─────────────────────────────────────────────────────────────────────────────
const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
    const [lang, setLang] = useState(() => {
        return localStorage.getItem('skinscan-lang') || 'en';
    });

    const changeLang = (newLang) => {
        setLang(newLang);
        localStorage.setItem('skinscan-lang', newLang);
    };

    // t('settings.title') → translated string
    const t = (key) => {
        const parts = key.split('.');
        let val = TRANSLATIONS[lang];
        for (const p of parts) {
            val = val?.[p];
        }
        // fallback to English if key missing
        if (val === undefined) {
            let fb = TRANSLATIONS['en'];
            for (const p of parts) fb = fb?.[p];
            return fb ?? key;
        }
        return val;
    };

    return (
        <LanguageContext.Provider value={{ lang, setLang: changeLang, t }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLang() {
    const ctx = useContext(LanguageContext);
    if (!ctx) throw new Error('useLang must be used inside <LanguageProvider>');
    return ctx;
}
