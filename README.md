
# ⚡ WhatsApp Chat Analyzer  
### Turn your WhatsApp chats into real data insights — response times, heatmaps, conversation patterns, double-text desperation analysis & more.

<p align="center">
  <img src="https://img.shields.io/badge/WhatsApp-Analyzer-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Streamlit-Web%20UI-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Matplotlib-Seaborn-yellow?style=for-the-badge" />
</p>

---

## 🧠 Why This Exists

Because waiting 6 hours for someone to reply is a crime against humanity —  
so this project tells you *exactly when* someone replies fastest, who carries the conversation, who double-texts more, and who ghosts more than Casper.

Built originally as a CLI tool, upgraded with a **full interactive Streamlit web app** for real-time analytics.

---

# 🚀 Features

### 🔍 Deep Chat Analytics
- **Best time to message someone**  
- **P50 / P90 / P95 / P99 response time percentiles**
- **Response time heatmaps** (hour × weekday)
- **Who talks more** (message volumes)
- **Double text frequency** (aka the desperation index)
- **Message length patterns**
- **Emoji usage analysis**
- **Longest gaps in conversation**
- **Daily streaks**
- **Conversation initiators**

### 🖥️ Two Ways to Use
| Mode | Description |
|------|-------------|
| **Web UI (Streamlit)** | Upload `.txt`, view all charts instantly — no folders, no PNGs. |
| **CLI Mode** | Old-school mode: saves PNG charts to `output/` folder. |

---

# 🌐 Streamlit Web App (Recommended)

You now get a full GUI experience.  
Upload your WhatsApp `.txt` file → get instant analytics in your browser.

### **Run Web App**
```bash
pip install -r requirements.txt
streamlit run streamlit_app/app.py
```

Then open:

```text
http://localhost:8501
```

### **Web UI Highlights**

* Drag-and-drop file upload
* Live chart rendering
* Tabs for every metric
* Toggle PNG saving
* Download all charts as a ZIP
* Runs entirely locally — nothing leaves your machine

---

# 🧪 CLI Usage (Original Mode)

### **1. Export Your WhatsApp Chat**

* **iPhone:** Open chat → Contact name → Export Chat → *Without Media*
* **Android:** Chat → ⋮ menu → More → Export Chat → *Without Media*

### **2. Run Analyzer**

```bash
python analyser.py "chat.txt"
```

### **3. Custom Output Folder**

```bash
python analyser.py "chat.txt" -o results
```

All charts saved to the specified folder.

---

# 📊 Output Visualizations

Both CLI & Web UI generate these 12 analytics:

1. Summary Stats
2. Response Time Percentiles
3. Response Time Heatmap
4. Message Volume
5. Activity Patterns
6. Conversation Initiators
7. Double Text Frequency
8. Message Length
9. Emoji Usage
10. Question Frequency
11. Conversation Gaps
12. Daily Streak

---

# 📁 Project Structure

```plaintext
.
├── analyser.py                  # Core analytics engine (CLI + Web)
├── streamlit_app/
│   └── app.py                   # Streamlit Web UI
├── output/                      # Generated charts (CLI mode)
├── requirements.txt
└── README.md
```

---

# 🔧 Installation

```bash
git clone <your-repo-url>
cd <repo-folder>
pip install -r requirements.txt
```

---

# 🔒 Privacy

Everything runs locally.
Your chat never leaves your machine.
No servers. No tracking. No data upload.

---

# 🤝 Contributing

Contributions are welcome — especially on:

* UI/UX improvements for the Streamlit app
* Adding interactive Plotly charts
* More statistical measures
* Multi-chat comparison
* Performance optimizations

### **To contribute:**

1. Fork repo
2. Create feature branch
3. Make changes
4. Create PR

---

# 🐞 Troubleshooting

### **Common errors:**

* ❌ *“No messages found”*
  → Export chat **without media**
  → Ensure `.txt` formatting matches WhatsApp export formats
* ❌ Unicode issues
  → Run with UTF-8 environment

---

# ❤️ Credits

Created originally by [Pankaj Tanwar](https://github.com/Pankajtanwarbanna)
Upgraded with a modern **Streamlit Web UI** by [Anubhav Sharma](https://github.com/LordZeusIsBack/).

Checkout his other projects:
[https://pankajtanwar.in/side-hustles](https://pankajtanwar.in/side-hustles)

---

# 📜 License

MIT License — free to use, modify, and break things.

---
