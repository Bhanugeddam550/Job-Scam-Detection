# 🔍 AI Job Scam Detection System

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange)
![NLP](https://img.shields.io/badge/NLP-NLTK-green)
![Streamlit](https://img.shields.io/badge/Web%20App-Streamlit-red)

## 📌 Project Overview

The **AI Job Scam Detection System** is a Machine Learning–based web application that analyzes job postings and identifies potential fraudulent job offers.

The system uses **Natural Language Processing (NLP)** and **Machine Learning algorithms** to detect common scam patterns such as unrealistic salaries, urgent hiring language, suspicious contact methods, and "too good to be true" job offers.

This project helps job seekers **identify potentially fraudulent job postings and avoid online job scams**.

---

## 🌐 Live Demo

Try the application here:

👉 https://job-scam-detection.streamlit.app/

---

## 🚀 Features

* 🔍 Analyze job descriptions for scam indicators
* 🤖 Machine Learning–based classification
* 📊 Scam probability score generation
* 🚨 Detection of common scam patterns:

  * Urgent hiring language
  * Unrealistic salary promises
  * Suspicious contact methods (WhatsApp / Telegram)
  * Poor grammar or excessive punctuation
  * Too-good-to-be-true job offers
* 🌐 Interactive web interface built with Streamlit
* ⚡ Real-time job description analysis

---

## 🧠 Technologies Used

* **Python**
* **Machine Learning**
* **Natural Language Processing (NLP)**
* **Streamlit**
* **Scikit-learn**
* **Pandas**
* **NumPy**
* **NLTK**

---

## ⚙️ Machine Learning Model

The application uses a combination of **Machine Learning and rule-based analysis**.

Key techniques include:

* **TF-IDF Vectorization** for text feature extraction
* **Logistic Regression** for scam classification
* **Rule-based detection** for identifying suspicious job patterns

The system analyzes job descriptions and predicts whether the job posting is:

* ✅ **Legitimate**
* ⚠️ **Potentially Fraudulent**

---

## 📂 Project Structure

```
job-scam-detector/
│
├── app.py
├── requirements.txt
└── README.md
```

---

## ▶️ How to Run the Project Locally

### 1️⃣ Clone the Repository

```
git clone https://github.com/Bhanugeddam550/Job-Scam-Detector.git
```

### 2️⃣ Navigate to the Project Folder

```
cd Job-Scam-Detector
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```
streamlit run app.py
```

### 5️⃣ Open the Browser

Streamlit will generate a local link such as:

```
http://localhost:8501
```

---

## 🛡️ Scam Detection Indicators

The system identifies common fraud signals such as:

* Urgent hiring messages
* Extremely high salary promises
* Contact through messaging apps
* Lack of professional job requirements
* Suspicious language patterns

---

## ⚠️ Disclaimer

This tool provides **risk assessment only** and may not always be 100% accurate.

Users should **always verify job opportunities through official company websites or trusted platforms** before applying.

---

## 👩‍💻 Author

**Bhanusri Geddam**

👤 Authentication Feature

This project also includes a basic user authentication system using SQLite, allowing users to:

Create a new account

Log in securely

Access the scam detection system after authentication

This improves the structure of the application and simulates real-world protected access to a web platform.
---

## ⭐ Future Improvements

* Train the model using **large real-world job datasets**
* Implement **Deep Learning NLP models**
* Add **company verification APIs**
* Improve **UI/UX and analytics dashboard**
* Integrate **job posting data sources**

---

⭐ If you like this project, consider **starring the repository**!
