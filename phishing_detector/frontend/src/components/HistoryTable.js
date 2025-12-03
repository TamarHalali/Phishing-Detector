import React, { useState, useEffect } from 'react';
import axios from 'axios';

function HistoryTable({ onEmailSelect }) {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get('/history');
      setEmails(response.data);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskClass = (score) => {
    if (score < 30) return 'risk-low';
    if (score < 70) return 'risk-medium';
    return 'risk-high';
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Scan History</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Sender</th>
            <th>Subject</th>
            <th>Risk Score</th>
            <th>Summary</th>
          </tr>
        </thead>
        <tbody>
          {emails.map(email => (
            <tr key={email.id} onClick={() => onEmailSelect(email.id)}>
              <td>{new Date(email.timestamp).toLocaleDateString()}</td>
              <td>{email.sender}</td>
              <td>{email.subject}</td>
              <td className={getRiskClass(email.ai_score)}>
                {email.ai_score}/100
              </td>
              <td>{email.ai_summary}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default HistoryTable;