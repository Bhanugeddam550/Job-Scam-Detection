import streamlit as st
import pandas as pd
import re
import numpy as np
import sqlite3
import hashlib
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

warnings.filterwarnings("ignore")

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="AI Job Scam Detector",
    page_icon="🛡️",
    layout="wide"
)

# ======================
# CUSTOM CSS - NEW THEME
# ======================
st.markdown("""
<style>
/* Main app */
.stApp {
    background: linear-gradient(135deg, #f4f7fb, #eaf1f8);
    color: #1f2937;
}

/* Hide default Streamlit menu/footer/header */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* General headings */
h1, h2, h3 {
    color: #0f172a !important;
    font-weight: 700 !important;
}

/* Paragraphs and text */
p, label, div, span, li {
    color: #1f2937 !important;
}

/* Input labels */
label {
    font-weight: 600 !important;
    color: #111827 !important;
}

/* Text inputs */
.stTextInput input {
    border-radius: 12px !important;
    border: 1.5px solid #cbd5e1 !important;
    background-color: #ffffff !important;
    color: #111827 !important;
    padding: 10px !important;
}

/* Text area */
.stTextArea textarea {
    border-radius: 14px !important;
    border: 2px solid #cbd5e1 !important;
    background-color: #ffffff !important;
    color: #111827 !important;
    padding: 12px !important;
    font-size: 16px !important;
}

/* Placeholder */
input::placeholder, textarea::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: none;
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white !important;
    font-weight: 600;
    font-size: 16px;
    height: 46px;
    transition: 0.25s ease;
    box-shadow: 0 6px 14px rgba(37, 99, 235, 0.20);
}

.stButton > button:hover {
    background: linear-gradient(90deg, #1d4ed8, #1e40af);
    transform: translateY(-1px);
    color: white !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #dbeafe;
    border-radius: 10px 10px 0 0;
    color: #1e3a8a !important;
    padding: 10px 18px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background-color: #2563eb !important;
    color: white !important;
}

/* Cards */
.card-box {
    background: #ffffff;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    margin-bottom: 16px;
}

.hero-box {
    background: linear-gradient(135deg, #ffffff, #f8fbff);
    padding: 28px;
    border-radius: 22px;
    text-align: center;
    margin-bottom: 22px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
}

.result-box {
    padding: 20px;
    border-radius: 16px;
    background: #eff6ff;
    border-left: 6px solid #2563eb;
    border: 1px solid #bfdbfe;
    margin-top: 10px;
    margin-bottom: 16px;
}

.about-box {
    background: #ffffff;
    padding: 28px;
    border-radius: 20px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    margin-top: 30px;
    margin-bottom: 20px;
}

.small-note {
    color: #475569 !important;
    font-size: 14px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #eff6ff, #dbeafe);
    border-right: 1px solid #cbd5e1;
}

section[data-testid="stSidebar"] * {
    color: #0f172a !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e5e7eb;
    padding: 10px;
    border-radius: 14px;
    box-shadow: 0 4px 10px rgba(15, 23, 42, 0.05);
}

/* HR */
hr {
    border: none;
    height: 1px;
    background: #cbd5e1;
}
</style>
""", unsafe_allow_html=True)

# ======================
# DATABASE
# ======================
def create_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    return conn

conn = create_connection()
cursor = conn.cursor()

def create_users_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()

create_users_table()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(name, email, password):
    try:
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(email, password):
    hashed_password = hash_password(password)
    cursor.execute(
        "SELECT name FROM users WHERE email = ? AND password = ?",
        (email, hashed_password)
    )
    user = cursor.fetchone()
    return user

# ======================
# SESSION STATE
# ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = ""

if "model" not in st.session_state:
    st.session_state.model = None

if "vectorizer" not in st.session_state:
    st.session_state.vectorizer = None

if "example_job" not in st.session_state:
    st.session_state.example_job = ""

