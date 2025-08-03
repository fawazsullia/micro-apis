from typing import List, Dict
from schemas import Comment

def get_video_ideas_prompt(comments: List[Comment]) -> str:
    comments_text = "\n".join([f"{c.text}" for c in comments])

    prompt = f"""
You're an expert YouTube content strategist.

Your task is to read through the following viewer comments and come up with engaging and relevant YouTube video ideas that respond to common questions, themes, and interest areas.

Here are the comments:
{comments_text}

Please generate 5–10 unique YouTube video ideas that:
- Are based on patterns or interesting suggestions in the comments
- Are phrased as YouTube-friendly titles (e.g. "How I Made $1,000/month from a Side Project")
- Cover a variety of tones: tutorial, storytime, analysis, motivational, or question-based
- Are suitable for a general YouTube audience
- Avoid duplicates or vague suggestions

Return the results in this JSON format:

{{
  "ideas": [
    "Title 1",
    "Title 2",
    ...
  ],
  "count": total_number_of_ideas
}}

Only return valid JSON. Do NOT explain anything. Do NOT wrap in backticks.
"""
    return prompt
