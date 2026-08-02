import { createContext, useContext, useState, useCallback } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('ss_token'));
  const [user,  setUser]  = useState(() => {
    try { return JSON.parse(localStorage.getItem('ss_user')); }
    catch { return null; }
  });

  const login = useCallback((tok, usr) => {
    localStorage.setItem('ss_token', tok);
    localStorage.setItem('ss_user',  JSON.stringify(usr));
    setToken(tok);
    setUser(usr);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('ss_token');
    localStorage.removeItem('ss_user');
    localStorage.removeItem('ss_refresh');
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
