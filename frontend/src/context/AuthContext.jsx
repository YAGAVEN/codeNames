// /media/yagaven_25/coding/Projects/codeNames/src/context/AuthContext.jsx
import { createContext, useCallback, useContext, useEffect, useMemo, useReducer } from 'react';
import {
  clearStoredToken,
  completeOAuthLogin,
  fetchCurrentUser,
  getGoogleLoginUrl,
  getStoredToken,
  loginUser,
  logoutUser,
  registerUser
} from '../services/api.js';

const AuthContext = createContext(null);
const storedToken = getStoredToken();

const initialState = {
  user: null,
  token: storedToken,
  status: storedToken ? 'loading' : 'guest',
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
    case 'AUTH_FAILURE':
      return { ...state, status: 'guest', user: null, token: null };
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
    const token = getStoredToken();
    let active = true;

    if (!token) {
      return undefined;
    }

    fetchCurrentUser()
      .then((user) => {
        if (active) {
          dispatch({ type: 'AUTH_SUCCESS', payload: { token, user } });
        }
      })
      .catch(() => {
        clearStoredToken();
        if (active) {
          dispatch({ type: 'AUTH_FAILURE' });
        }
      });

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', state.theme === 'dark');
    document.documentElement.classList.toggle('light', state.theme === 'light');
    document.documentElement.dataset.festival = state.festivalTheme;
  }, [state.festivalTheme, state.theme]);

  const login = useCallback(async (credentials) => {
    dispatch({ type: 'AUTH_LOADING' });
    try {
      const response = await loginUser(credentials);
      dispatch({ type: 'AUTH_SUCCESS', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' });
      throw error;
    }
  }, []);

  const register = useCallback(async (payload) => {
    dispatch({ type: 'AUTH_LOADING' });
    try {
      const response = await registerUser(payload);
      dispatch({ type: 'AUTH_SUCCESS', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' });
      throw error;
    }
  }, []);

  const loginWithGoogle = useCallback(async () => {
    dispatch({ type: 'AUTH_LOADING' });
    try {
      const url = await getGoogleLoginUrl();
      window.location.assign(url);
      return url;
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' });
      throw error;
    }
  }, []);

  const completeOAuth = useCallback(async (payload) => {
    dispatch({ type: 'AUTH_LOADING' });
    try {
      const response = await completeOAuthLogin(payload);
      dispatch({ type: 'AUTH_SUCCESS', payload: response });
      return response;
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' });
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    logoutUser();
    dispatch({ type: 'AUTH_LOGOUT' });
  }, []);

  const value = useMemo(
    () => ({
      ...state,
      login,
      register,
      loginWithGoogle,
      completeOAuth,
      logout,
      setTheme: (theme) => dispatch({ type: 'SET_THEME', payload: theme }),
      setFestivalTheme: (theme) => dispatch({ type: 'SET_FESTIVAL', payload: theme }),
      setLanguage: (language) => dispatch({ type: 'SET_LANGUAGE', payload: language }),
      setSoundEnabled: (enabled) => dispatch({ type: 'SET_SOUND', payload: enabled }),
      setNotificationsEnabled: (enabled) => dispatch({ type: 'SET_NOTIFICATIONS', payload: enabled }),
      updateProfile: (profile) => dispatch({ type: 'UPDATE_PROFILE', payload: profile })
    }),
    [completeOAuth, login, loginWithGoogle, logout, register, state]
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
