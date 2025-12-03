import React, { useState, useEffect } from 'react';
import axios from 'axios';

function DomainManagement() {
  const [maliciousDomains, setMaliciousDomains] = useState([]);
  const [whitelistedDomains, setWhitelistedDomains] = useState([]);
  const [newDomain, setNewDomain] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDomains();
  }, []);

  const fetchDomains = async () => {
    try {
      const [maliciousRes, whitelistRes] = await Promise.all([
        axios.get('/malicious_domains'),
        axios.get('/whitelisted_domains')
      ]);
      setMaliciousDomains(maliciousRes.data);
      setWhitelistedDomains(whitelistRes.data);
    } catch (error) {
      console.error('Error fetching domains:', error);
    }
  };

  const whitelistDomain = async (domain) => {
    setLoading(true);
    try {
      await axios.post('/whitelist_domain', { domain });
      await fetchDomains();
      alert(`Domain ${domain} whitelisted successfully`);
    } catch (error) {
      alert('Error whitelisting domain: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const removeFromWhitelist = async (domain) => {
    setLoading(true);
    try {
      await axios.post('/remove_whitelist', { domain });
      await fetchDomains();
      alert(`Domain ${domain} removed from whitelist`);
    } catch (error) {
      alert('Error removing from whitelist: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const addToWhitelist = async () => {
    if (!newDomain.trim()) return;
    
    setLoading(true);
    try {
      await axios.post('/whitelist_domain', { domain: newDomain.trim() });
      setNewDomain('');
      await fetchDomains();
      alert(`Domain ${newDomain} added to whitelist`);
    } catch (error) {
      alert('Error adding to whitelist: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>🛡️ Domain Management</h2>
      
      {/* Add to Whitelist Section */}
      <div className="detail-card" style={{marginBottom: '30px'}}>
        <h3>➕ Add Domain to Whitelist</h3>
        <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
          <input
            type="text"
            value={newDomain}
            onChange={(e) => setNewDomain(e.target.value)}
            placeholder="Enter domain (e.g., example.com)"
            style={{
              flex: 1,
              padding: '10px',
              border: '2px solid #667eea',
              borderRadius: '8px',
              fontSize: '14px'
            }}
          />
          <button
            onClick={addToWhitelist}
            disabled={!newDomain.trim() || loading}
            style={{
              background: 'linear-gradient(45deg, #28a745, #20c997)',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Add to Whitelist
          </button>
        </div>
      </div>

      {/* Malicious Domains Section */}
      <div className="detail-card" style={{marginBottom: '30px'}}>
        <h3>🚨 Detected Malicious Domains ({maliciousDomains.length})</h3>
        {maliciousDomains.length === 0 ? (
          <p style={{color: '#6c757d', fontStyle: 'italic'}}>No malicious domains detected yet</p>
        ) : (
          <div style={{maxHeight: '300px', overflowY: 'auto'}}>
            {maliciousDomains.map((domain, index) => (
              <div key={index} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px',
                margin: '8px 0',
                background: '#fff5f5',
                border: '1px solid #dc3545',
                borderRadius: '8px'
              }}>
                <span style={{fontWeight: '600', color: '#dc3545'}}>
                  🚫 {domain}
                </span>
                <button
                  onClick={() => whitelistDomain(domain)}
                  disabled={loading}
                  style={{
                    background: '#28a745',
                    color: 'white',
                    border: 'none',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  Whitelist
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Whitelisted Domains Section */}
      <div className="detail-card">
        <h3>✅ Whitelisted Domains ({whitelistedDomains.length})</h3>
        {whitelistedDomains.length === 0 ? (
          <p style={{color: '#6c757d', fontStyle: 'italic'}}>No domains whitelisted yet</p>
        ) : (
          <div style={{maxHeight: '300px', overflowY: 'auto'}}>
            {whitelistedDomains.map((domain, index) => (
              <div key={index} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px',
                margin: '8px 0',
                background: '#f8fff8',
                border: '1px solid #28a745',
                borderRadius: '8px'
              }}>
                <span style={{fontWeight: '600', color: '#28a745'}}>
                  ✅ {domain}
                </span>
                <button
                  onClick={() => removeFromWhitelist(domain)}
                  disabled={loading}
                  style={{
                    background: '#dc3545',
                    color: 'white',
                    border: 'none',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default DomainManagement;