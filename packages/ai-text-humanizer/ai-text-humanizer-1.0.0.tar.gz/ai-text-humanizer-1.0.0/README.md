
# ✨ AI Text Humanizer ✨
Transform AI-generated or informal text into **formal, human-like, and academic writing** (English & Persian) with ease! 🚀

![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-red?style=flat-square&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square&logo=python)
![License](https://img.shields.io/github/license/mohammadham/AI-Text-Humanizer?style=flat-square)

## 📌 Features

✅ **AI-Powered Text Refinement**: Converts AI-generated or informal text into a more **academic** and **human-like** format (English & Persian)
✅ **Multi-engine support**: hazm, stanza, combo (for Persian), academic (for English)
✅ **CLI & Library Usage**: Use as a command-line tool or import as a Python library
✅ **Streamlit Web Interface**: User-friendly web app for both languages
✅ **PyPI Ready**: Installable via pip, ready for production
✅ **Customizable**: Choose language, engine, and settings
✅ **Word & Sentence Statistics**: Instantly view stats before and after transformation

## 🚀 Live   

![AI-Text-Humanizer](img/humanizer.png)

---

## 📥 Installation

### 4️⃣ Set Up a Virtual Environment (Recommended)  
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

```

### 1️⃣ Install from PyPI
```bash
pip install ai-text-humanizer
```

### 2️⃣ Or Clone the Repository
```bash
git clone https://github.com/mohammadham/AI-Text-Humanizer.git
cd AI-Text-Humanizer-App
pip install --upgrade pip
pip install -r requirements.txt
python setup.py install
```

### 3️⃣ Download NLP Models (for Persian)
```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger');"
python -m stanza.download fa
python -c "from hazm import download_corpus; download_corpus()"
```

## 🖥️ Usage

### 🎯 Web App
```bash
streamlit run main.py
```
- This will **open a browser** at `http://localhost:8501` 🎉  
- Paste or upload your text, apply transformations, and see instant results!  


### 🖥️ Command Line Interface (CLI)
```bash
ai-text-humanizer -t "Your text here" -l en -e default
ai-text-humanizer -t "متن فارسی شما" -l fa -e combo
ai-text-humanizer -f input.txt -l fa -e hazm
```

### 📚 As a Python Library
```python
from ai_text_humanizer import humanize_text
result = humanize_text("Your text here", language="en", engine="default")
result_fa = humanize_text("متن فارسی شما", language="fa", engine="combo")
```
---

## 🛠️ Deployment  

### 📌 **Deploying on Streamlit Cloud**  
1. Push your repo to GitHub.  
2. Ensure `setup.sh` is in the repo root.  
3. Link your **GitHub repo** to **Streamlit Cloud** & specify `app.py` as the entry point.  
4. Streamlit Cloud will handle the deployment automatically.  

---


## 📂 Project Structure
```
AI-Text-Humanizer-App/
├── ai_text_humanizer/      # Python package (library & CLI)
│   ├── __init__.py
│   ├── core.py
│   └── cli.py
├── transformer/            # Text transformation logic (engines)
│   ├── fa_hazm.py
│   ├── fa_stanza.py
│   ├── fa_combo.py
│   └── app.py
├── main.py                 # Streamlit Web Interface
├── requirements.txt
├── setup.py
├── setup.sh
├── README.md
├── README.fa.md
└── .github/workflows/      # CI/CD & release
```

---

## 👨‍💻 Contributing  

🙌 We welcome contributions! Follow these simple steps:

1. **Fork** this repository.  
2. **Create a new branch** (`git checkout -b feature-branch`).  
3. **Commit your changes** (`git commit -m "Add new feature"`).  
4. **Push to GitHub** (`git push origin feature-branch`).  
5. **Open a Pull Request** and let’s improve the project together! 🚀  

---

## 📄 License

📝 This project is licensed under the **MIT License** – feel free to use and modify it as needed.

---

## ⭐️ Support & Call-to-Action

If you find this project useful, please consider:
- **Starring** the repository ⭐️
- **Forking** the project to contribute enhancements
- **Following** for updates on future improvements

Your engagement helps increase visibility and encourages further collaboration!

---

## 🚀 Planned & Possible Improvements
- Add automatic language detection
- Improve Persian paraphrasing (add more transformer models)
- Add more engines (e.g. ParsBERT)
- Improve UX and error messages
- Add more unit tests
- Add Dockerfile for easy deployment

---

## 📞 Contact & Support
For issues or feature requests, open an issue on GitHub.

---

🔥 **Transform Your AI-Generated Text with Ease!** ✨

