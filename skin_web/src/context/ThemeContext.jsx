import { createContext, useContext, useState, useEffect, useCallback } from 'react';

// ─────────────────────────────────────────────────────────────────────────────
// ThemeContext — глобален dark/light mode
// Топла cosmetics/beauty палета (крем/беж + бордо акценти)
//
// Light mode бои:
//   background: #F3E7DA
//   cardBg:     #FFFFFF
//   textDark:   #2B1810
//   textMuted:  #8C7568
//   border:     #E5D5C5
//   brand:      #8B2E42 (бордо)
//
// Dark mode бои:
//   background: #1C1310
//   cardBg:     #2A1E1A
//   textDark:   #F3E7DA
//   textMuted:  #A8927F
//   border:     #332420
// ─────────────────────────────────────────────────────────────────────────────

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('ss_theme');
    return saved ? saved === 'dark' : false; // default light
  });

  // Apply theme class to <html> element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    localStorage.setItem('ss_theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggleTheme = useCallback(() => setIsDark(v => !v), []);

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
