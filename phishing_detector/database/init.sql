CREATE DATABASE IF NOT EXISTS phishing_db;
USE phishing_db;

CREATE TABLE IF NOT EXISTS untrusted_domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain VARCHAR(255) UNIQUE NOT NULL,
    risk_score INTEGER DEFAULT 50
);

CREATE TABLE IF NOT EXISTS untrusted_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url VARCHAR(500) UNIQUE NOT NULL,
    risk_score INTEGER DEFAULT 50
);

CREATE TABLE IF NOT EXISTS emails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender VARCHAR(255) NOT NULL,
    subject TEXT,
    body TEXT,
    urls TEXT,
    attachments TEXT,
    ai_score INT,
    ai_summary TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample untrusted domains
INSERT INTO untrusted_domains (domain, risk_score) VALUES 
('tempmail.com', 80),
('guerrillamail.com', 85),
('10minutemail.com', 90),
('mailinator.com', 75);

-- Insert sample untrusted URLs
INSERT INTO untrusted_urls (url, risk_score) VALUES 
('http://bit.ly/suspicious', 70),
('http://tinyurl.com/phish', 75),
('https://fake-bank.com', 95);