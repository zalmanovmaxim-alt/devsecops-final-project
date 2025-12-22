יצירת סביבה וירטואלית
git clone https://github.com/Gidiy/DevSecOps-Project6.git - העתקת הפרוייקט למחשב
cd DevSecOps-Project6-מעבר לתיקייה במחשב
python -m venv .venv-יצירת סביבה וירטואלית
.\.venv\Scripts\Activate.ps1-הפעלת הסביבה הוירטואלית
python -m pip install --upgrade pip-הכנת מנהל ההרחבות להורדה
python -m pip install -r requirements.txt- הורדת כל ההרחבות מתוך הקובץ
python main.py - הרצת הפרוייקט
ctrl + c - עצירת הפרוייקט
deactivate - יציאה מהסביבה הוירטואלית

קובץ .env חשוף כדי לאפשר הפעלה זמנית

קונספט
הפכו משימות משרדיות משעממות למשחקים מרגשים! צרו תחרויות לכל דבר - איכות קוד, חיסכון באנרגיה, כושר, למידה, אתגרי צוות. השלם עם לוחות הישגים, הישגים ופרסים!

חלוקת צוותים
תלמיד 1: מנוע משחק ומערכת הישגים
תלמיד 2: ניהול תחרויות ותכונות חברתיות
תלמיד 3: לוחות הישגים ומערכת תגמולים

מנוע ליצירת משחקים

POST /api/games/competitions/create - יצירת תחרות חדשה 
GET /api/games/active - צפייה בתחרויות פעילות 
POST /api/games/join - הצטרפות לתחרות 
PUT /api/games/progress/update - עדכון התקדמות התחרות 
GET /api/games/rules - קבלת כללי תחרות 
POST /api/games/custom/create - יצירת כללי משחק מותאמים אישית מערכת הישגים 

מערכת הישגים
GET /api/achievements/available - צפייה בהישגים זמינים 
POST /api/achievements/unlock - פתיחת הישגים 
GET /api/achievements/my-progress - התקדמות אישית בהישגים 
POST /api/achievements/create-custom - יצירת הישגים מותאמים אישית 
קטגוריות משחק
POST /api/competitions/code-quality - תחרויות איכות קוד 
POST /api/competitions/learning - אתגרי למידה 
POST /api/competitions/fitness - אתגרי כושר במשרד 
POST /api/competitions/sustainability - תחרויות משרד ירוק 
POST /api/competitions/creativity - אתגרים יצירתיים 
POST /api/competitions/team-building - פעילויות בניית צוות לוחות הישגים ודירוגים 

לוח הישגים ודירוגים
GET /api/leaderboards/global - לוחות הישגים משרדיים גלובליים 
GET /api/leaderboards/team - לוחות הישגים ספציפיים לצוות 
GET /api/leaderboards/monthly - דירוגים חודשיים 
POST /api/leaderboards/challenge - אתגר דירוג של מישהו 
GET /api/leaderboards/hall-of-fame - היכל התהילה 
POST /api/leaderboards/predictions - ניבוי זוכים תכונות חברתיות 
פיצ'רים חברתיים
POST /api/social/teams/create - יצירת צוותי תחרות 
GET /api/social/friends - צפייה בחברים/עמיתים מהמשרד 
POST /api/social/challenges/send - שליחת אתגרים אישיים 
GET /api/social/activity-feed - פיד של פעילות חברתית 
POST /api/social/celebrations - חגיגת הישגים 
GET /api/social/rivalries - יריבויות משרדיות מהנות מערכת תגמולים 
מערכת תגמולים
GET /api/rewards/available - תגמולים זמינים 
POST /api/rewards/redeem - מימוש נקודות עבור תגמולים 
GET /api/rewards/my-points - בדיקת נקודות אישיות 
POST /api/rewards/donate-points - תרומת נקודות לצדקה 
GET /api/rewards/store - אחסון תגמולים במשרד 
POST /api/rewards/suggest - הצעת תגמולים חדשים

כדי להקל על שליחת הבקשות יצרנו ממשק משתמש נוח שבוחרים את המצב הרצוי ומקבלים את תשובת הrequest
