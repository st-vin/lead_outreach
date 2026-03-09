# 🚀 QUICK START GUIDE

## You're Ready to Go! Here's What You Have:

### ✅ **Complete Application Built**
- 21 Python files (backend 100% done)
- 9 HTML templates (frontend 100% done)
- All 8 critical fixes implemented
- Sample CSV data included

---

## 🏃 **3 Steps to Launch**

### **Step 1: Install Dependencies**
```bash
cd lead-outreach-tool-v2
pip install -r requirements.txt
```

### **Step 2: Start the App**
```bash
python main.py
```

**OR use the startup script:**
```bash
./start.sh
```

### **Step 3: Open Browser**
```
http://localhost:5000
```

---

## 📱 **Your First Campaign (5 minutes)**

1. **Go to Settings** → Add your name (API key optional)
2. **Upload CSV** → Use `uploads/sample_kisii_businesses.csv`
3. **Preview Columns** → Verify detection (should show 95% confidence)
4. **Confirm Import** → See 8 businesses imported
5. **Generate Pitches** → Click "Generate Next 10 Pitches"
   - Watch real-time progress (SSE working!)
   - See AI/template fallback in action
6. **Send via WhatsApp** → Click business → Send message

---

## 🎯 **What Works Right Now**

### **All 8 Critical Fixes Working**
1. ✅ **Unique Filenames** - Try uploading same CSV twice
2. ✅ **WAL Mode** - Database handles concurrent access
3. ✅ **Timeouts** - All API calls have 5-30s limits
4. ✅ **Encryption Key** - Stored in `data/encryption.key`
5. ✅ **Phone Validation** - Invalid phones shown in skip report
6. ✅ **Column Confidence** - See % scores in preview
7. ✅ **Settings Verification** - Save & reload to confirm
8. ✅ **SSE Progress** - Real-time batch generation updates

### **Core Features**
- ✅ CSV Upload (3-step process)
- ✅ Column auto-detection
- ✅ Data cleaning & validation
- ✅ Opportunity scoring
- ✅ AI pitch generation (Cerebras)
- ✅ Template fallback (no API key needed)
- ✅ WhatsApp integration
- ✅ Status tracking
- ✅ Campaign management

---

## 🧪 **Quick Test Checklist**

```bash
# 1. Test imports
python3 -c "import config; print('✓ Config loaded')"

# 2. Test database init
python3 -c "from application.database import init_db; init_db(); print('✓ DB created')"

# 3. Test phone normalization
python3 -c "from application.utils.phone import normalize_phone; print(normalize_phone('0719833700', '+254'))"
# Should output: +254719833700

# 4. Test encryption
python3 -c "from application.utils.crypto import encrypt_api_key, decrypt_api_key; enc=encrypt_api_key('test'); print(decrypt_api_key(enc))"
# Should output: test

# 5. Start app
python3 main.py
```

---

## 📊 **File Structure**

```
lead-outreach-tool-v2/
├── main.py                    # Flask app entry point
├── config.py                  # All settings & timeouts
├── requirements.txt           # Dependencies
├── start.sh                   # Quick startup script
│
├── application/
│   ├── database.py            # WAL mode + sessions
│   ├── models.py              # SQLAlchemy models
│   ├── routes/                # 5 route blueprints
│   ├── services/              # Business logic
│   └── utils/                 # Crypto, phone, files
│
├── templates/                 # 9 HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── campaign_detail.html   # SSE progress UI
│   └── upload/                # 3-step process
│
├── uploads/                   # CSV storage
│   └── sample_kisii_businesses.csv
│
└── data/                      # Auto-created
    ├── lead_outreach.db       # SQLite database
    └── encryption.key         # Persistent key
```

---

## 🔑 **Optional: Get Free Cerebras API Key**

Without API key: Uses template-based pitches ✅
With API key: Uses AI-generated pitches 🚀

1. Visit: https://cerebras.ai
2. Sign up (free tier available)
3. Get API key (starts with `sk-`)
4. Add in Settings page
5. Generate pitches → See AI in action!

---

## 🐛 **Common Issues**

### **Port already in use**
```bash
# Change port in main.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### **Database locked**
```bash
# WAL mode should prevent this, but if it happens:
rm data/lead_outreach.db
python3 main.py  # Will recreate DB
```

### **Module not found**
```bash
# Make sure you're in project directory
cd lead-outreach-tool-v2
pip install -r requirements.txt
```

---

## 📦 **Deploy to Production**

### **Railway (Recommended)**
```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo>
git push

# 2. Connect to Railway
# railway.app → New Project → Deploy from GitHub

# 3. Add environment variable:
DATABASE_URL=postgresql://... (Railway provides this)
```

### **Render / PythonAnywhere**
Same process - just connect GitHub repo!

---

## ✨ **You're Done!**

This is a **production-ready MVP** with:
- Clean architecture
- Error handling
- Real-time updates
- Data validation
- Security (encryption)
- Responsive UI
- API fallbacks

**Next Steps:**
1. Test with your own CSV data
2. Get Cerebras API key (optional)
3. Customize pitch templates
4. Deploy to production
5. Start finding clients! 🎯

---

**Questions? Check README.md for detailed documentation.**
