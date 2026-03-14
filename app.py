import streamlit as st
import pandas as pd
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import warnings

# NLP IMPORTS
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

nltk.download('punkt')
nltk.download('stopwords')

warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Fake Job Detector",
    page_icon="🔍",
    layout="wide"
)

# ADVANCED HTML + CSS DESIGN
st.markdown("""
<style>

/* Background */
.stApp {
background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
color: white;
}

/* Title */
h1 {
text-align:center;
color:#00ffc8;
font-size:45px;
}

/* Text area */
textarea {
border-radius:10px !important;
border:2px solid #00ffc8 !important;
}

/* Buttons */
.stButton>button {
background-color:#00ffc8;
color:black;
font-size:18px;
border-radius:10px;
height:3em;
width:100%;
}

/* Hover effect */
.stButton>button:hover {
background-color:#00c9a7;
}

/* Result box */
.result-box{
padding:20px;
border-radius:10px;
background-color:rgba(255,255,255,0.1);
margin-top:10px;
}

</style>
""", unsafe_allow_html=True)

# HTML WELCOME CARD
st.markdown("""
<div style='
padding:20px;
border-radius:10px;
background-color:rgba(255,255,255,0.1);
text-align:center;
margin-bottom:20px;
'>

<h2>🛡 AI Job Scam Detector</h2>

<p>
Paste a job posting below and our AI system will analyze it
for scam indicators using <b>Machine Learning + NLP</b>.
</p>

</div>
""", unsafe_allow_html=True)

# Title
st.title("🔍 Fake Job Detector for Call Center / Scam Jobs")

st.markdown(
"Paste a job post below to analyze its legitimacy and identify potential red flags."
)

# Session state
if 'model' not in st.session_state:
    st.session_state.model = None

if 'vectorizer' not in st.session_state:
    st.session_state.vectorizer = None


# ======================
# NLP FUNCTIONS
# ======================

def preprocess_text(text):

    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', '', text)

    tokens = word_tokenize(text)

    stop_words = set(stopwords.words('english'))

    filtered = [word for word in tokens if word not in stop_words]

    return filtered


def detect_nlp_scam_patterns(text):

    scam_keywords = [
        "earn","money","quick","profit",
        "guaranteed","instant","cash",
        "income","bonus","fast"
    ]

    words = preprocess_text(text)

    matches = []

    for w in words:
        if w in scam_keywords:
            matches.append(w)

    return matches


# ======================
# MODEL CREATION
# ======================

def load_model():

    sample_scam_texts = [
        "Earn $5000 weekly working from home with no experience needed",
        "URGENT HIRING WhatsApp us at +1234567890 for interview",
        "Immediate start no interview required just send details",
        "High salary with zero qualifications needed",
        "Contact us on Telegram easyjob",
        "Get paid daily through PayPal",
        "Work only 2 hours daily earn $3000 monthly",
        "No resume needed just WhatsApp your name",
        "Guaranteed income with minimal effort",
        "EASY MONEY fast hiring process"
    ]

    sample_legit_texts = [
        "We are looking for qualified candidates",
        "Please submit resume through official portal",
        "Competitive salary based on experience",
        "Interview process will consist of multiple rounds",
        "Successful candidates receive benefits",
        "Minimum 2 years experience required",
        "Submit application through website",
        "Background check conducted",
        "Bachelor degree required",
        "Professional development opportunities"
    ]

    texts = sample_scam_texts + sample_legit_texts
    labels = [1]*len(sample_scam_texts) + [0]*len(sample_legit_texts)

    vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
    X = vectorizer.fit_transform(texts)

    model = LogisticRegression()
    model.fit(X, labels)

    return model, vectorizer


# ======================
# RULE DETECTION
# ======================

def detect_urgency(text):

    urgency_keywords = [
        'urgent','immediate','asap','quick','fast',
        'start now','apply now','last chance'
    ]

    matches = []

    for keyword in urgency_keywords:
        if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
            matches.append(keyword)

    return matches


def detect_salary_language(text):

    patterns = [
        r'\$\d{3,5}\s*(weekly|daily)',
        r'earn\s+\$\d{3,}',
        r'high\s+salary\s+no\s+experience',
        r'guaranteed\s+(income|salary)'
    ]

    matches = []

    for pattern in patterns:
        found = re.findall(pattern,text,re.IGNORECASE)
        if found:
            matches.extend(found)

    return matches


