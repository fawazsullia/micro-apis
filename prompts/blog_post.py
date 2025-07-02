def get_blog_post_prompt(content: str) -> str:
    prompt ="""
You are an expert in creating blog posts. Given the following blog outline, turn it into a full blog post.
I will give you a blog outline with headings, subheadings, and bullet points.
Your task is to write the full blog post, and return the result as a structured JSON object in this format:

"{{
    "title": "AI in Cybersecurity: What You Need to Know",
    "sections": [
        {{
            "type": "heading",
            "level": 2,
            "text": "Introduction"
        }},
        {{
            "type": "paragraph",
            "text": "Artificial Intelligence (AI) is reshaping the cybersecurity landscape..."
        }},
        {{
            "type": "blockquote",
            "text": "AI doesn’t eliminate threats, it just changes the game."
        }},
        {{
            "type": "list",
            "ordered": true,
            "items": [
                "Detect anomalies",
                "Automate patching",
                "Respond to threats"
            ]
        }},
        {{
            "type": "code",
            "language": "python",
            "code": "def detect_threat(data):    return model.predict(data)"
        }},
        {{
            "type": "table",
            "headers": ["Tool", "Use Case"],
            "rows": [
                ["Snort", "Intrusion Detection"],
                ["Wireshark", "Packet Analysis"]
            ]
        }}
    ]
}}"

Use "type": "heading" with level 2 or 3 for headings/subheadings.
Use "paragraph" for body text.
Use "list" for bullets.
Ensure line breaks and logical section flow.

Here is the blog outline to create a full blog post from:
***********************
{content}
***********************

Ensure that the blog post is engaging, informative, and well-structured. Use appropriate tags for headings, paragraphs, lists, and other elements to enhance readability.
Make sure the content flows logically and maintains the reader's interest throughout.
The blog post should be suitable for publication on a blog platform, with a clear introduction, body, and conclusion.
The blog post should be written in a way that is easy to read and understand by a general audience.
The blog post should be written as it was written by a human, with a natural tone and style that reflects the topic and audience.
You do not have to include every headline or sub heading like call to action, conclusion etc. Use what makes sense for the content.
Do not include any additional explanations or comments in the output, just the HTML content.
Only return a valid JSON object. Do not wrap the response in triple backticks. Do not escape any characters. Do not return a string representation of JSON — just the JSON itself.
If the content is in first person, write the blog post in first person. If the content is in third person, write the blog post in third person.
"""
    return prompt.format(content=content)
