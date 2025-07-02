import re

def json_to_markdown(data):
    md = f"# {data['title']}\n\n"

    for section in data['sections']:
        section_type = section['type']

        if section_type == "heading":
            level = section.get("level", 2)
            md += f"{'#' * level} {section['text']}\n\n"

        elif section_type == "paragraph":
            md += f"{section['text']}\n\n"

        elif section_type == "list":
            for i, item in enumerate(section['items']):
                bullet = f"{i + 1}." if section.get('ordered', False) else "-"
                md += f"{bullet} {item}\n"
            md += "\n"

        elif section_type == "blockquote":
            md += f"> {section['text']}\n\n"

        elif section_type == "code":
            language = section.get("language", "")
            code = section.get("code", "")
            md += f"```{language}\n{code}\n```\n\n"

        elif section_type == "table":
            headers = section['headers']
            md += f"{' | '.join(headers)}\n"
            md += f"{' | '.join(['---'] * len(headers))}\n"
            for row in section['rows']:
                md += f"{' | '.join(row)}\n"
            md += "\n"

        elif section_type == "image":
            alt = section.get("alt", "")
            src = section.get("src", "")
            md += f"![{alt}]({src})\n"
            caption = section.get("caption")
            if caption:
                md += f"*{caption}*\n"
            md += "\n"

    return md.strip()

def clean_markdown(text):
    # Convert literal '\n' to real newlines
    text = text.replace('\\n', '\n')

    # Fix malformed headings (ensure a space after #s)
    text = re.sub(r'(#+)([^\s#])', r'\1 \2', text)

    # Remove accidental double hashes (if not intentional)
    text = re.sub(r'#+\s*(#+)', r'\1', text)

    # Optional: strip trailing spaces on each line
    text = "\n".join(line.rstrip() for line in text.splitlines())

    return text.strip()

def json_to_clean_markdown(data):
    return clean_markdown(json_to_markdown(data))
