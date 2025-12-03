import React, { useState } from 'react';
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
        <h1>Phishing Email Detector</h1>
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