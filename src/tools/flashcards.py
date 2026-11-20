"""
Flashcard tools — turn subject content into importable study cards.

Cards are emitted as a plain-text file: one card per line, fields in the
order front, back, romanization, notes.
"""

from __future__ import annotations

from mcp import types

from ..resources.loader import ContentLoader

# Separator key -> (literal character, human-readable name)
SEPARATORS: dict[str, tuple[str, str]] = {
    "tab": ("\t", "a Tab character"),
    "comma": (",", "a comma (,)"),
    "pipe": ("|", "a pipe (|)"),
    "semicolon": (";", "a semicolon (;)"),
    "dash": (" - ", "a hyphen ( - )"),
}


def register_flashcard_tools(
    tools: list[types.Tool],
    handlers: dict,
    loader: ContentLoader,
    config: dict,
) -> None:

    subject_name = config.get("subject_name", "this subject")

    # --- generate_flashcards ---
    tools.append(
        types.Tool(
            name="generate_flashcards",
            description=(
                "Generate study flashcards from a topic or from raw text supplied by the user. "
                "Returns the reference material plus the exact .txt output format: one card per "
                "line, fields front, back, romanization, notes."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": (
                            "What to build the cards from: a topic keyword (searched in the "
                            "content library) or a block of raw text pasted by the user."
                        ),
                    },
                    "count": {
                        "type": "integer",
                        "description": "How many cards to generate. Defaults to 20.",
                    },
                    "separator": {
                        "type": "string",
                        "enum": ["tab", "comma", "pipe", "semicolon", "dash"],
                        "description": "Field separator for the output file. Defaults to 'tab'.",
                    },
                    "include_romanization": {
                        "type": "string",
                        "description": (
                            "Script to romanize in the third column (e.g. 'grego', 'latim'). "
                            "Omit to leave the column out."
                        ),
                    },
                    "include_notes": {
                        "type": "boolean",
                        "description": "Whether to fill the fourth column with a short note. Defaults to false.",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Where to write the .txt file. Defaults to 'flashcards.txt'.",
                    },
                },
                "required": ["content"],
            },
        )
    )

    async def handle_generate_flashcards(args: dict) -> str:
        content = args.get("content", "").strip()
        if not content:
            return "Please provide the content: a topic keyword or the raw text to turn into cards."

        count = args.get("count", 20)
        sep_key = args.get("separator", "tab")
        sep, sep_name = SEPARATORS.get(sep_key, SEPARATORS["tab"])
        romanization = args.get("include_romanization", "").strip()
        include_notes = args.get("include_notes", False)
        output_path = args.get("output_path", "").strip() or "flashcards.txt"

        results = loader.search(content)
        if results:
            snippets = "\n\n".join(r["snippet"] for r in results[:5])
            context_block = f"## Reference material\n\n{snippets}"
        else:
            context_block = (
                "## Reference material\n\n"
                "Nothing matched in the content library — treat the requested content itself "
                "as the source, and ground the cards in it."
            )

        if romanization and include_notes:
            columns = f"front{sep}back{sep}romanization{sep}notes"
            column_note = f"Romanize the {romanization} terms in the third column."
        elif romanization:
            columns = f"front{sep}back{sep}romanization"
            column_note = f"Romanize the {romanization} terms in the third column."
        elif include_notes:
            columns = f"front{sep}back{sep}{sep}notes"
            column_note = (
                "Leave the romanization column empty — the columns are positional, so notes "
                "still need the empty third field before them."
            )
        else:
            columns = f"front{sep}back"
            column_note = "Only the two required columns."

        return (
            f"## Flashcard Generation Request\n"
            f"**Subject:** {subject_name}\n"
            f"**Content:** {content}\n"
            f"**Cards requested:** {count}\n"
            f"**Separator:** {sep_name}\n"
            f"**Write to:** {output_path}\n\n"
            f"{context_block}\n\n"
            f"## Output format\n\n"
            f"Plain-text UTF-8 file, one card per line, no header, no numbering, no blank lines.\n"
            f"Columns are positional, in this order: front, back, romanization, notes.\n"
            f"Only front and back are required; trailing empty columns are left out.\n\n"
            f"For this request, each line is:\n\n"
            f"    {columns}\n\n"
            f"{column_note}\n\n"
            f"Rules:\n"
            f"- Separator for this file: {sep_name}. Spaces around the separator are optional.\n"
            f"- To put a separator inside a field, wrap that field in \"double quotes\".\n"
            f"- A literal double quote inside a quoted field is doubled: \"\".\n"
            f"- Math: $x^2$ inline, $$\\frac{{a}}{{b}}$$ for display. Quote the field if the "
            f"formula contains the separator.\n"
            f"- No markdown formatting outside of the math delimiters.\n\n"
            f"[The AI should now write {count} flashcards about '{content}' for {subject_name}, "
            f"grounded in the reference material above, in the language of that material, and "
            f"save them to {output_path} in exactly the format described.]"
        )

    handlers["generate_flashcards"] = handle_generate_flashcards
