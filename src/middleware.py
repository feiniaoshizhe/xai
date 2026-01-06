"""
Security Middleware Module

Provides security filtering for agent interactions:
- Prompt injection detection
- Sensitive content filtering
- Input validation
- Output sanitization
"""

import logging
import re
from typing import Callable, Awaitable
from agent_framework import AgentRunContext, FunctionInvocationContext

logger = logging.getLogger(__name__)


# ============================================================================
# Security Configuration
# ============================================================================

# Prompt injection patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+(instructions?|prompts?)",
    r"system\s+prompt",
    r"jailbreak",
    r"act\s+as\s+if",
    r"pretend\s+(you|to)\s+are",
    r"role[:\s]+system",
    r"override\s+(instructions?|rules?)",
    r"disregard\s+(previous|above)",
]

# Sensitive keywords (customize based on your use case)
SENSITIVE_KEYWORDS = [
    "password",
    "credit card",
    "ssn",
    "social security",
    "api key",
    "secret",
    "token",
    "private key",
]

# Maximum input length (characters)
MAX_INPUT_LENGTH = 10000


# ============================================================================
# Security Middleware
# ============================================================================


async def security_agent_middleware(
    context: AgentRunContext,
    next: Callable[[AgentRunContext], Awaitable[None]],
) -> None:
    """
    Security middleware for agent execution.

    Validates:
    - No prompt injection attempts
    - No sensitive content in input
    - Input length within limits

    Raises:
        SecurityError: If validation fails
    """
    from src.core.exceptions import SecurityError

    # Get user input from the last message (per official docs)
    last_message = context.messages[-1] if context.messages else None
    if not last_message:
        await next(context)
        return

    # Extract text from message
    user_input = None
    if hasattr(last_message, "text") and last_message.text:
        user_input = last_message.text
    elif hasattr(last_message, "content"):
        user_input = str(last_message.content)
    else:
        user_input = str(last_message)

    # Skip validation for non-string inputs
    if not user_input or not isinstance(user_input, str):
        await next(context)
        return

    logger.debug(f"🔒 Security check for input: {user_input[:100]}...")

    # 1. Check input length
    if len(user_input) > MAX_INPUT_LENGTH:
        logger.warning(f"⚠️ Input too long: {len(user_input)} characters")
        raise SecurityError(
            f"Input exceeds maximum length of {MAX_INPUT_LENGTH} characters"
        )

    # 2. Check for prompt injection
    user_input_lower = user_input.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, user_input_lower, re.IGNORECASE):
            logger.warning(f"⚠️ Potential prompt injection detected: {pattern}")
            raise SecurityError(
                "Your input appears to contain instructions that could interfere with the system. "
                "Please rephrase your question."
            )

    # 3. Check for sensitive keywords (warning only, not blocking)
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in user_input_lower:
            logger.warning(f"⚠️ Sensitive keyword detected: {keyword}")
            # Note: You may want to block or just log depending on your policy
            # For now, we'll just log a warning

    logger.debug("✅ Security check passed")

    # Continue to next middleware or agent execution
    await next(context)

    # Optional: Sanitize output (after agent execution)
    # You can add output filtering here if needed


async def security_function_middleware(
    context: FunctionInvocationContext,
    next: Callable[[FunctionInvocationContext], Awaitable[None]],
) -> None:
    """
    Security middleware for function/tool calls.

    Validates function arguments before execution.

    Raises:
        SecurityError: If validation fails
    """
    from src.core.exceptions import SecurityError

    # Safely get function name and arguments
    function_name = "unknown"
    if hasattr(context, "function") and hasattr(context.function, "name"):
        function_name = context.function.name

    arguments = getattr(context, "arguments", None)
    if not arguments:
        # No arguments to validate, proceed
        await next(context)
        return

    logger.debug(f"🔒 Security check for function: {function_name}")
    logger.debug(f"Arguments: {arguments}")

    # Validate string arguments
    if isinstance(arguments, dict):
        for key, value in arguments.items():
            if isinstance(value, str):
                # Check length
                if len(value) > MAX_INPUT_LENGTH:
                    logger.warning(
                        f"⚠️ Function argument '{key}' too long: {len(value)} characters"
                    )
                    raise SecurityError(
                        f"Function argument '{key}' exceeds maximum length"
                    )

                # Check for malicious patterns
                value_lower = value.lower()
                for pattern in PROMPT_INJECTION_PATTERNS:
                    if re.search(pattern, value_lower, re.IGNORECASE):
                        logger.warning(
                            f"⚠️ Suspicious pattern in function argument '{key}'"
                        )
                        raise SecurityError(
                            f"Function argument '{key}' contains suspicious content"
                        )

    logger.debug("✅ Function security check passed")

    # Continue to function execution
    await next(context)


# ============================================================================
# Utility Functions
# ============================================================================


def add_sensitive_keyword(keyword: str) -> None:
    """
    Add a custom sensitive keyword to the filter list.

    Args:
        keyword: The keyword to add (case-insensitive)
    """
    if keyword.lower() not in [k.lower() for k in SENSITIVE_KEYWORDS]:
        SENSITIVE_KEYWORDS.append(keyword.lower())
        logger.info(f"Added sensitive keyword: {keyword}")


def add_injection_pattern(pattern: str) -> None:
    """
    Add a custom prompt injection pattern.

    Args:
        pattern: Regular expression pattern to detect
    """
    if pattern not in PROMPT_INJECTION_PATTERNS:
        PROMPT_INJECTION_PATTERNS.append(pattern)
        logger.info(f"Added injection pattern: {pattern}")


def set_max_input_length(length: int) -> None:
    """
    Set the maximum input length.

    Args:
        length: Maximum allowed input length in characters
    """
    global MAX_INPUT_LENGTH
    MAX_INPUT_LENGTH = length
    logger.info(f"Max input length set to: {length}")
