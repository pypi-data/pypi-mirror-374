from typing import Optional

from langchain_llm7 import ChatLLM7
from llmatch_messages import llmatch
from langchain_core.messages import SystemMessage, HumanMessage


def generate_readme_from_llm(
    llm: Optional[ChatLLM7] = None,
    package_text: str = "",
    author_name: Optional[str] = None,
    author_email: Optional[str] = None,
    repo_link: Optional[str] = None,
    verbose: bool = False,
) -> str:
    """
    Generate a README.md for a Python package using an LLM.

    Parameters:
      llm: preconfigured ChatLLM7 instance. If None, a default is created with codestral-2501.
      package_text: plain text containing the package name, source code, and optional setup.py content.
      author_name, author_email, repo_link: optional metadata for the README.
      verbose: whether to print verbose llm interaction.

    Returns:
      The README.md content as a string, or a fallback message if generation fails.
    """
    if llm is None:
        llm = ChatLLM7(model="codestral-2501", temperature=0, base_url="https://api.llm7.io/v1")

    system_content = (
        "You are a helpful assistant that creates a polished README.md for a Python package. "
        "Return the content wrapped only in a single tag <README_MD>... </README_MD> and nothing else. "
        "Include installation, usage, and a short example. Include an author section if metadata is provided."
    )

    human_content = (
        f"Package content:\n{package_text}\n"
        f"Author: {author_name or ''} <{author_email or ''}>\n"
        f"Repository: {repo_link or ''}\n"
        "Please generate the README.md accordingly, wrapped as requested."
    )

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]

    pattern = r"<README_MD>\s*(.*?)\s*</README_MD>"

    resp = llmatch(
        llm=llm,
        messages=messages,
        pattern=pattern,
        verbose=verbose,
    )

    if resp.get("success"):
        extracted = resp.get("extracted_data", [])
        if extracted:
            return extracted[0]

    return "# README\n\nUnable to generate via LLM."