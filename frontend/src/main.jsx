// /media/yagaven_25/coding/Projects/codeNames/src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { App } from './App.jsx';
import { AuthProvider } from './context/AuthContext.jsx';
import { GameProvider } from './context/GameContext.jsx';
import { SocketProvider } from './context/SocketContext.jsx';
import { ToastProvider } from './components/ui/Toast.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <SocketProvider>
          <GameProvider>
            <ToastProvider>
              <App />
            </ToastProvider>
          </GameProvider>
        </SocketProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
