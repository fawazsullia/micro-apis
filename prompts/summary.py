def get_summary_prompt(content: str):
    prompt = """
    You are an expert in summarizing content. Given the following text, create a concise summary that captures the main points and key details.

    Ensure that the summary is structured, clear, and engaging. The summary should be brief but informative, highlighting the most important aspects of the content.
    Here is the text to summarize:
    ***********************
    {content}
    ***********************
    Make sure to format the summary in a way that is easy to read and follow, using appropriate headings and bullet points if necessary.
    The summary should not have unnecessary details or filler content, but should instead focus on the core message and insights of the original text.
    """
    return prompt.format(content=content)