import streamlit as st
import pandas as pd
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
def get_sentiment(text):

    if not text:
        return "Neutral"

    score = TextBlob(
        text
    ).sentiment.polarity

    if score > 0:
        return "Positive"

    elif score < 0:
        return "Negative"

    return "Neutral"
def create_wordcloud(articles):

    text = " ".join(
        article.get("title", "")
        for article in articles
    )

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white"
    ).generate(text)

    return wordcloud
API_KEY = st.secrets["NEWS_API_KEY"]
create_database()
st.title("📰 News App")



location = st.text_input(
    "Enter a location or keyword"
)
category = st.sidebar.selectbox(
    "Choose Category",
    [
        "All",
        "Technology",
        "Business",
        "Sports",
        "Health"
    ]
)
st.sidebar.subheader(
    "Recent Searches"
)

recent_searches = get_recent_searches()

for location_, category_ in recent_searches:

    st.sidebar.write(
        f"{location_} - {category_}"
    )


    
if st.button("Get News"):

    save_search(
    location,
    category
    )
    query = location

    if category != "All":
        query += f" AND {category}"
    

    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}"
        f"&sortBy=publishedAt"
        f"&language=en"
        f"&pageSize=10"
        f"&apiKey={API_KEY}"
    )
    with st.spinner("Fetching latest news..."):
        response = requests.get(url)
        data = response.json()

    articles = data.get("articles", [])
    news_data = []
    for article in articles:
        news_data.append({
            "Title": article.get("title"),
            "Source": article["source"]["name"],
            "Published": article.get("publishedAt"),
            "URL": article.get("url")
        })
    df = pd.DataFrame(news_data)
    st.download_button(
        "📥 Download News CSV",
        df.to_csv(index=False),
        file_name="news.csv",
        mime="text/csv"
        )
    if not articles:
        st.error("No news found.")
        st.stop()
    st.success(
    f"Found {len(articles)} articles"
    )
    if articles:
        st.subheader("☁️ Trending Topics")
        wordcloud = create_wordcloud(articles)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud)
        ax.axis("off")
        st.pyplot(fig)

    for article in articles:
        date = article["publishedAt"]
        formatted_date = datetime.strptime(
            date,
            "%Y-%m-%dT%H:%M:%SZ"
            )
        description = article.get("description", "")
        sentiment = get_sentiment(description)
        
        

        with st.container(border=True):
            st.subheader(
                article["title"]
                )
            if article.get("urlToImage"):
                st.image(
                    article["urlToImage"]
        )
            st.write(
                description if description
                else "No description available."
                )
            st.write(
                f"Sentiment: {sentiment}"
                )
            st.write(
                formatted_date.strftime(
                    "%d %B %Y %I:%M %p"
                    )
                )
            st.link_button(
                "📖 Read Full Article",
                article["url"]
            )