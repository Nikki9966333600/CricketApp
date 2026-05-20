# 🏏 Cricket Score Calculator

A free, user-friendly cricket scoring app built with Python and Streamlit. Track scores, wickets, overs, run rates, and more — all in a clean web interface.

## ✨ Features

- **Match Setup**: Configure team names, overs, and toss decision
- **Live Scoring**: Add runs (0-6), wickets, wides, no-balls, byes
- **Auto Calculations**: Current Run Rate (CRR), Required Run Rate (RRR), target
- **Two Innings Support**: Automatic innings transition with target tracking
- **Undo Function**: Fix mistakes easily
- **Ball-by-ball History**: Review recent balls
- **Match Result**: Automatic winner determination
- **Mobile Friendly**: Works on phones, tablets, and desktops

## 🚀 Run Locally (Free)

### Step 1: Install Python
Make sure you have Python 3.8+ installed. Download from [python.org](https://www.python.org/).

### Step 2: Install Streamlit
```bash
pip install -r requirements.txt
```

### Step 3: Run the App
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🌐 Deploy for FREE on Streamlit Community Cloud

Streamlit Community Cloud lets you deploy this app **completely free** with zero infrastructure costs.

### Step-by-Step Deployment:

1. **Create a GitHub account** (free) at [github.com](https://github.com)

2. **Create a new repository**:
   - Click "New repository"
   - Name it `cricket-score-app`
   - Make it **Public** (required for free deployment)

3. **Upload these files** to your repo:
   - `app.py`
   - `requirements.txt`
   - `README.md`

4. **Sign up at Streamlit Community Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account (free)

5. **Deploy your app**:
   - Click "New app"
   - Select your repository: `cricket-score-app`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"

6. **Done!** Your app will be live at a URL like:
   `https://your-username-cricket-score-app.streamlit.app`

You can share this URL with anyone, on any device.

---

## 💰 Cost Breakdown

| Item | Cost |
|------|------|
| Python | **Free** |
| Streamlit Library | **Free** |
| GitHub Hosting | **Free** |
| Streamlit Community Cloud | **Free** |
| Domain (your-app.streamlit.app) | **Free** |
| **TOTAL** | **$0.00** |

## 📱 How to Use

1. **Open the app** in your browser
2. **Set up match** in the sidebar (team names, overs, who bats first)
3. **Click "Start Match"**
4. **During play**:
   - Tap run buttons (0-6) to record runs
   - Tap "WICKET" for dismissals
   - Tap "Wide", "No Ball", or "Bye" for extras
   - Tap "UNDO" to correct mistakes
5. **App handles**:
   - Automatic over progression
   - Innings transition
   - Target calculation
   - Winner declaration

## 🛠️ Tech Stack

- **Python 3.8+**: Programming language
- **Streamlit**: Web framework (turns Python into web apps with zero HTML/CSS/JS)

## 📝 Notes

- The Streamlit Community Cloud free tier includes:
  - Unlimited public apps
  - 1 GB RAM per app
  - The app sleeps after inactivity but wakes up when accessed
- For more features, you can extend the app to add player names, bowler stats, or save match data

## 🤝 Contributing

Feel free to fork this project and add features like:
- Player-wise batting and bowling stats
- Save/load match data
- Export scorecard as PDF
- Tournament tracking

Enjoy scoring! 🏏
