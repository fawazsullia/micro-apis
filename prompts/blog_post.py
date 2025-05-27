def get_blog_post_prompt(content: str) -> str:
    prompt ="""
    You are an expert in creating blog posts. Given the following blog outline, turn it into a full blog post.
    The output should be in markdown format with proper headings, subheadings, and formatting.

    Here is the blog outline to create a full blog post from:
    ***********************
    {content}
    ***********************
    Ensure that the blog post is engaging, informative, and well-structured. Use appropriate tags for headings, paragraphs, lists, and other elements to enhance readability.
    Make sure the content flows logically and maintains the reader's interest throughout.
    The blog post should be suitable for publication on a blog platform, with a clear introduction, body, and conclusion.
    The blog post should be written in a way that is easy to read and understand by a general audience.
    The blog post should be written as it was written by a human, with a natural tone and style that reflects the topic and audience.
    The resulting markdown should be well-formatted and ready for publication.
    Do not include any additional explanations or comments in the output, just the HTML content.
    Do not use escape characters for line breaks.
    """
    return prompt.format(content=content)