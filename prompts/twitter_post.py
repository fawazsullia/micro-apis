from typing import Optional

def get_twitter_post_prompt(content: str, count: int, styleExample: Optional[str] = None) -> str:
    prompt = f"""
You are a social media strategist creating high-performing Twitter posts based on long-form content.

Input content:
\"\"\"
{content}
\"\"\"

Your task:
- Generate exactly {count} unique Twitter posts.
- Each should be within Twitter’s 280-character limit.
- Write in a clear, human, relatable tone — avoid robotic phrasing.
- Use different tones if possible: e.g., informative, witty, bold, inspirational.
- Avoid fluff and excessive hashtags — use only 1–2 if highly relevant.
- Don't mention "this video" or "this content" — write as if you’re the original poster.
{"Style example:\n" + styleExample if styleExample else ""}

Output must be a JSON object:
{{
  "posts": [
    {{
      "content": "Your tweet text here.",
      "hashtags": ["#example"],
      "tone": "informative"
    }},
    ...
  ],
  "count": {count}
}}

Only return raw, valid JSON. Do NOT wrap in markdown or quotes. Do NOT explain anything. Just return the JSON.
"""
    return prompt
