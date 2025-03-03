import re
from pdf_helper import strip_filename


def process_document(markdown_text, model, original_filename, batch_type):
    """
    Process a document to extract and validate entities.

    Args:
        markdown_text (str): The markdown text to process

    Returns:
        dict: Extracted entities
    """
    extracted = extract_entities(markdown_text, model, original_filename, batch_type)
    return extracted


def extract_entities(markdown_text, model, original_filename, batch_type):
    """
    Extract key entities from city ordinance markdown text using rule-based matching.

    Args:
        markdown_text (str): The markdown text of the ordinance document

    Returns:
        dict: Dictionary containing extracted entities
    """
    entities = {
        "ordinance_number": None,
        "resolution_number": None,
        "proponent": None,
        "author": None,
        "title": None,
        "held_at": None,
    }

    labels = ["date", "author", "ordinance_number", "resolution_number"]

    gliner_result = model.predict_entities(markdown_text, labels)

    #

    for entity in gliner_result:
        print(entity["text"], "=>", entity["label"])

    if batch_type == "ORDINANCE":
        # Reformat filename: 2001-15.pdf -> 15-2001

        ordinance_number = strip_filename(original_filename)

        resolution_match = re.search(
            r"(?:RES[OQ]LUTION[_ ]*(?:NO\.?|NUMBER)[_ ]*|RES[OQ]LUTION[_ ]*)[:\.\-_ ]*(\d+(?:[- ]?\d+)*(?:-[A-Z])?)",
            markdown_text,
            re.IGNORECASE,
        )

        if resolution_match:
            entities["resolution_number"] = resolution_match.group(1).strip()
        else:
            for entity in gliner_result:
                if entity["label"] == "resolution_number":
                    entities["resolution_number"] = entity["text"]
                    break
        entities["ordinance_number"] = ordinance_number

    else:
        # Reformat filename: 2001-15.pdf -> 15-2001
        resolution_number = strip_filename(original_filename)

        ordinance_match = re.search(
            r"(?:ORDINANCE[_ ]*(?:NO\.?|NUMBER)[_ ]*|ORDINANCE[_ ]*)[:\.\-_ ]*(\d+(?:[- ]?\d+)*(?:-[A-Z])?)",
            markdown_text,
            re.IGNORECASE,
        )

        if ordinance_match:
            entities["ordinance_number"] = ordinance_match.group(1).strip()
        else:
            for entity in gliner_result:
                if entity["label"] == "ordinance_number":
                    entities["ordinance_number"] = entity["text"]
                    break

        entities["resolution_number"] = resolution_number
    # Extract ordinance_no with more robust pattern
    # ordinance_match = re.search(
    #     r"(?:ORDINANCE[_ ]*(?:NO\.?|NUMBER)[_ ]*|ORDINANCE[_ ]*)[:\.\-_ ]*(\d+(?:[- ]?\d+)*(?:-[A-Z])?)",
    #     markdown_text,
    #     re.IGNORECASE,
    # )

    # if not ordinance_match:
    #     for entity in gliner_result:
    #         if entity["label"] == "ordinance_number":
    #             entities["ordinance_number"] = entity["text"]
    #             break

    # if ordinance_match:
    #     entities["ordinance_number"] = ordinance_match.group(1).strip()

    # # Extract resolution_no with more robust pattern
    # resolution_match = re.search(
    #     r"(?:RES[OQ]LUTION[_ ]*(?:NO\.?|NUMBER)[_ ]*|RES[OQ]LUTION[_ ]*)[:\.\-_ ]*(\d+(?:[- ]?\d+)*(?:-[A-Z])?)",
    #     markdown_text,
    #     re.IGNORECASE,
    # )
    # if not resolution_match:
    #     for entity in gliner_result:
    #         if entity["label"] == "resolution_number":
    #             entities["resolution_number"] = entity["text"]
    #             break

    # if resolution_match:
    #     entities["resolution_number"] = resolution_match.group(1).strip()

    # Extract proponent
    proponent_match = re.search(r"Proponent:\s+(.*?)$", markdown_text, re.MULTILINE)

    if not proponent_match:
        proponent_match = re.search(
            r"## Proponent:\s+(.*?)$", markdown_text, re.MULTILINE
        )

    if not proponent_match:
        for entity in gliner_result:
            if entity["label"] == "author":
                proponent_match = entity["text"]
                break

    if proponent_match:
        entities["proponent"] = proponent_match.group(1).strip()

    if entities["proponent"]:
        entities["author"] = entities["proponent"]

    # Extract title with more robust pattern that keeps the "AN ORDINANCE" prefix
    title_match = re.search(
        r"((?:AN\s+ORDINANCE|A\s+RESOLUTION)\s+.*?)(?:\s+APPROVED\s+ON|\s+WHEREAS|\s+BE\s+IT\s+|$)",
        markdown_text,
        re.IGNORECASE | re.DOTALL,
    )

    # Alternative title match pattern for difficult cases
    if not title_match:
        title_match = re.search(
            r"((?:ORDINANCE|RESOLUTION)[^A-Za-z0-9]*(?:NO\.?|NUMBER)?[^A-Za-z0-9]*(?:\d+(?:[- ]?\d+)*(?:-[A-Z])?)?\s*[:\-]?\s*.*?)(?:\s+APPROVED\s+ON|\s+WHEREAS|\s+BE\s+IT\s+|$)",
            markdown_text,
            re.IGNORECASE | re.DOTALL,
        )

    if title_match:
        # Clean up the title - remove excessive whitespace and normalize
        title = re.sub(r"\s+", " ", title_match.group(1).strip())
        entities["title"] = title

    # Extract date (held_at) - make pattern more flexible
    date_match = re.search(r"SESSION HALL ON ([A-Z]+ \d+, \d{4})", markdown_text)
    if not date_match:
        date_match = re.search(
            r"HELD AT THE SESSION HALL ON ([A-Z]+ \d+, \d{4})", markdown_text
        )
    if not date_match:
        # The date will usually be in the first 100 words
        for entity in gliner_result:
            if entity["label"] == "date":
                entities["held_at"] = entity["text"]
                break
    else:
        entities["held_at"] = date_match.group(1)

    return entities
