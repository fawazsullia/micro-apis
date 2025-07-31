from typing import Optional

def get_reddit_post_prompt(content: str, count: int, styleExample: Optional[str] = None) -> str:
    prompt = f"""
You are a skilled Reddit content creator helping a YouTuber repurpose their video transcript into native Reddit posts.

Here is the source content:
\"\"\"
{content}
\"\"\"

Your task is to:
- Write {count} Reddit posts.
- Each post should include a compelling title and a post body written in Reddit-native tone (authentic, helpful, discussion-oriented).
- Avoid self-promotion or referring to "the video".
- Encourage engagement by ending with a thoughtful or open-ended question.
- Use a tone that feels natural to Reddit: informative, curious, or experience-driven.
- Do NOT include hashtags.
{"Here is a style example:\n" + styleExample if styleExample else ""}

Output format (must be valid raw JSON only, no markdown, no string escaping):
{{
  "posts": [
    {{
      "title": "Post title here",
      "content": "The main post content, suitable for Reddit.",
      "tone": "informative"
    }},
    ...
  ],
  "count": {count}
}}

Only return valid JSON. Do NOT explain anything. Do NOT wrap in backticks.
"""
    return prompt
