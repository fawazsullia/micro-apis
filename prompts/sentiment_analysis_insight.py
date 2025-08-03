
from typing import List, Dict
from schemas import Comment

def build_sentiment_insight_prompt(comments: List[Comment]) -> str:
    comments_text = "\n".join([f"- {c.text}" for c in comments])
    return f"""
You are an AI assistant analyzing YouTube comments for insights.

Here are the comments:
{comments_text}

Please:
1. Classify each comment as positive, neutral, or negative.
2. Return the sentiment distribution as percentages.
3. Write a short summary of the overall sentiment.
4. Pick 3 especially positive comments (supportive, enthusiastic, grateful).
5. Pick up to 10 negative or concerning comments (critical, confused, negative tone, suggesting improvements).

Return only valid JSON in this exact format:

{{
  "summary": "Short summary of trends and tone",
  "distribution": {{
    "positive": 64.7,
    "neutral": 23.5,
    "negative": 11.8
  }},
  "top_positive_comments": [
    "I learned so much, thank you!",
    "This was super clear and helpful.",
    "Best video on this topic I've found."
  ],
  "top_negative_comments": [
    "The sound was too low to hear.",
    "You didn’t explain the key concept clearly.",
    "... up to 10 total ..."
  ]
}}
Only return valid JSON. Do NOT explain anything. Do NOT wrap in backticks.
"""
