import asyncio

import google.generativeai as genai

from app.core.config import settings


def _configure_ai() -> None:
    if settings.GOOGLE_API_KEY:
        genai.configure(api_key=settings.GOOGLE_API_KEY)


def _fallback_review(code: str) -> str:
    findings = []
    if not code.strip():
        findings.append("- Add code before requesting a review.")
    if "eval(" in code:
        findings.append("- Avoid eval(); it can execute untrusted input.")
    if "console.log(" in code:
        findings.append("- Remove or gate console.log statements before production.")
    if "TODO" in code or "FIXME" in code:
        findings.append("- Resolve remaining TODO/FIXME items before shipping.")
    if not findings:
        findings.append("- No basic security or maintenance issues detected.")

    return "### Local Code Review\n\n" + "\n".join(findings) + (
        "\n\nAdd GOOGLE_API_KEY to enable the full Gemini-powered review."
    )


async def get_review(code: str) -> str:
    if not settings.GOOGLE_API_KEY:
        return _fallback_review(code)

    _configure_ai()

    prompt = f"Review this code:\n\n{code}"
    system_instruction = """
Role:
You are an expert Full-Stack Developer with deep knowledge of the MERN stack and DevOps practices. Your mission is to review code submitted by MERN stack developers and provide short, focused, high-impact feedback along with an improved version of the code.

Core Review Strategy:
1. Keep it Short & Impactful
- Use bullet points or concise sentences.
- Avoid long paragraphs, aim for clarity in minimal words.
- Prioritize the top 2-4 issues that matter most.
2. Lead with Positivity
- Start with 1-2 quick praises.
3. Point Out Mistakes Clearly
- Be honest but supportive.
- Avoid generic phrases, be specific about what needs fixing.
- Include a one-liner reason.
4. Show a Better Way
- Provide a clean and corrected version of the code snippet.
- Include best practices: modularity, error handling, naming, etc.
- No need to explain every change, let the code speak.
5. Warm Closure
- Use a quick, positive note to encourage the developer.
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as exc:
        error_string = str(exc)
        if "429" in error_string or "quota" in error_string or "RESOURCE_EXHAUSTED" in error_string:
            return """###  API Quota Exceeded

The Gemini API quota has been exhausted. Please add a paid billing method to your Google Cloud account.

Quick Fix:
1. Go to https://ai.google.dev/pricing
2. Add your billing details
3. Return and try again

Fallback Review:

###  What's Good
- Code structure looks organized
- Using async/await patterns

###  Needs Improvement
- Add comprehensive error handling
- Add input validation
- Include logging for debugging
- Add unit tests
- Document complex functions

Paid tier has unlimited requests!"""
        raise RuntimeError(f"Failed to generate code review: {error_string}") from exc
