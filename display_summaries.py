import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import pipeline
import os

# Set up logging
logging.basicConfig(filename='/Users/jackmustonen/Intelligence Report Generator/display_summaries.log', level=logging.DEBUG)

# Load the summarization pipeline
summarizer = pipeline('summarization')

def load_important_articles_from_csv(filename='/Users/jackmustonen/Intelligence Report Generator/important_articles.csv'):
    if not os.path.isfile(filename):
        logging.error(f"File not found: {filename}")
    else:
        logging.info(f"Loading file: {filename}")
    return pd.read_csv(filename)

def save_important_articles_to_csv(df, filename='/Users/jackmustonen/Intelligence Report Generator/important_articles.csv'):
    df.to_csv(filename, index=False)

def summarize_text(text):
    def chunk_text(text, max_length=1024):
        return [text[i:i + max_length] for i in range(0, len(text), max_length)]
    
    chunks = chunk_text(text)
    summaries = []
    for chunk in chunks:
        chunk_length = len(chunk)
        dynamic_max_length = min(200, chunk_length)
        if dynamic_max_length < 50:
            dynamic_max_length = 50
        
        summary = summarizer(chunk, max_length=dynamic_max_length, min_length=30, do_sample=False)
        logging.info(f"Summary generated: {summary[0]['summary_text']}")
        summaries.append(summary[0]['summary_text'])
    
    return ' '.join(summaries)

def fetch_and_summarize_article(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        article_body_div = soup.find('div', class_='caas-body')
        if article_body_div:
            article_content = article_body_div.get_text(separator='\n', strip=True)
            logging.info(f"Article content fetched from {url}: {article_content[:500]}...")  # Log first 500 characters
            if len(article_content) < 1000:
                return article_content
            return summarize_text(article_content)
        else:
            return f"Failed to find the article body in {url}"
    except Exception as e:
        logging.error(f"Failed to fetch article from {url}: {e}")
        return f"Failed to fetch article from {url}: {e}"

# Load important articles
articles_df = load_important_articles_from_csv()

logging.info(f"DataFrame loaded with {len(articles_df)} rows.")

if not articles_df.empty:
    articles_df['summary'] = articles_df['link'].apply(fetch_and_summarize_article)
    logging.info("Summaries added to DataFrame.")
    save_important_articles_to_csv(articles_df)
else:
    logging.info("No articles found or DataFrame is empty.")

logging.info("Script completed.")
