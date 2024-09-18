import feedparser
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import spacy
from spacy.matcher import PhraseMatcher
import pandas as pd

# Load spaCy model for keyword matching
nlp = spacy.load('en_core_web_sm')
matcher = PhraseMatcher(nlp.vocab)

# Define Yahoo News RSS feed URLs
rss_urls = [
    "https://www.yahoo.com/news/rss/",  # Yahoo News Top Stories RSS feed
]

# Define national security-related topics
security_topics = [
    "terrorism", "attack", "cyberattack", "military", "security",
    "intelligence", "Hezbollah", "war", "nuclear", "bomb",
    "explosion", "spy", "threat", "Putin", "army", "Afghanistan",
    "defense", "bioweapon", "weapon", "warfare", "drone strike",
    "chemical weapon", "Russia", "China", "Beirut", "Iran", "assassinate"
]

# Adjusted weights for each topic
topic_weights = [
    2.5, 2.3, 2.2, 2.2, 2.0, 2.5, 3.0, 2.4, 2.1, 2.0,
    2.1, 2.2, 2.3, 2.1, 2.2, 2.0, 2.0, 2.1, 2.2, 2.1,
    2.0, 2.2, 2.1, 1.5, 1.5, 2.0
]

# Initialize tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Add security topics to PhraseMatcher
patterns = [nlp(text) for text in security_topics]
matcher.add("SECURITY_TOPICS", patterns)

def get_news_titles_and_links(rss_urls):
    articles = []
    for url in rss_urls:
        print(f"Fetching RSS feed from: {url}")
        feed = feedparser.parse(url)
        print(f"Feed parsed successfully: {feed.feed.get('title', 'No Title Found')}")
        for entry in feed.entries:
            article = {
                'title': entry.title,
                'link': entry.link,
                'summary': entry.summary if 'summary' in entry else ''  # Fetch summary if available
            }
            articles.append(article)
    return articles

def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.pooler_output.squeeze().numpy()

def keyword_boost(title, keywords, boost_value):
    """Check for keywords in the title and boost score if any are present."""
    doc = nlp(title.lower())
    matches = matcher(doc)
    if matches:
        return boost_value
    return 0

def rank_by_relevance(articles, security_topics, topic_weights):
    # Get embeddings for security topics
    topic_embeddings = [get_embedding(topic) for topic in security_topics]
    
    ranked_articles = []
    
    for article in articles:
        title = article['title']
        title_embedding = get_embedding(title)
        
        # Compute weighted similarity score
        scores = [cosine_similarity([title_embedding], [topic_emb])[0][0] * weight for topic_emb, weight in zip(topic_embeddings, topic_weights)]
        importance_score = np.sum(scores)  # Weighted sum of scores
        
        # Apply keyword boost
        boost_score = keyword_boost(title, security_topics, 100)  # Boost score by 100 if any keyword is present
        importance_score += boost_score
        
        # Add score to the article
        article['importance_score'] = importance_score
        ranked_articles.append(article)
    
    # Sort articles by importance score (descending order)
    ranked_articles.sort(key=lambda x: x['importance_score'], reverse=True)
    
    # Apply cutoff for "Important" based on the score threshold
    cutoff_threshold = 100  # Set the cutoff threshold
    for article in ranked_articles:
        article['importance'] = 'Important' if article['importance_score'] >= cutoff_threshold else 'Unimportant'
    
    return ranked_articles

# Save important articles to CSV
def save_important_articles_to_csv(articles, filename='/Users/jackmustonen/Intelligence Report Generator/important_articles.csv'):
    important_articles = [article for article in articles if article['importance'] == 'Important']
    df = pd.DataFrame(important_articles, columns=['title', 'link'])
    df.to_csv(filename, index=False)
    print(f"Important articles saved to {filename}")

# Fetch and rank articles
news_articles = get_news_titles_and_links(rss_urls)
ranked_articles = rank_by_relevance(news_articles, security_topics, topic_weights)

# Print ranked articles
'''
for article in ranked_articles:
    print(f"Title: {article['title']}")
    print(f"Link: {article['link']}")
    print(f"Importance Score: {article['importance_score']:.4f}")
    print(f"Importance: {article['importance']}")
    print("-" * 80)
'''

save_important_articles_to_csv(ranked_articles)