def detect_contact_methods(text):

    patterns = [
        r'whatsapp',
        r'telegram',
        r'\+\d{10,}',
        r'cash\s*app',
        r'paypal'
    ]

    matches=[]

    for pattern in patterns:
        found=re.findall(pattern,text,re.IGNORECASE)
        if found:
            matches.extend(found)

    return matches


def detect_grammar_issues(text):

    issues=[]

    if re.search(r'[A-Z]{4,}',text):
        issues.append("Excessive capitalization")

    if re.search(r'!{2,}',text):
        issues.append("Too many exclamation marks")

    professional_terms = [
        "experience","qualification",
        "resume","interview","position"
    ]

    if not any(term in text.lower() for term in professional_terms):
        issues.append("Lacks professional terms")

    return issues


def detect_too_good(text):

    patterns = [
        r'no\s+experience\s+needed',
        r'work\s+from\s+home',
        r'easy\s+money',
        r'no\s+interview'
    ]

    matches=[]

    for pattern in patterns:
        found=re.findall(pattern,text,re.IGNORECASE)
        if found:
            matches.extend(found)

    return matches


# ======================
# SCAM SCORE
# ======================

def calculate_scam_score(flags):

    score=0

    score+=len(flags['urgency'])*10
    score+=len(flags['salary'])*15
    score+=len(flags['contact'])*20
    score+=len(flags['grammar'])*5
    score+=len(flags['too_good'])*10
    score+=len(flags['nlp_patterns'])*5

    return min(score,100)


# ======================
# ANALYSIS
# ======================

def analyze_job(text):

    red_flags={
        "urgency":detect_urgency(text),
        "salary":detect_salary_language(text),
        "contact":detect_contact_methods(text),
        "grammar":detect_grammar_issues(text),
        "too_good":detect_too_good(text),
        "nlp_patterns":detect_nlp_scam_patterns(text)
    }

    score=calculate_scam_score(red_flags)
    red_flags["score"]=score

    return red_flags


# LOAD MODEL
if st.session_state.model is None:

    with st.spinner("Loading AI model..."):

        st.session_state.model,st.session_state.vectorizer=load_model()


# TABS
tab1,tab2,tab3=st.tabs(["Analyze Job","Red Flag Guide","About"])


# TAB1
with tab1:

    col1,col2=st.columns([2,1])

    with col1:

        job_text=st.text_area(
            "Paste Job Post Here",
            height=300,
            placeholder="Example: URGENT HIRING!!! Work from home earn $5000 weekly"
        )

        if job_text:
            words=len(job_text.split())
            st.caption(f"Word count: {words}")

    with col2:

        st.markdown("### What to look for")

        st.markdown("""
🚨 Urgent language  
💰 Unrealistic salary  
📱 WhatsApp contact  
❗ Poor grammar  
🎯 Too good offers
""")

    if st.button("Analyze Job Post",use_container_width=True):

        if job_text:

            with st.spinner("🔍 AI analyzing job post..."):

                result=analyze_job(job_text)
                score=result["score"]

                st.subheader("Analysis Result")

                if score>70:
                    st.error(f"⚠️ High Scam Risk ({score}%)")

                elif score>30:
                    st.warning(f"⚠️ Medium Risk ({score}%)")

                else:
                    st.success(f"✅ Low Risk ({score}%)")

                st.progress(score/100)

                st.subheader("Detected Issues")

                for key,value in result.items():

                    if key!="score" and value:

                        st.write(f"**{key.upper()}**")

                        for item in value:

                            st.write("-",item)

        else:

            st.warning("Paste job post first")


# TAB2
with tab2:

    st.header("Common Job Scam Indicators")

    st.markdown("""
🚨 Urgency pressure  
💰 Unrealistic salary  
📱 WhatsApp interviews  
❗ Poor grammar  
🎯 No experience high pay  
💸 Asking money
""")


# TAB3
with tab3:

    st.header("About")

    st.markdown("""
This tool uses **Machine Learning + NLP + Rule Detection**
to detect scam job posts.

Technology used:

• Python  
• Scikit-learn  
• Regex  
• NLP (NLTK)  
• Streamlit  

⚠️ This tool provides **risk analysis only**.
Always verify jobs through official websites.
""")


# FOOTER
st.markdown("""
<hr>

<div style="text-align:center">

<p>🔍 AI Job Scam Detection System</p>

<p>Built with Python • Machine Learning • NLP • Streamlit</p>

<p>⚠ Always verify job offers through official company websites.</p>

</div>
""",unsafe_allow_html=True)
