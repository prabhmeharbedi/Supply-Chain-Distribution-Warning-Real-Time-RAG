import React, { useEffect } from 'react';
import { AppProvider } from './contexts/AppContext';
import Layout from './components/Layout/Layout';

function App() {
  useEffect(() => {
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  return (
    <AppProvider>
      <Layout />
    </AppProvider>
  );
}

export default App;