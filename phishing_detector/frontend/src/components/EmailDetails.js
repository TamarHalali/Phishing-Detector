import React, { useState, useEffect } from 'react';
import axios from 'axios';

function EmailDetails({ emailId }) {
  const [email, setEmail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEmailDetails();
  }, [emailId]);

  const fetchEmailDetails = async () => {
    try {
      const response = await axios.get(`/email/${emailId}`);
      setEmail(response.data);
    } catch (error) {
      console.error('Error fetching email details:', error);
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) return <div className="loading">Loading...</div>;
  if (!email) return <div>Email not found</div>;

  // Handle both old and new data structure
  const emailData = email.parsed_email || email;
  const aiData = email.ai_analysis || email;

  return (
    <div className="scan-result">
      <h2>📊 Email Analysis Details</h2>
      
      <div className={`${getRiskClass(aiData.ai_score || aiData.score)}`}>
        <div className="risk-score-container">
          <div className="risk-score">
            {getRiskIcon(aiData.ai_score || aiData.score)} {aiData.ai_score || aiData.score}/100
          </div>
          <div className="risk-level">
            {getRiskLevel(aiData.ai_score || aiData.score)}
          </div>
        </div>
      </div>
      
      <div className="email-field">
        <label>🤖 AI Analysis Summary:</label>
        <p>{aiData.ai_summary || aiData.summary}</p>
      </div>

      <div className="email-field">
        <label>📅 Scan Date:</label>
        <p>{new Date(email.timestamp).toLocaleString()}</p>
      </div>

      {aiData.indicators && aiData.indicators.length > 0 && (
        <div className="email-field">
          <label>🚨 Phishing Indicators Found:</label>
          <ul style={{color: '#dc3545', fontWeight: '600'}}>
            {aiData.indicators.map((indicator, index) => (
              <li key={index}>{indicator}</li>
            ))}
          </ul>
        </div>
      )}

      {aiData.detections && aiData.detections.length > 0 && (
        <div className="virustotal-results">
          <h3>🛡️ Security Vendor Detections</h3>
          {aiData.detections.map((detection, index) => (
            <div key={index} className="detection-item">
              <span className="detection-vendor">{detection[0]}</span>
              <span className="detection-result">{detection[1]}</span>
            </div>
          ))}
        </div>
      )}

      <div style={{display: 'flex', flexWrap: 'wrap', gap: '20px', margin: '30px 0'}}>
        <div style={{flex: '0 1 auto', minWidth: '200px', maxWidth: '400px'}} className="detail-card">
          <h3>📧 Sender Information</h3>
          <p><strong>From:</strong> {emailData.sender}</p>
        </div>
        
        <div style={{flex: '1 1 300px', minWidth: '300px'}} className="detail-card">
          <h3>📝 Subject Line</h3>
          <p>{emailData.subject}</p>
        </div>
      </div>
      
      {aiData.url_analysis && aiData.url_analysis.length > 0 && (
        <div className="detail-card" style={{width: '100%', maxWidth: 'none'}}>
          <h3>🔗 URL Analysis ({aiData.url_analysis.length})</h3>
          {aiData.url_analysis.map((urlResult, index) => (
            <div key={index} style={{
              background: urlResult.is_malicious ? '#fff5f5' : '#f8f9fa',
              padding: '15px',
              margin: '10px 0',
              borderRadius: '8px',
              border: urlResult.is_malicious ? '2px solid #dc3545' : '1px solid #dee2e6'
            }}>
              <div style={{marginBottom: '10px', wordBreak: 'break-all', overflowWrap: 'break-word'}}>
                <strong>Original:</strong> {urlResult.original_url}
              </div>
              {urlResult.is_shortened && (
                <div style={{marginBottom: '10px', color: '#ffc107', wordBreak: 'break-all', overflowWrap: 'break-word'}}>
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
            </div>
          ))}
        </div>
      )}
        
      <div style={{display: 'flex', flexWrap: 'wrap', gap: '20px', margin: '20px 0'}}>
        {emailData.urls && emailData.urls.length > 0 && !aiData.url_analysis && (
          <div style={{flex: '1 1 300px'}} className="detail-card">
            <h3>🔗 URLs Found ({emailData.urls.length})</h3>
            <ul className="urls-list">
              {emailData.urls.map((url, index) => (
                <li key={index}>{url}</li>
              ))}
            </ul>
          </div>
        )}
        
        {emailData.attachments && emailData.attachments.length > 0 && (
          <div style={{flex: '0 1 auto', minWidth: '250px'}} className="detail-card">
            <h3>📎 Attachments ({emailData.attachments.length})</h3>
            <ul className="attachments-list">
              {emailData.attachments.map((att, index) => (
                <li key={index}>
                  <strong>{att.filename}</strong> ({att.content_type})
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      <div className="detail-card" style={{width: '100%', maxWidth: 'none'}}>
        <h3>📄 Email Content</h3>
        <p style={{whiteSpace: 'pre-wrap', maxHeight: '300px', overflow: 'auto'}}>
          {emailData.body}
        </p>
      </div>
    </div>
  );
}

export default EmailDetails;