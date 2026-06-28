import streamlit as st

import html
from textblob import TextBlob
import requests
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from database import (
    create_database,
    save_search,
    get_recent_searches
)

st.set_page_config(
    page_title="NewsPulse",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CSS Styling ----------------
st.markdown("""
<style>
    /* Hide only the Deploy button */
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }

    [data-testid="stDeployButton"] {
        display: none !important;
        visibility: hidden !important;
    }

    [data-testid="stAppDeployButton"] {
        display: none !important;
        visibility: hidden !important;
    }

    button[title="Deploy"] {
        display: none !important;
        visibility: hidden !important;
    }

    a[title="Deploy"] {
        display: none !important;
        visibility: hidden !important;
    }
    .stApp {
        background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.22), transparent 35%),
        radial-gradient(circle at top right, rgba(14, 165, 233, 0.18), transparent 30%),
        linear-gradient(135deg, #020617 0%, #0f172a 50%, #111827 100%);
        color: #e5e7eb;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        position: relative;
        padding: 42px;
        border-radius: 30px;
        background:
        linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.82)),
        radial-gradient(circle at right, rgba(59, 130, 246, 0.30), transparent 35%);
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 25px 70px rgba(0, 0, 0, 0.35);
        color: white;
        margin-bottom: 28px;
        overflow: hidden;
    }
    .hero::after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -70px;
        top: -70px;
        background: rgba(96, 165, 250, 0.18);
        border-radius: 50%;
        filter: blur(8px);
    }
    .hero h1 {
        font-size: 52px;
        font-weight: 900;
        letter-spacing: -1px;
        margin-bottom: 8px;
    }
    .hero p {
        font-size: 18px;
        color: #cbd5e1;
        max-width: 760px;
    }
    .search-panel {
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-radius: 26px;
        padding: 26px;
        margin: 24px 0;
        box-shadow: 0 20px 55px rgba(0, 0, 0, 0.28);
        backdrop-filter: blur(18px);
    }
    .search-panel-title {
        color: #f8fafc;
        font-size: 26px;
        font-weight: 850;
    }
    .search-panel-subtitle {
        color: #94a3b8;
        font-size: 15px;
        margin-top: 5px;
    }
    .visual-card {
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 24px;
        padding: 22px;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.25);
        margin-bottom: 24px;
    }
    .section-title {
        font-size: 24px;
        font-weight: 850;
        color: #f8fafc;
        margin: 24px 0 14px 0;
    }
    .custom-metric {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.24);
    }
    .custom-metric-label {
        color: #94a3b8;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .custom-metric-value {
        color: #f8fafc;
        font-size: 34px;
        font-weight: 900;
    }
    .custom-metric-sub {
        color: #60a5fa;
        font-size: 13px;
        margin-top: 4px;
    }
    

    

    
    
    .news-card {
        position: relative;
        display: grid;
        grid-template-columns: 250px 1fr;
        gap: 24px;
        padding: 18px;
        margin-bottom: 24px;
        border-radius: 24px;
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.92));
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
        overflow: hidden;
        transition: all 0.25s ease;
    }
    .news-card:hover {
        transform: translateY(-4px);
        border-color: rgba(96, 165, 250, 0.45);
        box-shadow: 0 24px 70px rgba(37, 99, 235, 0.20);
    }
    .news-card::before {
        content: "";
        position: absolute;
        left: 0;
        top: 22px;
        bottom: 22px;
        width: 4px;
        border-radius: 999px;
        background: linear-gradient(180deg, #60a5fa, #38bdf8);
    }
    .news-image {
        width: 100%;
        height: 175px;
        object-fit: cover;
        border-radius: 18px;
        display: block;
    }
    .news-content {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-width: 0;
    }
    .news-source {
        display: inline-block;
        width: fit-content;
        background: rgba(96, 165, 250, 0.14);
        color: #93c5fd;
        border: 1px solid rgba(96, 165, 250, 0.25);
        padding: 5px 11px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .news-title {
        color: #f8fafc;
        font-size: 23px;
        line-height: 1.35;
        font-weight: 800;
        margin-bottom: 9px;
    }
    .news-meta {
        color: #94a3b8;
        font-size: 13.5px;
        margin-bottom: 12px;
    }
    .news-description {
        color: #cbd5e1;
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 16px;
    }
    .news-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 14px;
    }
    .sentiment-pill {
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 800;
    }
    .pill-positive {
        background: rgba(34, 197, 94, 0.14);
        color: #86efac;
        border: 1px solid rgba(34, 197, 94, 0.24);
    }
    .pill-negative {
        background: rgba(239, 68, 68, 0.14);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.24);
    }
    .pill-neutral {
        background: rgba(148, 163, 184, 0.14);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.24);
    }
    .read-link {
        color: #60a5fa !important;
        text-decoration: none !important;font-size: 14px;
        font-weight: 800;
        padding: 8px 13px;
        border-radius: 999px;
        background: rgba(37, 99, 235, 0.12);
        border: 1px solid rgba(96, 165, 250, 0.24);
    }
    .read-link:hover {
        background: rgba(37, 99, 235, 0.22);
        color: #bfdbfe !important;
    }
    @media (max-width: 768px) {
        .news-card {
            grid-template-columns: 1fr;
        }
        .news-image {
            height: 220px;
        }
        .news-footer {
            flex-direction: column;
            align-items: flex-start;
        }
    }

    

    .sidebar-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    div.stButton > button {
        background-color: #2563eb;
        color: white;
        border-radius: 12px;
        height: 48px;
        font-weight: 700;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- Functions ----------------
def get_sentiment(text):
    
    if not text:
        return "Neutral"

    score = TextBlob(text).sentiment.polarity

    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    return "Neutral"





def create_wordcloud(articles):
    text = " ".join(
        article.get("title", "")
        for article in articles
        if article.get("title")
    )

    if not text.strip():
        return None

    wordcloud = WordCloud(
        width=1000,
        height=450,
        background_color="white",
        colormap="viridis"
    ).generate(text)

    return wordcloud


def format_date(date_string):
    try:
        date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        return date.strftime("%d %B %Y • %I:%M %p")
    except:
        return "Date not available"


# ---------------- App Start ----------------
API_KEY = st.secrets["NEWS_API_KEY"]

create_database()

# ---------------- Sidebar ----------------
st.sidebar.markdown("<div class='sidebar-title'>🗂️ Recent Searches</div>", unsafe_allow_html=True)

recent_searches = get_recent_searches()

if recent_searches:
    for location_, category_ in recent_searches:
        st.sidebar.info(f"{location_} • {category_}")
else:
    st.sidebar.write("No recent searches yet.")

st.sidebar.markdown("---")
st.sidebar.write("### About")
st.sidebar.write(
    "NewsPulse is a Streamlit-based news app that fetches latest articles using News API."
)

# ---------------- Hero Section ----------------
st.markdown("""
<div class="hero">
    <h1>📰 NewsPulse</h1>
    <p>Search latest news, track trends, analyze sentiment, and download articles instantly.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- Premium Search Area ----------------
st.markdown("""
<div class="search-panel">
    <div class="search-panel-title">Discover Latest Stories</div>
    <div class="search-panel-subtitle">
        Search breaking news, technology updates, sports headlines, business trends and more.
    </div>
</div>
""", unsafe_allow_html=True)
country_codes = {
    "Argentina": "ar",
    "Australia": "au",
    "Austria": "at",
    "Belgium": "be",
    "Brazil": "br",
    "Bulgaria": "bg",
    "Canada": "ca",
    "China": "cn",
    "Colombia": "co",
    "Cuba": "cu",
    "Czech Republic": "cz",
    "Egypt": "eg",
    "France": "fr",
    "Germany": "de",
    "Greece": "gr",
    "Hong Kong": "hk",
    "Hungary": "hu",
    "India": "in",
    "Indonesia": "id",
    "Ireland": "ie",
    "Israel": "il",
    "Italy": "it",
    "Japan": "jp",
    "Malaysia": "my",
    "Mexico": "mx",
    "Morocco": "ma",
    "Netherlands": "nl",
    "New Zealand": "nz",
    "Nigeria": "ng",
    "Norway": "no",
    "Philippines": "ph",
    "Poland": "pl",
    "Portugal": "pt",
    "Romania": "ro",
    "Saudi Arabia": "sa",
    "Singapore": "sg",
    "South Africa": "za",
    "South Korea": "kr",
    "Sweden": "se",
    "Switzerland": "ch",
    "Thailand": "th",
    "Turkey": "tr",
    "UAE": "ae",
    "UK": "gb",
    "USA": "us"
}

search_col, country_col, category_col, results_col, button_col = st.columns([2, 1.2, 1.3, 1, 1])

with search_col:
    location = st.text_input(
        "Search Topic",
        placeholder="Search India, AI, Cyber Security, Cricket..."
    )
with country_col:
    country = st.selectbox(
        "Country",
        list(country_codes.keys()),
        index=list(country_codes.keys()).index("India")
    )

with category_col:
    category = st.selectbox(
        "News Category",
        [
            "All",
            "Technology",
            "Business",
            "Sports",
            "Health",
            "Science",
            "Entertainment"
        ]
    )
with results_col:
    result_limit = st.selectbox(
        "Results",
        [5, 10, 20, 50],
        index=1
    )

with button_col:
    st.write("")
    st.write("")
    search_button = st.button("Search News", use_container_width=True)
country_codes = {
    "Argentina": "ar",
    "Australia": "au",
    "Austria": "at",
    "Belgium": "be",
    "Brazil": "br",
    "Bulgaria": "bg",
    "Canada": "ca",
    "China": "cn",
    "Colombia": "co",
    "Cuba": "cu",
    "Czech Republic": "cz",
    "Egypt": "eg",
    "France": "fr",
    "Germany": "de",
    "Greece": "gr",
    "Hong Kong": "hk",
    "Hungary": "hu",
    "India": "in",
    "Indonesia": "id",
    "Ireland": "ie",
    "Israel": "il",
    "Italy": "it",
    "Japan": "jp",
    "Latvia": "lv",
    "Lithuania": "lt",
    "Malaysia": "my",
    "Mexico": "mx",
    "Morocco": "ma",
    "Netherlands": "nl",
    "New Zealand": "nz",
    "Nigeria": "ng",
    "Norway": "no",
    "Philippines": "ph",
    "Poland": "pl",
    "Portugal": "pt",
    "Romania": "ro",
    "Russia": "ru",
    "Saudi Arabia": "sa",
    "Serbia": "rs",
    "Singapore": "sg",
    "Slovakia": "sk",
    "Slovenia": "si",
    "South Africa": "za",
    "South Korea": "kr",
    "Sweden": "se",
    "Switzerland": "ch",
    "Taiwan": "tw",
    "Thailand": "th",
    "Turkey": "tr",
    "UAE": "ae",
    "Ukraine": "ua",
    "UK": "gb",
    "USA": "us",
    "Venezuela": "ve"
}
# ---------------- Quick Topics ----------------
st.write("#### 🔥 Quick Topics")

quick_cols = st.columns(5)

quick_topics = ["AI", "India", "Cricket", "Technology", "Cyber Security"]

for i, topic in enumerate(quick_topics):
    with quick_cols[i]:
        if st.button(topic, use_container_width=True):
            location = topic
            search_button = True

# ---------------- Fetch News ----------------
if search_button:



    search_text = location.strip() if location.strip() else "Top Headlines"
    save_search(f"{search_text} - {country}", category)

    country_code = country_codes[country]
    if location.strip():
        # For city/region/topic search like Northland, Dehradun, AI, Cricket
        url = "https://newsapi.org/v2/everything"
        query = f"{location.strip()} {country}"
        if category != "All":
            query += f" {category}"
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": result_limit,
            "apiKey": API_KEY
        }
    else:
        # For country-wise top headlines
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": country_code,
            "pageSize": result_limit,
            "apiKey": API_KEY
        }
        if category != "All":
            params["category"] = category.lower()

    with st.spinner("Fetching latest news..."):
        response = requests.get(url, params=params)
        data = response.json()

    articles = data.get("articles", [])

    if not articles:
        st.error(
            f"No news found for '{location}' in {country}. Try a broader keyword like '{country}', 'Politics', 'Business', or 'Technology'."
        )
        st.stop()

    # ---------------- Metrics ----------------
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    for article in articles:
        sentiment = get_sentiment(article.get("description", ""))
        if sentiment == "Positive":
            positive_count += 1
        elif sentiment == "Negative":
            negative_count += 1
        else:
            neutral_count += 1

    st.markdown("<div class='section-title'>📊 News Overview</div>", unsafe_allow_html=True)
    metric1, metric2, metric3, metric4 = st.columns(4)
    with metric1:
        st.markdown(f"""
                    <div class="custom-metric">
                    <div class="custom-metric-label">Total Articles</div>
                    <div class="custom-metric-value">{len(articles)}</div>
                    <div class="custom-metric-sub">Fetched from News API</div>
                    </div>
                    """, unsafe_allow_html=True)
    with metric2:
        st.markdown(f"""
                    <div class="custom-metric">
                    <div class="custom-metric-label">Positive</div>
                    <div class="custom-metric-value">{positive_count}</div>
                    <div class="custom-metric-sub">Good news tone</div>
                </div>
                """, unsafe_allow_html=True)
    with metric3:
        st.markdown(f"""
                    <div class="custom-metric">
                    <div class="custom-metric-label">Negative</div>
                    <div class="custom-metric-value">{negative_count}</div>
                    <div class="custom-metric-sub">Serious tone</div>
                    </div>
                    """, unsafe_allow_html=True)
    with metric4:
        st.markdown(f"""
                    <div class="custom-metric">
                    <div class="custom-metric-label">Neutral</div>
                    <div class="custom-metric-value">{neutral_count}</div>
                    <div class="custom-metric-sub">Balanced tone</div>
                    </div>
                    """, unsafe_allow_html=True)
    

    st.markdown("<div class='section-title'>🗞️ Latest Stories</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📰 Articles", "☁️ Trending Topics"])

    # ---------------- Articles Tab ----------------
    with tab1:
        for article in articles:
            raw_title = article.get("title") or "No title available"
            raw_source = article.get("source", {}).get("name") or "Unknown source"
            raw_published = format_date(article.get("publishedAt", ""))
            raw_description = article.get("description") or "No description available."
            sentiment = get_sentiment(raw_description)
            title = html.escape(raw_title)
            source = html.escape(raw_source)
            published = html.escape(raw_published)
            description = html.escape(raw_description)
            image_url = article.get("urlToImage") or "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=900&q=80"
            article_url = article.get("url") or "#"
            image_url = html.escape(image_url, quote=True)
            article_url = html.escape(article_url, quote=True)
            if sentiment == "Positive":
                pill_class = "pill-positive"
            elif sentiment == "Negative":
                pill_class = "pill-negative"
            else:
                pill_class = "pill-neutral"
            card_html = f"""
            <div class="news-card">
<img class="news-image" src="{image_url}" alt="News image">
<div class="news-content">
<div class="news-source">{source}</div>
<div class="news-title">{title}</div>
<div class="news-meta">{published}</div>
<div class="news-description">{description}</div>
<div class="news-footer">
<span class="sentiment-pill {pill_class}">{sentiment} sentiment</span>
<a class="read-link" href="{article_url}" target="_blank" rel="noopener noreferrer">Read article →</a>
</div>
</div>
</div>
"""
            st.markdown(card_html, unsafe_allow_html=True)
        


    # ---------------- Trending Topics Tab ----------------
    with tab2:
        st.subheader("☁️ Trending Words From Headlines")

        wordcloud = create_wordcloud(articles)

        if wordcloud:
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.imshow(wordcloud)
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.info("Not enough text to generate word cloud.")

else:
    st.info("Search for a topic to see latest news.")
