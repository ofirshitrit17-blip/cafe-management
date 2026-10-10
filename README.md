# מערכת ניהול עובדים ותפעול – בית קפה

מערכת מותאמת לפי הארכיטקטורה שאושרה בתוכנית המורחבת (אוקטובר 2026).

## טכנולוגיות
- **Backend**: Python 3.11+ / FastAPI + Jinja2 + HTMX
- **Database**: PostgreSQL (מנוהל – Render / אחר)
- **הודעות**: WhatsApp Cloud API
- **אחסון תמונות**: Cloudflare R2 (או S3 תואם)
- **Hosting מומלץ**: Render

## מבנה הפרויקט
```
cafe-management/
├── app/
│   ├── main.py              # נקודת כניסה
│   ├── config.py            # הגדרות
│   ├── database.py
│   ├── models/              # כל הטבלאות
│   ├── routers/             # נתיבים
│   ├── services/            # לוגיקה עסקית
│   ├── templates/           # ממשק בעברית (RTL)
│   └── utils/
├── requirements.txt
├── .env.example
└── README.md
```

## התקנה מקומית (פיתוח)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# ערוך את .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## משתני סביבה חשובים
ראה `.env.example`.

## מה כבר ממומש (גרסה ראשונה)
- מודל נתונים מלא (Users, Attendance, Breaks, Shifts, Tasks, Checklists, Notifications, Audit, Onboarding)
- התחברות ב-OTP דרך WhatsApp
- שעון נוכחות (עם בדיקת רשת בית הקפה)
- ניהול הפסקות + תזמון תזכורת + התראת חריגה
- תור הודעות + תהליך רקע כל 30 שניות
- יומן ביקורת
- ממשק מובייל בעברית (RTL) עם HTMX

## מה נשאר להשלים בשלבים הבאים
1. סידור עבודה מלא + הגשת אילוצים + דדליין רביעי 13:00
2. החלפת משמרות + אישור מנהל
3. הגרלת / תורנות משימות יומיות
4. בקרת איכות + העלאת תמונות
5. אונבורדינג
6. לוח מנהלים + ייצוא אקסל חודשי
7. טאבלט עם QR מתחלף להחתמה
8. הגדרת תבניות WhatsApp מאושרות

## פריסה ב-Render
1. חבר את הריפו
2. הגדר משתני סביבה
3. הוסף PostgreSQL
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## הערות משפטיות
- משך הפסקות ייקבע רק אחרי ייעוץ שכר.
- רישומי נוכחות נשמרים 7 שנים.
- תמונות נמחקות אחרי 60 יום.
