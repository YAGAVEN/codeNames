// /media/yagaven_25/coding/Projects/codeNames/src/context/AuthContext.jsx
import { createContext, useCallback, useContext, useEffect, useMemo, useReducer } from 'react';
import { mockPlayers } from '../data/mockPlayers.js';
import { loginUser, registerUser } from '../services/api.js';

const AuthContext = createContext(null);

const initialState = {
  user: mockPlayers[0],
  token: 'mock-token-codenames-india',
  status: 'authenticated',
  theme: 'dark',
  festivalTheme: 'diwali',
  language: 'en',
  soundEnabled: true,
  notificationsEnabled: true
};

const authReducer = (state, action) => {
  switch (action.type) {
    case 'AUTH_LOADING':
      return { ...state, status: 'loading' };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        status: 'authenticated',
        user: action.payload.user,
        token: action.payload.token
      };
    case 'AUTH_LOGOUT':
      return { ...state, status: 'guest', user: null, token: null };
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    case 'SET_FESTIVAL':
      return { ...state, festivalTheme: action.payload };
    case 'SET_LANGUAGE':
      return { ...state, language: action.payload };
    case 'SET_SOUND':
      return { ...state, soundEnabled: action.payload };
    case 'SET_NOTIFICATIONS':
      return { ...state, notificationsEnabled: action.payload };
    case 'UPDATE_PROFILE':
      return { ...state, user: { ...state.user, ...action.payload } };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', state.theme === 'dark');
    document.documentElement.classList.toggle('light', state.theme === 'light');
    document.documentElement.dataset.festival = state.festivalTheme;
  }, [state.festivalTheme, state.theme]);

  const login = useCallback(async (credentials) => {
    dispatch({ type: 'AUTH_LOADING' });
    const response = await loginUser(credentials);
    dispatch({ type: 'AUTH_SUCCESS', payload: response });
    return response;
  }, []);

  const register = useCallback(async (payload) => {
    dispatch({ type: 'AUTH_LOADING' });
    const response = await registerUser(payload);
    dispatch({ type: 'AUTH_SUCCESS', payload: response });
    return response;
  }, []);

  const value = useMemo(
    () => ({
      ...state,
      login,
      register,
      logout: () => dispatch({ type: 'AUTH_LOGOUT' }),
      setTheme: (theme) => dispatch({ type: 'SET_THEME', payload: theme }),
      setFestivalTheme: (theme) => dispatch({ type: 'SET_FESTIVAL', payload: theme }),
      setLanguage: (language) => dispatch({ type: 'SET_LANGUAGE', payload: language }),
      setSoundEnabled: (enabled) => dispatch({ type: 'SET_SOUND', payload: enabled }),
      setNotificationsEnabled: (enabled) => dispatch({ type: 'SET_NOTIFICATIONS', payload: enabled }),
      updateProfile: (profile) => dispatch({ type: 'UPDATE_PROFILE', payload: profile })
    }),
    [login, register, state]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuthContext must be used inside AuthProvider');
  }

  return context;
};
