# Phishing Detector

## מערכת זיהוי דוא"ל פישינג מתקדמת

מערכת מתקדמת לזיהוי וניתוח דוא"ל פישינג באמצעות בינה מלאכותית (Gemini AI) ו-VirusTotal API.

## תכונות עיקריות

- **ניתוח AI מתקדם**: שימוש ב-Gemini AI לניתוח תוכן הדוא"ל
- **בדיקת דומיינים**: אימות דומיינים באמצעות VirusTotal API
- **מסד נתונים**: שמירת תוצאות ניתוח ב-MySQL
- **Load Balancing**: 3 instances של backend עם Nginx
- **CI/CD**: GitHub Actions עם deployment אוטומטי ל-EC2
- **Security Scanning**: סריקת אבטחה אוטומטית של dependencies ו-Docker images

## מבנה הפרויקט

```
Phishing-Detector/
├── phishing_detector/
│   ├── backend/          # Flask API server
│   ├── frontend/         # React application
│   ├── docker-compose.yml
│   └── nginx.conf
├── .github/
│   └── workflows/        # CI/CD pipelines
└── README.md
```

## ניהול גרסאות Docker Images

### איך זה עובד:
- **גרסאות אוטומטיות**: כל push ל-main יוצר גרסה חדשה בפורמט `1.0.X`
- **חישוב גרסה**: מבוסס על מספר ה-commits בפרויקט
- **Tags**: כל image מקבל גם tag של הגרסה וגם `latest`

### דוגמה:
- Commit #45 → גרסה `1.0.45`
- Commit #46 → גרסה `1.0.46`

### Docker Hub Images:
- `tamarhalali/phishing-detector-backend:1.0.X`
- `tamarhalali/phishing-detector-frontend:1.0.X`
- `tamarhalali/phishing-detector-nginx:1.0.X`

**הערה**: Docker Hub שומר מספר מוגבל של גרסאות. הגרסאות החדשות יותר יהיו עם מספרים גבוהים יותר.

## הרצה מקומית

1. **Clone הפרויקט**:
```bash
git clone <repository-url>
cd Phishing-Detector/phishing_detector
```

2. **הגדרת משתני סביבה**:
```bash
export MYSQL_ROOT_PASSWORD=your_root_password
export MYSQL_PASSWORD=your_password
export GEMINI_API_KEY=your_gemini_key
export VIRUSTOTAL_API_KEY=your_virustotal_key
```

3. **הרצה עם Docker Compose**:
```bash
docker-compose up -d --build
```

## API Endpoints

- `GET /health` - בדיקת תקינות המערכת
- `POST /analyze-email` - ניתוח דוא"ל
- `GET /history` - היסטוריית ניתוחים
- `GET /container-info` - מידע על ה-container

## טסטים

```bash
cd phishing_detector/backend
python -m pytest tests/ -v
```

## Deployment

הפרויקט מתפרס אוטומטיות ל-EC2 באמצעות GitHub Actions כאשר יש push ל-main branch.

## אבטחה

- סריקת dependencies אוטומטית
- סריקת Docker images עם Trivy
- דוחות אבטחה מפורטים
- עדכונים אוטומטיים של חבילות פגיעות

## Database Tests Added

נוספו טסטים מקיפים למסד הנתונים כולל:
- בדיקת חיבור למסד נתונים
- יצירת רשומות
- בדיקת API endpoints
- אימות תקינות המערכת
