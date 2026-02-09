# EC2 Deployment Guide - Phishing Detector

## שלב 1: התחברות ל-EC2

```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_IP
```

## שלב 2: העלאת קבצים ל-EC2

מהמחשב המקומי שלך, העלי את הקבצים:

```bash
# העתקת הסקריפטים
scp -i your-key.pem ec2-setup.sh ec2-user@YOUR_EC2_IP:~/
scp -i your-key.pem ec2-deploy.sh ec2-user@YOUR_EC2_IP:~/
scp -i your-key.pem ec2-docker-compose.yml ec2-user@YOUR_EC2_IP:~/
```

## שלב 3: הרצת סקריפט ההתקנה הראשונית

ב-EC2:

```bash
chmod +x ec2-setup.sh
./ec2-setup.sh
```

## שלב 4: עריכת משתני הסביבה

```bash
nano ~/phishing-detector/.env
```

ערכי את הקבץ עם הערכים האמיתיים שלך:

```env
MYSQL_ROOT_PASSWORD=your_strong_root_password
MYSQL_PASSWORD=your_strong_password
GEMINI_API_KEY=your_gemini_api_key
VIRUSTOTAL_API_KEY=your_virustotal_api_key
```

שמרי: `Ctrl+O`, `Enter`, `Ctrl+X`

## שלב 5: התנתקות והתחברות מחדש

```bash
exit
ssh -i your-key.pem ec2-user@YOUR_EC2_IP
```

## שלב 6: העברת הקבצים לתיקיית הפרויקט

```bash
cd ~/phishing-detector
mv ~/ec2-deploy.sh ./deploy.sh
mv ~/ec2-docker-compose.yml ./docker-compose.yml
chmod +x deploy.sh
```

## שלב 7: הרצת ה-Deployment

```bash
./deploy.sh
```

או עם גרסה ספציפית:

```bash
./deploy.sh 1.0.50
```

## פקודות שימושיות

### בדיקת סטטוס
```bash
cd ~/phishing-detector
docker-compose ps
```

### צפייה בלוגים
```bash
docker-compose logs -f
docker-compose logs -f backend1
docker-compose logs -f frontend
```

### עדכון לגרסה חדשה
```bash
./deploy.sh 1.0.51
```

### הפעלה מחדש
```bash
docker-compose restart
```

### עצירת השירותים
```bash
docker-compose down
```

### ניקוי מלא
```bash
docker-compose down -v  # מוחק גם volumes
docker system prune -a  # מנקה הכל
```

## פתרון בעיות

### בדיקת חיבור למסד נתונים
```bash
docker-compose exec mysql mysql -u phishing_user -p phishing_db
```

### בדיקת בריאות השירותים
```bash
curl http://localhost/api/health
```

### בדיקת לוגים של שירות ספציפי
```bash
docker-compose logs backend1 --tail=100
```

## Security Groups ב-AWS

וודאי שה-Security Group של ה-EC2 מאפשר:
- **Port 22** (SSH) - מה-IP שלך בלבד
- **Port 80** (HTTP) - מכל מקום (0.0.0.0/0)
- **Port 443** (HTTPS) - אם יש SSL

## גישה לאפליקציה

לאחר ההתקנה, האפליקציה תהיה זמינה ב:
```
http://YOUR_EC2_PUBLIC_IP
```

## עדכון אוטומטי

כדי לעדכן לגרסה האחרונה מ-Docker Hub:
```bash
cd ~/phishing-detector
./deploy.sh latest
```
