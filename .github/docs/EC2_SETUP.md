# EC2 Setup Guide - GitHub Actions Runner & Security Groups

## 1. הגדרת GitHub Actions Runner כ-Service (אוטומטי)

**לא צריך להפעיל כל פעם עם SSH!** צריך להגדיר את ה-runner כ-service שירוץ אוטומטית.

### התקנה ראשונית (אם עדיין לא התקנת):

```bash
# התחבר ל-EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# הורד את ה-runner
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# הגדר את ה-runner (תקבל token מ-GitHub)
./config.sh --url https://github.com/YOUR_USERNAME/YOUR_REPO --token YOUR_TOKEN
```

### הגדרה כ-Service (אוטומטי):

```bash
# התקן את ה-service
sudo ./svc.sh install

# הפעל את ה-service
sudo ./svc.sh start

# בדוק סטטוס
sudo ./svc.sh status

# אם צריך לעצור
sudo ./svc.sh stop

# אם צריך להסיר
sudo ./svc.sh uninstall
```

**אחרי זה ה-runner ירוץ אוטומטית כל הזמן!**

### עדכון ה-runner:

```bash
cd ~/actions-runner
./svc.sh stop
./svc.sh uninstall

# הורד גרסה חדשה
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# התקן מחדש
sudo ./svc.sh install
sudo ./svc.sh start
```

---

## 2. Security Group - פורטים שצריכים להיות פתוחים

### Inbound Rules (נכנסים):

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| HTTP | TCP | 80 | 0.0.0.0/0 | Web traffic - nginx |
| SSH | TCP | 22 | Your IP /32 | SSH access (מומלץ להגביל ל-IP שלך) |

**הערה:** אם תרצה HTTPS בעתיד, תצטרך להוסיף:
- HTTPS | TCP | 443 | 0.0.0.0/0

### Outbound Rules (יוצאים):

| Type | Protocol | Port Range | Destination | Description |
|------|----------|------------|-------------|-------------|
| HTTPS | TCP | 443 | 0.0.0.0/0 | GitHub API, Docker Hub, External APIs |
| HTTP | TCP | 80 | 0.0.0.0/0 | Optional - for HTTP redirects |

**חשוב:** Outbound צריך להיות פתוח כדי:
- GitHub Actions Runner להתחבר ל-GitHub
- Docker למשוך images מ-Docker Hub
- Backend להתחבר ל-VirusTotal API
- Backend להתחבר ל-Gemini API

### פורטים שלא צריכים להיות פתוחים:

- **5000** - Backend Flask (פנימי, בתוך Docker network)
- **3306** - MySQL (פנימי, בתוך Docker network)
- **8080, 3000** - Development ports (לא בשימוש ב-production)

---

## 3. בדיקת Security Group

### ב-AWS Console:

1. לך ל-EC2 → Instances
2. בחר את ה-instance שלך
3. לחץ על Security tab
4. בדוק את ה-Security Group
5. לחץ על Security Group → Edit inbound/outbound rules

### בדיקה מ-Terminal:

```bash
# בדוק אם פורט 80 פתוח
curl -I http://YOUR_EC2_IP

# בדוק אם SSH עובד
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

---

## 4. טיפים נוספים

### בדיקת Runner Status:

```bash
# בדוק אם ה-runner רץ
sudo systemctl status actions.runner.*.service

# בדוק לוגים
cd ~/actions-runner/_diag
tail -f Runner_*.log
```

### אם ה-runner לא עובד:

```bash
# הפעל מחדש
cd ~/actions-runner
sudo ./svc.sh stop
sudo ./svc.sh start

# או הפעל ידנית לבדיקה
./run.sh
```

### בדיקת Docker:

```bash
# בדוק אם Docker רץ
sudo systemctl status docker

# בדוק containers
docker ps

# בדוק images
docker images
```

---

## סיכום

✅ **Runner:** הגדר כ-service - `sudo ./svc.sh install && sudo ./svc.sh start`  
✅ **Inbound:** פורט 80 (HTTP), פורט 22 (SSH - מומלץ להגביל ל-IP שלך)  
✅ **Outbound:** פורט 443 (HTTPS) - לכל המקומות  
❌ **לא צריך:** פורטים 5000, 3306 - הם פנימיים ב-Docker network
