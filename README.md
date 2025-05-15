# fpl-optimizer-app
Fun app to optimize FPL gameplay weekly
# 🌟 FPL Assistant Dashboard

This Streamlit app is a Fantasy Premier League (FPL) assistant tool designed to help users:

* Build an optimized FPL squad using linear programming (PuLP)
* Visualize squad composition and performance
* Compare player stats with radar charts
* Discover high-value players
* Receive weekly transfer suggestions based on player performance and risk

---

## ⚙️ How It Works

The app uses live FPL data from the [Fantasy Premier League API](https://fantasy.premierleague.com/api/bootstrap-static/) and performs the following steps:

### 🧠 Optimization Logic

* **Objective**: Maximize gameweek planning score
* **Constraints**:

  * 15 total players
  * £100m budget (1000 in FPL units)
  * Squad structure: 2 GK, 5 DEF, 5 MID, 3 FWD
  * Max 3 players per club
* **Rotation Risk** is calculated based on player status and minutes played

### 📈 Visualizations

* **Radar Chart**: Compare key metrics (form, points per game, creativity, threat)
* **Bar Charts**:

  * Top 10 projected players
  * Squad projected performance
  * Value for money (points per £m)

### 🔁 Transfer Suggestions

* Suggests up to 3 player swaps
* Prioritizes improvement in planning score and reduced rotation risk
* Honors position and budget compatibility

---

## 🚀 How to Run Locally

### 1. Clone or Download this Repo

```
git clone https://github.com/your-username/fpl-optimizer-app.git
cd fpl-optimizer-app
```

### 2. Install Requirements

```
pip install -r requirements.txt
```

### 3. Run Streamlit

```
streamlit run app.py
```

---

## ☁️ How to Deploy on Streamlit Cloud

1. Push this repo to your GitHub account
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub account
4. Deploy the app by selecting your repo and `app.py`

---

## 📁 Files in This Repo

| File               | Description                      |
| ------------------ | -------------------------------- |
| `app.py`           | Main dashboard code              |
| `requirements.txt` | List of required Python packages |
| `README.md`        | You're reading it!               |

---

## 👨‍💻 Author Notes

This app was built to demonstrate:

* Linear optimization in FPL planning
* Seaborn and matplotlib for performance analysis
* Practical dashboard design with Streamlit

You can enhance this further by:

* Adding fixture difficulty mapping
* Integrating real-time gameweek stats
* Including captaincy decision logic

Enjoy building your perfect FPL team!

---

**Developed by:** Ese Onovughe
**Inspired by:** Fantasy football, data science, and optimization 💡
