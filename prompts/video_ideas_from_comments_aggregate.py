from typing import List, Dict
from schemas import Comment

def get_video_ideas_aggregate_prompt(ideas: List[str]) -> str:
    ideas_text = "\n".join(ideas)

    prompt = f"""
You're an expert YouTube content strategist.

Your task is to read through the following ideas generate from youtube comments and aggregating them into 10-20 unique YouTube video ideas.

Here are the ideas:
{ideas_text}

Please generate 10-20unique YouTube video ideas that:
- That have frequent appearance in the ideas list
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
