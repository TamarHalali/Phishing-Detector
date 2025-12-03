import React from 'react';

function ScanResult({ result }) {
  const { parsed_email, ai_analysis } = result;
  
  const getRiskClass = (score) => {
    if (score < 30) return 'risk-low';
    if (score < 70) return 'risk-medium';
    return 'risk-high';
  };

  const getRiskLevel = (score) => {
    if (score < 30) return 'Low Risk';
    if (score < 70) return 'Medium Risk';
    return 'High Risk';
  };

  const getRiskIcon = (score) => {
    if (score < 30) return '✅';
    if (score < 70) return '⚠️';
    return '🚨';
  };

  return (
    <div className="scan-result">
      <h2>📊 Scan Results</h2>
      
      <div className={`${getRiskClass(ai_analysis.score)}`}>
        <div className="risk-score-container">
          <div className="risk-score">
            {getRiskIcon(ai_analysis.score)} {ai_analysis.score}/100
          </div>
          <div className="risk-level">
            {getRiskLevel(ai_analysis.score)}
          </div>
        </div>
      </div>
      
      <div className="email-field">
        <label>🤖 AI Analysis Summary:</label>
        <p>{ai_analysis.summary}</p>
      </div>

      {ai_analysis.indicators && ai_analysis.indicators.length > 0 && (
        <div className="email-field">
          <label>🚨 Phishing Indicators Found:</label>
          <ul style={{color: '#dc3545', fontWeight: '600'}}>
            {ai_analysis.indicators.map((indicator, index) => (
              <li key={index}>{indicator}</li>
            ))}
          </ul>
        </div>
      )}

      {ai_analysis.detections && ai_analysis.detections.length > 0 && (
        <div className="virustotal-results">
          <h3>🛡️ Security Vendor Detections</h3>
          {ai_analysis.detections.map((detection, index) => (
            <div key={index} className="detection-item">
              <span className="detection-vendor">{detection[0]}</span>
              <span className="detection-result">{detection[1]}</span>
            </div>
          ))}
        </div>
      )}

      <div className="analysis-details">
        <div className="detail-card">
          <h3>📧 Sender Information</h3>
          <p><strong>From:</strong> {parsed_email.sender}</p>
        </div>
        
        <div className="detail-card">
          <h3>📝 Subject Line</h3>
          <p>{parsed_email.subject}</p>
        </div>
        
        {ai_analysis.url_analysis && ai_analysis.url_analysis.length > 0 && (
          <div className="detail-card">
            <h3>🔗 URL Analysis ({ai_analysis.url_analysis.length})</h3>
            {ai_analysis.url_analysis.map((urlResult, index) => (
              <div key={index} style={{
                background: urlResult.is_malicious ? '#fff5f5' : '#f8f9fa',
                padding: '15px',
                margin: '10px 0',
                borderRadius: '8px',
                border: urlResult.is_malicious ? '2px solid #dc3545' : '1px solid #dee2e6'
              }}>
                <div style={{marginBottom: '10px'}}>
                  <strong>Original:</strong> {urlResult.original_url}
                </div>
                {urlResult.is_shortened && (
                  <div style={{marginBottom: '10px', color: '#ffc107'}}>
                    <strong>⚠️ Shortened URL expands to:</strong> {urlResult.expanded_url}
                  </div>
                )}
                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                  <span style={{
                    color: urlResult.is_malicious ? '#dc3545' : '#28a745',
                    fontWeight: '600'
                  }}>
                    Risk Score: {urlResult.risk_score}/100
                  </span>
                  {urlResult.is_malicious && (
                    <span style={{
                      background: '#dc3545',
                      color: 'white',
                      padding: '4px 8px',
                      borderRadius: '12px',
                      fontSize: '12px'
                    }}>
                      🚨 MALICIOUS
                    </span>
                  )}
                </div>
                {urlResult.detections && urlResult.detections.length > 0 && (
                  <div style={{marginTop: '10px'}}>
                    <strong>Detections:</strong>
                    <ul style={{margin: '5px 0', paddingLeft: '20px'}}>
                      {urlResult.detections.map((detection, detIndex) => (
                        <li key={detIndex} style={{color: '#dc3545'}}>
                          {detection[0]}: {detection[1]}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        
        {parsed_email.attachments.length > 0 && (
          <div className="detail-card">
            <h3>📎 Attachments ({parsed_email.attachments.length})</h3>
            <ul className="attachments-list">
              {parsed_email.attachments.map((att, index) => (
                <li key={index}>
                  <strong>{att.filename}</strong> ({att.content_type})
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="detail-card" style={{gridColumn: '1 / -1'}}>
          <h3>📄 Email Content</h3>
          <p style={{whiteSpace: 'pre-wrap', maxHeight: '300px', overflow: 'auto'}}>
            {parsed_email.body}
          </p>
        </div>
      </div>
    </div>
  );
}

export default ScanResult;