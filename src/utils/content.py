def extract_text(content) -> str:

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        parts = []

        for block in content:

            if isinstance(block, str):
                parts.append(block)

            elif isinstance(block, dict):

                text = block.get("text")

                if text:
                    parts.append(text)

        return "\n".join(parts)

    return str(content)