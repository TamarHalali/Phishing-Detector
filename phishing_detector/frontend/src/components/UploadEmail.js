import React, { useState } from 'react';
import axios from 'axios';

function UploadEmail({ onScanComplete }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.name.endsWith('.eml')) {
      setFile(droppedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/upload_email', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      onScanComplete(response.data);
    } catch (error) {
      alert('Error uploading file: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>📧 Upload Email File for Analysis</h2>
      <div 
        className={`upload-area ${dragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div style={{fontSize: '3em', marginBottom: '20px'}}>
          📁
        </div>
        <input
          type="file"
          accept=".eml"
          onChange={handleFileChange}
          style={{margin: '20px 0', padding: '10px'}}
        />
        {file && (
          <p style={{marginTop: '15px', color: '#28a745', fontWeight: '600'}}>
            ✓ Selected: {file.name}
          </p>
        )}
        <p style={{color: '#6c757d', fontSize: '14px', marginTop: '10px'}}>
          Upload email files (.eml format) to analyze for phishing indicators
        </p>
        <br/>
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          style={{
            background: loading ? '#6c757d' : 'linear-gradient(45deg, #28a745, #20c997)',
            color: 'white',
            border: 'none',
            padding: '15px 30px',
            borderRadius: '25px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            marginTop: '20px'
          }}
        >
          {loading ? '🔍 Analyzing...' : '🚀 Upload & Analyze'}
        </button>
      </div>
    </div>
  );
}

export default UploadEmail;