# ======================
# SIMPLE NLP PREPROCESS
# ======================
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9@+$ ]", " ", text)
    tokens = text.split()

    stop_words = {
        "the", "is", "am", "are", "was", "were", "be", "been", "being",
        "a", "an", "and", "or", "but", "if", "then", "than", "to", "from",
        "of", "in", "on", "for", "with", "at", "by", "about", "into",
        "through", "during", "before", "after", "above", "below", "up",
        "down", "out", "off", "over", "under", "again", "further", "once",
        "here", "there", "when", "where", "why", "how", "all", "any",
        "both", "each", "few", "more", "most", "other", "some", "such",
        "no", "nor", "not", "only", "own", "same", "so", "too", "very",
        "can", "will", "just", "your", "you", "we", "our", "us", "they",
        "them", "their", "this", "that", "these", "those"
    }

    filtered = [word for word in tokens if word not in stop_words and len(word) > 2]
    return filtered

def detect_nlp_scam_patterns(text):
    scam_keywords = [
        "earn", "money", "quick", "profit", "guaranteed", "instant",
        "cash", "income", "bonus", "fast", "weekly", "daily", "urgent",
        "whatsapp", "telegram", "easy", "offer", "limited", "immediate",
        "hiring", "selected", "win", "payment", "salary", "remote"
    ]

    words = preprocess_text(text)
    matches = []

    for word in words:
        if word in scam_keywords:
            matches.append(word)

    return list(sorted(set(matches)))

def detect_missing_company_details(text):
    issues = []
    lower_text = text.lower()

    company_terms = ["company", "website", "role", "responsibilities", "requirements", "location"]
    found_terms = sum(1 for term in company_terms if term in lower_text)

    if found_terms <= 1:
        issues.append("Very limited company/job details")

    if "@" not in text and "website" not in lower_text and "www." not in lower_text:
        issues.append("No official website or email mentioned")

    return issues

def detect_money_request(text):
    patterns = [
        r"training fee",
        r"registration fee",
        r"processing fee",
        r"pay.*fee",
        r"security deposit",
        r"equipment deposit",
        r"background check fee",
        r"send money",
        r"payment required"
    ]

    matches = []
    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            matches.extend(found)

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
        "EASY MONEY fast hiring process",
        "Selected candidates contact on Telegram immediately",
        "Pay training fee and get hired today",
        "Work from home, instant joining, no interview",
        "Limited vacancies apply now and earn fast cash"
    ]

    sample_legit_texts = [
        "We are looking for qualified candidates with relevant experience",
        "Please submit your resume through our official portal",
        "Competitive salary based on experience and qualifications",
        "Interview process will consist of multiple rounds",
        "Successful candidates will receive benefits",
        "Minimum 2 years experience required",
        "Submit application through company website",
        "Background check will be conducted",
        "Bachelor degree required for this position",
        "Professional development opportunities available",
        "Candidates should have communication and analytical skills",
        "The role includes customer handling and reporting responsibilities"
    ]

    texts = sample_scam_texts + sample_legit_texts
    labels = [1] * len(sample_scam_texts) + [0] * len(sample_legit_texts)

    vectorizer = TfidfVectorizer(
        max_features=150,
        stop_words="english",
        ngram_range=(1, 2)
    )
    X = vectorizer.fit_transform(texts)

    model = LogisticRegression(max_iter=300)
    model.fit(X, labels)

    return model, vectorizer

# ======================
# RULE DETECTION
# ======================
def detect_urgency(text):
    urgency_keywords = [
        "urgent", "immediate", "asap", "quick", "fast", "start now",
        "apply now", "last chance", "limited time", "join immediately",
        "hiring now", "instant joining"
    ]

    matches = []
    for keyword in urgency_keywords:
        if re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE):
            matches.append(keyword)

    return matches

def detect_salary_language(text):
    patterns = [
        r"\$\d{3,5}\s*(weekly|daily|monthly|per week|per day|per month)",
        r"earn\s+\$\d{3,}",
        r"high\s+salary\s+no\s+experience",
        r"guaranteed\s+(income|salary|payment)",
        r"\d{2,6}\s*(per day|per week|per month)",
        r"easy money",
        r"earn from home"
    ]

    matches = []
    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            if isinstance(found, list):
                for x in found:
                    if isinstance(x, tuple):
                        matches.append(" ".join([i for i in x if i]))
                    else:
                        matches.append(str(x))
            else:
                matches.append(str(found))

    return matches

