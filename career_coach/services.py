import json
import time
import requests
from django.conf import settings


# ─── System Prompt ───────────────────────────────────────────────────
CAREER_COACH_SYSTEM_PROMPT = """You are a professional Career Coach AI for Student Success Hub — an educational platform for students, alumni, and professionals.

You ONLY answer questions about:
- Career planning, job search strategies, career transitions
- Resume/CV writing, review, and optimization
- Interview preparation, techniques, and mock scenarios
- Skill development, learning paths, and certifications
- Industry insights, job market trends, and emerging roles
- Networking strategies and professional development
- Salary negotiation and workplace communication
- Internship and campus placement guidance
- Higher education decisions (Masters, MBA, PhD)
- LinkedIn profile and portfolio optimization
- Freelancing and entrepreneurship guidance
- Work-life balance and professional growth

If the user asks about ANYTHING outside career-related topics (coding help, cooking recipes, general knowledge, math problems, creative writing, etc.), you MUST politely decline and redirect:

"I appreciate your curiosity! However, I'm your dedicated Career Coach — I focus exclusively on career guidance and professional development. Could you rephrase your question to be about your career journey? For example, I can help with resumes, interviews, skill planning, or career strategy."

Guidelines:
- Be professional, warm, and encouraging
- Give specific, actionable advice with concrete next steps
- Use bullet points and clear formatting for readability
- When relevant, suggest resources or strategies the student can use on this platform (mentorship sessions, roadmaps, alumni connections)
- Tailor advice based on context (student, fresher, experienced professional)
- Keep responses concise but thorough (aim for 150-300 words)"""


# ─── Career Topic Keywords (Server-side Pre-filter) ──────────────────
CAREER_KEYWORDS = {
    'career', 'job', 'resume', 'cv', 'interview', 'salary', 'work',
    'internship', 'placement', 'hire', 'hiring', 'recruit', 'skill',
    'profession', 'industry', 'mentor', 'network', 'linkedin', 'portfolio',
    'promotion', 'manager', 'leadership', 'freelance', 'startup',
    'experience', 'qualification', 'certification', 'degree', 'mba',
    'masters', 'phd', 'company', 'corporate', 'business', 'role',
    'position', 'apply', 'application', 'cover letter', 'negotiate',
    'workplace', 'colleague', 'boss', 'team', 'project', 'goal',
    'growth', 'development', 'learning', 'course', 'training',
    'fresher', 'graduate', 'student', 'alumni', 'professional',
    'career change', 'switch', 'transition', 'opportunity', 'path',
    'roadmap', 'plan', 'strategy', 'advice', 'guidance', 'help',
    'what should i', 'how to', 'tips', 'prepare', 'improve',
}

# Keywords that strongly indicate non-career topics
NON_CAREER_KEYWORDS = {
    'recipe', 'cook', 'food', 'weather', 'movie', 'song', 'game',
    'joke', 'story', 'poem', 'write code', 'debug', 'compile',
    'math problem', 'equation', 'calculate', 'translate', 'language',
    'history of', 'capital of', 'president of', 'population',
}


def is_likely_career_related(message: str) -> bool:
    """Quick server-side check. Returns True if likely career-related.
    
    This is a SOFT filter — the LLM system prompt is the real guardrail.
    We only block obviously non-career queries here to save API calls.
    """
    msg_lower = message.lower().strip()
    
    # Very short messages are allowed (greetings, follow-ups)
    if len(msg_lower) < 15:
        return True
    
    # Check for strong non-career signals
    for keyword in NON_CAREER_KEYWORDS:
        if keyword in msg_lower:
            return False
    
    # If it contains career keywords, allow it
    for keyword in CAREER_KEYWORDS:
        if keyword in msg_lower:
            return True
    
    # Ambiguous — let the LLM system prompt handle it
    return True


# ─── API Integration ─────────────────────────────────────────────────

def call_openrouter(api_key: str, messages: list, model: str = None) -> dict:
    """Call OpenRouter API. Returns dict with 'content' and 'usage'."""
    if model is None:
        model = getattr(settings, 'CAREER_COACH_OPENROUTER_MODEL', 'meta-llama/llama-4-scout')
    
    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'HTTP-Referer': getattr(settings, 'SITE_URL', 'https://student-success-hub.onrender.com'),
        'X-OpenRouter-Title': 'Student Success Hub Career Coach',
    }
    payload = {
        'model': model,
        'messages': messages,
        'max_tokens': 1024,
        'temperature': 0.7,
    }
    
    start = time.time()
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    elapsed_ms = int((time.time() - start) * 1000)
    
    if response.status_code != 200:
        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
        error_msg = error_data.get('error', {}).get('message', response.text[:200])
        raise APIError(f"OpenRouter error ({response.status_code}): {error_msg}")
    
    data = response.json()
    content = data['choices'][0]['message']['content']
    usage = data.get('usage', {})
    
    return {
        'content': content,
        'usage': usage,
        'elapsed_ms': elapsed_ms,
        'model': data.get('model', model),
    }


def call_nvidia(api_key: str, messages: list, model: str = None) -> dict:
    """Call NVIDIA NIM API. Returns dict with 'content' and 'usage'."""
    if model is None:
        model = getattr(settings, 'CAREER_COACH_NVIDIA_MODEL', 'meta/llama-3.3-70b-instruct')
    
    url = 'https://integrate.api.nvidia.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': model,
        'messages': messages,
        'max_tokens': 1024,
        'temperature': 0.7,
    }
    
    start = time.time()
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    elapsed_ms = int((time.time() - start) * 1000)
    
    if response.status_code != 200:
        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
        error_msg = error_data.get('error', {}).get('message', response.text[:200])
        raise APIError(f"NVIDIA error ({response.status_code}): {error_msg}")
    
    data = response.json()
    content = data['choices'][0]['message']['content']
    usage = data.get('usage', {})
    
    return {
        'content': content,
        'usage': usage,
        'elapsed_ms': elapsed_ms,
        'model': data.get('model', model),
    }


def validate_api_key(provider: str, api_key: str) -> bool:
    """Quick validation — sends a minimal request to verify the key works."""
    test_messages = [
        {'role': 'user', 'content': 'Hi'}
    ]
    try:
        if provider == 'openrouter':
            call_openrouter(api_key, test_messages)
        elif provider == 'nvidia':
            call_nvidia(api_key, test_messages)
        else:
            return False
        return True
    except Exception:
        return False


def get_ai_response(provider: str, api_key: str, conversation_messages: list) -> dict:
    """
    Main entry point. Prepends the system prompt and calls the correct provider.
    
    Args:
        provider: 'openrouter' or 'nvidia'
        api_key: The decrypted API key
        conversation_messages: List of {'role': ..., 'content': ...} dicts
    
    Returns:
        dict with 'content', 'usage', 'elapsed_ms', 'model'
    """
    # Prepend system prompt
    messages = [
        {'role': 'system', 'content': CAREER_COACH_SYSTEM_PROMPT},
        *conversation_messages
    ]
    
    if provider == 'openrouter':
        return call_openrouter(api_key, messages)
    elif provider == 'nvidia':
        return call_nvidia(api_key, messages)
    else:
        raise ValueError(f"Unknown provider: {provider}")


class APIError(Exception):
    """Custom exception for API call failures."""
    pass
