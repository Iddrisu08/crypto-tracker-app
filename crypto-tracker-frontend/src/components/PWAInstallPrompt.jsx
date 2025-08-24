import React, { useState, useEffect } from 'react';
import './PWAInstallPrompt.css';

const PWAInstallPrompt = () => {
  const [showInstallButton, setShowInstallButton] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // Check if app is already installed (running in standalone mode)
    const isStandaloneMode = window.matchMedia('(display-mode: standalone)').matches;
    const isIOSStandalone = window.navigator.standalone === true;
    setIsStandalone(isStandaloneMode || isIOSStandalone);

    // Listen for PWA install availability
    const handlePWAInstallable = () => {
      if (!isStandaloneMode && !isIOSStandalone) {
        setShowInstallButton(true);
      }
    };

    window.addEventListener('pwa-installable', handlePWAInstallable);

    // Check if already installable on mount
    if (window.deferredPrompt && !isStandaloneMode && !isIOSStandalone) {
      setShowInstallButton(true);
    }

    return () => {
      window.removeEventListener('pwa-installable', handlePWAInstallable);
    };
  }, []);

  const handleInstall = () => {
    if (window.installPWA) {
      window.installPWA();
      setShowInstallButton(false);
    }
  };

  const handleDismiss = () => {
    setShowInstallButton(false);
  };

  // Don't show if already installed or not available
  if (isStandalone || !showInstallButton) {
    return null;
  }

  return (
    <div className="pwa-install-prompt">
      <div className="install-prompt-content">
        <div className="install-prompt-icon">📱</div>
        <div className="install-prompt-text">
          <h4>Install Crypto Tracker</h4>
          <p>Get the full app experience with offline support and native performance!</p>
        </div>
        <div className="install-prompt-actions">
          <button 
            onClick={handleInstall}
            className="install-btn"
          >
            Install App
          </button>
          <button 
            onClick={handleDismiss}
            className="dismiss-btn"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  );
};

// Offline indicator component
export const OfflineIndicator = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline) return null;

  return (
    <div className="offline-indicator">
      <span className="offline-icon">📡</span>
      <span>Offline - Showing cached data</span>
    </div>
  );
};

export default PWAInstallPrompt;