def detect_contact_methods(text):
    patterns = [
        r"whatsapp",
        r"telegram",
        r"\+\d{10,}",
        r"cash\s*app",
        r"paypal",
        r"dm\s*me",
        r"direct\s*message",
        r"message\s*us",
        r"contact\s*us\s*on\s*telegram",
        r"contact\s*us\s*on\s*whatsapp"
    ]

    matches = []
    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            matches.extend(found)

    return matches

def detect_grammar_issues(text):
    issues = []

    if re.search(r"[A-Z]{4,}", text):
        issues.append("Excessive capitalization")

    if re.search(r"!{2,}", text):
        issues.append("Too many exclamation marks")

    if re.search(r"\?{2,}", text):
        issues.append("Too many question marks")

    professional_terms = [
        "experience", "qualification", "resume", "interview",
        "position", "responsibilities", "requirements", "skills"
    ]

    if not any(term in text.lower() for term in professional_terms):
        issues.append("Lacks professional job terminology")

    line_count = len([line for line in text.split("\n") if line.strip()])
    if line_count > 3:
        very_short_lines = [line for line in text.split("\n") if 0 < len(line.split()) <= 3]
        if len(very_short_lines) >= 3:
            issues.append("Poor sentence structure")

    return issues

def detect_too_good(text):
    patterns = [
        r"no\s+experience\s+needed",
        r"work\s+from\s+home",
        r"easy\s+money",
        r"no\s+interview",
        r"guaranteed\s+job",
        r"part\s*time\s+high\s+income",
        r"earn\s+without\s+experience",
        r"zero\s+qualification"
    ]

    matches = []
    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        if found:
            matches.extend(found)

    return matches

# ======================
# SCORE CALCULATION
# ======================
def calculate_scam_score(flags, ml_probability):
    score = 0
    score += len(flags["urgency"]) * 8
    score += len(flags["salary"]) * 12
    score += len(flags["contact"]) * 15
    score += len(flags["grammar"]) * 6
    score += len(flags["too_good"]) * 10
    score += len(flags["nlp_patterns"]) * 4
    score += len(flags["company_issues"]) * 8
    score += len(flags["money_request"]) * 18
    score += int(ml_probability * 25)

    return min(score, 100)

# ======================
# ANALYSIS
# ======================
def analyze_job(text):
    ml_probability = 0.0

    if st.session_state.model is not None and st.session_state.vectorizer is not None:
        transformed = st.session_state.vectorizer.transform([text])
        ml_probability = st.session_state.model.predict_proba(transformed)[0][1]

    red_flags = {
        "urgency": detect_urgency(text),
        "salary": detect_salary_language(text),
        "contact": detect_contact_methods(text),
        "grammar": detect_grammar_issues(text),
        "too_good": detect_too_good(text),
        "nlp_patterns": detect_nlp_scam_patterns(text),
        "company_issues": detect_missing_company_details(text),
        "money_request": detect_money_request(text)
    }

    score = calculate_scam_score(red_flags, ml_probability)
    red_flags["score"] = score
    red_flags["ml_probability"] = round(float(ml_probability) * 100, 2)

    return red_flags

def get_risk_label(score):
    if score >= 70:
        return "High Risk"
    elif score >= 35:
        return "Medium Risk"
    else:
        return "Low Risk"

def generate_recommendations(score):
    if score >= 70:
        return [
            "Do not share Aadhaar, PAN, bank details, OTP, or personal documents.",
            "Do not pay any registration fee, training fee, or deposit.",
            "Avoid communicating only through WhatsApp or Telegram.",
            "Verify the company on its official website and LinkedIn page.",
            "Report suspicious posts on the platform where you found them."
        ]
    elif score >= 35:
        return [
            "Research the company carefully before responding.",
            "Check whether the recruiter uses an official company email.",
            "Verify job details on LinkedIn, Glassdoor, or company careers page.",
            "Be cautious if they rush you into joining quickly.",
            "Never pay money to get hired."
        ]
    else:
        return [
            "The post looks relatively safer, but still verify the employer.",
            "Check the company website and role details before applying.",
            "Attend interviews only through official channels.",
            "Read the offer letter carefully before accepting."
        ]

