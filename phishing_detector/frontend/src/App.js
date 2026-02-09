import React, { useState, useEffect } from 'react';
import UploadEmail from './components/UploadEmail';
import ScanResult from './components/ScanResult';
import HistoryTable from './components/HistoryTable';
import EmailDetails from './components/EmailDetails';
import DomainManagement from './components/DomainManagement';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('upload');
  const [scanResult, setScanResult] = useState(null);
  const [selectedEmailId, setSelectedEmailId] = useState(null);
  const [containerInfo, setContainerInfo] = useState(null);

  useEffect(() => {
    fetch('/container-info')
      .then(res => res.json())
      .then(data => setContainerInfo(data))
      .catch(err => console.error('Failed to fetch container info:', err));
  }, [currentView]);

  const handleScanComplete = (result) => {
    setScanResult(result);
    setCurrentView('result');
  };

  const showEmailDetails = (emailId) => {
    setSelectedEmailId(emailId);
    setCurrentView('details');
  };

  return (
    <div className="App">
      <header>
        <div className="header-content">
          <img src="/logo.png" alt="Logo" className="logo" />
          <h1>Phishing Email Detector</h1>
        </div>
        {containerInfo && (
          <div className="container-info">
            <small>Container: {containerInfo.container_id} | Host: {containerInfo.hostname} | Requests: {containerInfo.requests_handled}</small>
          </div>
        )}
        <nav>
          <button onClick={() => setCurrentView('upload')}>Upload Email</button>
          <button onClick={() => setCurrentView('history')}>History</button>
          <button onClick={() => setCurrentView('domains')}>Domain Management</button>
        </nav>
      </header>
      
      <main>
        {currentView === 'upload' && (
          <UploadEmail onScanComplete={handleScanComplete} />
        )}
        {currentView === 'result' && scanResult && (
          <ScanResult result={scanResult} />
        )}
        {currentView === 'history' && (
          <HistoryTable onEmailSelect={showEmailDetails} />
        )}
        {currentView === 'details' && selectedEmailId && (
          <EmailDetails emailId={selectedEmailId} />
        )}
        {currentView === 'domains' && (
          <DomainManagement />
        )}
      </main>
    </div>
  );
}

export default App;