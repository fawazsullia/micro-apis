import json

def build_aggregate_prompt(distributions, summaries, positives, negatives) -> str:
    return f"""
You are a sentiment analysis assistant. Below is the data gathered from multiple chunks of YouTube comments.

Distributions (from each chunk):
{json.dumps(distributions, indent=2)}

Summaries (from each chunk):
{json.dumps(summaries, indent=2)}

Top Positive Comments:
{json.dumps(positives, indent=2)}

Top Negative Comments:
{json.dumps(negatives, indent=2)}

Your tasks:
1. Combine the distributions to create an overall sentiment distribution in % (positive, neutral, negative).
2. Write a single clear, insightful summary covering the key themes and tones of the comments overall.
3. From the positive comments, select the 3 most impressive/appreciative ones.
4. From the negative comments, select the 10 most concerning, constructive, or common criticisms.

Return ONLY a valid JSON object in this format:

{{
  "summary": "...",
  "distribution": {{
    "positive": ...,
    "neutral": ...,
    "negative": ...
  }},
  "top_positive_comments": ["...", "...", "..."],
  "top_negative_comments": ["...", "..."]
}}
Only return valid JSON. Do NOT explain anything. Do NOT wrap in backticks.
"""