# ======================
# LOAD MODEL
# ======================
if st.session_state.model is None:
    with st.spinner("Loading AI model..."):
        st.session_state.model, st.session_state.vectorizer = load_model()

# ======================
# AUTH PAGES
# ======================
if not st.session_state.logged_in:
    st.markdown("""
    <div class="hero-box">
        <h2>🛡️ AI Job Scam Detector</h2>
        <p>Create an account or login to continue and analyze suspicious job posts using Machine Learning and NLP-based detection.</p>
    </div>
    """, unsafe_allow_html=True)

    auth_tab1, auth_tab2 = st.tabs(["Login", "Create Account"])

    with auth_tab1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("Login to Your Account")

        st.markdown("**Email Address**")
        login_email = st.text_input(
            "Email Address",
            key="login_email",
            label_visibility="collapsed",
            placeholder="Enter your email address"
        )

        st.markdown("**Password**")
        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password",
            label_visibility="collapsed",
            placeholder="Enter your password"
        )

        if st.button("Login", key="login_btn"):
            if not login_email or not login_password:
                st.warning("Please fill all login fields.")
            else:
                user = login_user(login_email, login_password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user[0]
                    st.success(f"Welcome back, {user[0]}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
        st.markdown('</div>', unsafe_allow_html=True)

    with auth_tab2:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("Create Your Account")

        st.markdown("**Full Name**")
        signup_name = st.text_input(
            "Full Name",
            key="signup_name",
            label_visibility="collapsed",
            placeholder="Enter your name"
        )

        st.markdown("**Email Address**")
        signup_email = st.text_input(
            "Signup Email",
            key="signup_email",
            label_visibility="collapsed",
            placeholder="Enter your email address"
        )

        st.markdown("**Set Password**")
        signup_password = st.text_input(
            "Set Password",
            type="password",
            key="signup_password",
            label_visibility="collapsed",
            placeholder="Set up password"
        )

        st.markdown("**Confirm Password**")
        signup_confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm_password",
            label_visibility="collapsed",
            placeholder="Confirm password"
        )

        if st.button("Sign Up", key="signup_btn"):
            if not signup_name or not signup_email or not signup_password or not signup_confirm_password:
                st.warning("Please fill all signup fields.")
            elif signup_password != signup_confirm_password:
                st.error("Passwords do not match.")
            elif len(signup_password) < 6:
                st.warning("Password should be at least 6 characters.")
            else:
                created = add_user(signup_name, signup_email, signup_password)
                if created:
                    st.success("Account created successfully. Now login with your email and password.")
                else:
                    st.error("This email is already registered.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ======================
# SIDEBAR
# ======================
st.sidebar.markdown(f"### 👋 Welcome, {st.session_state.current_user}")
st.sidebar.markdown("Use the detector carefully and verify suspicious jobs through official sources.")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.rerun()

# ======================
# MAIN HEADER
# ======================
st.markdown("""
<div class="hero-box">
    <h1>🔍 AI Job Scam Detection System</h1>
    <p>Paste a job post below and the system will analyze scam indicators</p>
</div>
""", unsafe_allow_html=True)

# ======================
# MAIN TABS
# ======================
tab1, tab2 = st.tabs(["Analyze Job", "Red Flag Guide"])

with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        default_text = st.session_state.example_job if st.session_state.example_job else ""

        job_text = st.text_area(
            "Paste Job Post Here",
            value=default_text,
            height=320,
            placeholder="Paste the complete job description here..."
        )

        if job_text:
            words = len(job_text.split())
            chars = len(job_text)
            st.caption(f"Word count: {words} | Character count: {chars}")

        if st.button("Load Example Scam Job"):
            st.session_state.example_job = """URGENT HIRING!!!
Work from home and earn $5000 weekly
No experience needed
WhatsApp us at +1234567890
Immediate joining
Training fee required to confirm your slot"""
            st.rerun()

    with col2:
        st.markdown("""
        <div class="card-box">
            <h3>What to look for</h3>
            <p>🚨 Urgent hiring language</p>
            <p>💰 Unrealistic salary promises</p>
            <p>📱 WhatsApp / Telegram contact</p>
            <p>❗ Poor grammar / aggressive punctuation</p>
            <p>🎯 Too-good-to-be-true claims</p>
            <p>🏢 Missing company details</p>
            <p>💸 Any fee or payment request</p>
            <p>🧠 Suspicious NLP keywords</p>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Analyze Job Post", use_container_width=True):
        text_to_analyze = job_text.strip()

        if not text_to_analyze and st.session_state.example_job:
            text_to_analyze = st.session_state.example_job

        if not text_to_analyze:
            st.warning("Paste a job post first.")
        else:
            with st.spinner("Analyzing job post..."):
                result = analyze_job(text_to_analyze)
                score = result["score"]
                ml_score = result["ml_probability"]
                risk_label = get_risk_label(score)

                st.subheader("Analysis Result")

                st.markdown(f"""
                <div class="result-box">
                    <h3>Scam Probability: {score}%</h3>
                    <p><b>Risk Level:</b> {risk_label}</p>
                    <p><b>ML Confidence (Scam-like):</b> {ml_score}%</p>
                </div>
                """, unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Scam Score", f"{score}%")
                m2.metric("Risk Level", risk_label)
                m3.metric("ML Probability", f"{ml_score}%")
                red_flag_count = len([v for k, v in result.items() if k not in ["score", "ml_probability"] and v])
                m4.metric("Flag Categories", red_flag_count)

                st.progress(score / 100)

                if score >= 70:
                    st.error(f"High Scam Risk Detected ({score}%)")
                elif score >= 35:
                    st.warning(f"Medium Scam Risk ({score}%)")
                else:
                    st.success(f"Low Scam Risk ({score}%)")

                st.subheader("Detected Issues")
                displayed_any = False

                for key, value in result.items():
                    if key not in ["score", "ml_probability"] and value:
                        displayed_any = True
                        st.markdown(f"**{key.replace('_', ' ').title()}**")
                        for item in value:
                            st.write("-", item)

                if not displayed_any:
                    st.info("No strong rule-based red flags found, but always verify the company through official sources.")

                st.subheader("Recommendations")
                for rec in generate_recommendations(score):
                    st.write("-", rec)

with tab2:
    st.header("Common Job Scam Indicators")

    g1, g2 = st.columns(2)

    with g1:
        st.markdown("""
        <div class="card-box">
            <h3>Warning Signs</h3>
            <ul>
                <li>Urgent pressure to join immediately</li>
                <li>Unrealistic salary for little or no work</li>
                <li>Interview only on WhatsApp or Telegram</li>
                <li>No clear company name or official website</li>
                <li>No interview or no skill requirements</li>
                <li>Asking money for training or registration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown("""
        <div class="card-box">
            <h3>Safer Job Indicators</h3>
            <ul>
                <li>Official company email and website</li>
                <li>Clear role description and requirements</li>
                <li>Structured interview process</li>
                <li>Reasonable salary and responsibilities</li>
                <li>No payment request at any stage</li>
                <li>Verifiable company presence online</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ======================
# ABOUT SECTION AT BOTTOM
# ======================
st.markdown("""
<div class="about-box">
    <h2>About This Project</h2>
    <p>
        This application analyzes job posts and identifies possible scam indicators 
    </p>
    <p><b>Core Features:</b></p>
    <ul>
        <li>Scam probability score generation</li>
        <li>Urgent language and unrealistic salary detection</li>
        <li>Suspicious contact method identification</li>
        <li>Missing company details analysis</li>
        <li>Money request / fee demand detection</li>
        <li>User login and signup with SQLite database</li>
    </ul>
    <p><b>Disclaimer:</b> This tool provides risk assessment only and may not always be 100% accurate. Always verify job opportunities through official company websites and trusted job portals.</p>
</div>
""", unsafe_allow_html=True)

# ======================
# FOOTER
# ======================
st.markdown("""
<hr>
<div style="text-align:center; padding: 8px 0 25px 0;">
    <p><b>AI Job Scam Detection System</b></p>
   
    <p class="small-note">Always verify job offers through official company websites and trusted recruitment platforms.</p>
</div>
""", unsafe_allow_html=True)
