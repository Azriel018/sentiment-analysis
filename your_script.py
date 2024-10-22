from supabase import create_client, Client
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Replace with your Supabase credentials
SUPABASE_URL = "https://gfrbuvjfnlpfqkylbnxb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdmcmJ1dmpmbmxwZnFreWxibnhiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjgwMjM0NDgsImV4cCI6MjA0MzU5OTQ0OH0.JmDB012bA04pPoD64jqTTwZIPYowFl5jzIVql49bwx4"

# Create Supabase client instance
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Fetch data from the 'feedback' table
response = supabase.table("feedback").select("feedback_id, pet_owner_id, sp_id, review").execute()
feedback_df = pd.DataFrame(response.data)

# Function to classify sentiment based on VADER's compound score
def classify_sentiment(score):
    if score >= 0.05:
        return "positive"
    elif score <= -0.05:
        return "negative"
    else:
        return "neutral"

# Analyze reviews and store sentiment scores and classifications in new columns
feedback_df["compound_score"] = feedback_df["review"].apply(lambda x: analyzer.polarity_scores(x)["compound"])
feedback_df["sentiment"] = feedback_df["compound_score"].apply(classify_sentiment)

# Update feedback records in Supabase
for index, row in feedback_df.iterrows():
    supabase.table("feedback").update({
        "compound_score": row["compound_score"],
        "sentiment": row["sentiment"]
    }).eq("feedback_id", row["feedback_id"]).execute()

print("Sentiment analysis job completed.")
