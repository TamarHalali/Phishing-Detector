# קבצים מיותרים/כפולים בפרויקט - סקירה

## קבצים שזוהו כמיותרים (מומלץ למחוק):

### 1. קבצי VS Code/Docker Extension (לא בשימוש)
- **`Dockerfile`** (בשורש) - קובץ VS Code extension שלא בשימוש. הפרויקט משתמש ב-`phishing_detector/backend/Dockerfile` ו-`phishing_detector/frontend/Dockerfile`
- **`compose.yaml`** (בשורש) - קובץ VS Code extension שלא בשימוש. הפרויקט משתמש ב-`phishing_detector/docker-compose.yml`
- **`compose.debug.yaml`** (בשורש) - קובץ VS Code extension שלא בשימוש

### 2. קובץ requirements ישן (לא בשימוש)
- **`requirements.txt`** (בשורש) - קובץ ישן עם רק flask ו-gunicorn. הפרויקט משתמש ב-`phishing_detector/backend/requirements.txt`

### 3. קובץ test ישן (לא בשימוש)
- **`phishing_detector/test_db.py`** - קובץ test ישן. הפרויקט משתמש ב-`phishing_detector/backend/tests/test_db.py`

### 4. קובץ nginx מיותר (לא בשימוש)
- **`phishing_detector/frontend/nginx.conf`** - לא בשימוש. ה-frontend נבנה כ-static files ו-nginx:alpine משרת אותם כברירת מחדל. ה-nginx service ב-docker-compose משתמש ב-`phishing_detector/nginx.conf`

## קבצים שצריכים להיות ב-.gitignore (כבר נוספו):

- `venv/` - virtual environment
- `*.eml` - קבצי דוגמה/בדיקה
- `*.db` - קבצי database
- קבצי IDE ו-OS

## תיקונים שבוצעו:

1. ✅ **תוקן `phishing_detector/frontend/Dockerfile`** - הוסרה שורה 20 שניסתה להעתיק `../nginx.conf` שלא קיים/לא נחוץ
2. ✅ **עודכן `.gitignore`** - נוספו קבצים שצריכים להתעלם מ-git

## המלצה:

למחוק את הקבצים הבאים:
```bash
rm Dockerfile
rm compose.yaml
rm compose.debug.yaml
rm requirements.txt
rm phishing_detector/test_db.py
rm phishing_detector/frontend/nginx.conf
```

**הערה:** אם אתה משתמש ב-VS Code Docker extension, אולי תרצה לשמור את `compose.debug.yaml` לדיבוג. אבל הם לא נחוצים ל-production workflow.
