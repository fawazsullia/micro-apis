def get_blog_outline_prompt(content: str) -> str:
    prompt ="""
    You are an expert in creating blog outlines. Given the following text, create a detailed blog outline that includes:
    1. A catchy title
    2. An introduction that sets the context and purpose of the blog
    3. Main sections with headings and subheadings
    4. Key points or bullet points under each section
    5. A conclusion that summarizes the main points and provides a call to action

    Ensure that the outline is structured, clear, and engaging. The title should be attention-grabbing and relevant to the content. The introduction should provide a brief overview of what the blog will cover. Each section should have a clear heading, and subheadings should be used to break down complex topics. Key points should be concise and informative.
    The conclusion should tie everything together and encourage readers to take action or reflect on the content.
    Here is the text to create a blog outline from:
    ***********************
    {content}
    ***********************
    Make sure to format the outline in a way that is easy to read and follow, using appropriate headings and bullet points.
    """ 
    return prompt.format(content=content)