"""Core LLM hardening components."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional, Dict, Any, List, Mapping
from pydantic import BaseModel, Field, ValidationError
from openai import AsyncOpenAI

log = logging.getLogger(__name__)

class ReportSchema(BaseModel):
    """Structured schema for comprehensive technical analysis reports"""
    title: str = Field(default="", description="Report title starting with **COMPREHENSIVE TECHNICAL ANALYSIS:**")
    market_state: str = Field(default="", description="Current market state and sentiment analysis")
    
    # New comprehensive fields
    trend_indicators: str = Field(default="", description="ADX, Ichimoku, Moving Averages, MACD analysis")
    oscillators: str = Field(default="", description="RSI, Stochastic, Williams %R, CCI analysis")  
    volume_indicators: str = Field(default="", description="OBV, Volume Profile, MFI analysis")
    fibonacci_levels: str = Field(default="", description="Fibonacci retracements and extensions")
    elliott_wave: str = Field(default="", description="Elliott Wave count and pattern analysis")
    smart_money_concepts: str = Field(default="", description="Order blocks, Fair Value Gaps, liquidity analysis")
    trading_setup: str = Field(default="", description="Entry/exit levels with stop-loss and take-profit")
    risk_assessment: str = Field(default="", description="Risk-reward ratios and probability scenarios")
    
    # Legacy fields for backward compatibility (optional)
    timeframe_analysis: str = Field(default="", description="Multi-timeframe technical analysis")
    indicator_analysis: str = Field(default="", description="Advanced indicator analysis")
    trading_levels: str = Field(default="", description="Key trading levels and support/resistance")
    
    outlook: str = Field(default="", description="Final trading bias and market direction")
    
    class Config:
        extra = "forbid"  # Reject any fields not in schema

class CircuitBreaker:
    """Circuit breaker for LLM calls"""
    def __init__(self, failure_threshold: int = 3, reset_timeout: float = 60.0):
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if reset_timeout < 0:
            raise ValueError("reset_timeout must be non-negative")
            
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def can_proceed(self) -> bool:
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time and time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
            
    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
        
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
        elif self.state == "HALF_OPEN":
            self.state = "OPEN"

class ToolCallFirewall:
    """Firewall for controlling tool/function calls"""
    
    ALLOWED_TOOLS = {
        "get_market_data",
        "get_price_data", 
        "calculate_indicators",
        "get_defi_data",
        "get_news_sentiment"
    }
    
    BANNED_TOOLS = {
        "execute_code",
        "run_shell",
        "file_operations",
        "network_requests",
        "database_operations"
    }
    
    @classmethod
    def is_tool_allowed(cls, tool_name: str) -> bool:
        """Check if a tool call is allowed"""
        if tool_name in cls.BANNED_TOOLS:
            log.warning("Blocked banned tool call: %s", tool_name)
            return False
        if tool_name not in cls.ALLOWED_TOOLS:
            log.warning("Blocked unknown tool call: %s", tool_name)
            return False
        return True
    
    @classmethod
    def filter_tool_calls(cls, messages: List[Dict]) -> List[Dict]:
        """Filter out disallowed tool calls from messages"""
        filtered = []
        for msg in messages:
            if msg.get("role") == "assistant" and "tool_calls" in msg:
                allowed_calls = []
                for call in msg["tool_calls"]:
                    if cls.is_tool_allowed(call.get("function", {}).get("name", "")):
                        allowed_calls.append(call)
                    else:
                        log.warning("Filtered out disallowed tool call: %s", call)
                msg["tool_calls"] = allowed_calls
            filtered.append(msg)
        return filtered

# Simplified post-processing functions (standalone version)
def finalize_text(raw_text: str) -> str:
    """Simplified text finalization for package distribution"""
    if not raw_text:
        return ""
    
    # Basic meta commentary removal
    banned_patterns = [
        r"(?im)^.*?(?:I'll|I will|The key will be|The challenge is|Let me|I notice).*$",
        r"(?is)<think>.*?</think>",
        r"(?is)```think.*?```"
    ]
    
    text = raw_text
    for pattern in banned_patterns:
        text = re.sub(pattern, "", text)
    
    # Find first proper header
    lines = text.split('\n')
    start_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("**") and "ANALYSIS" in line.upper():
            start_idx = i
            break
    
    cleaned_lines = []
    for line in lines[start_idx:]:
        stripped = line.strip()
        if stripped:
            cleaned_lines.append(line.rstrip())
        elif cleaned_lines:  # Preserve empty lines only if we have content
            cleaned_lines.append("")
    
    result = '\n'.join(cleaned_lines).strip()
    return result if result else raw_text.strip()

class LLMCore:
    """Core LLM interface with all production hardening"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.fireworks.ai/inference/v1"):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.circuit_breaker = CircuitBreaker()
        self.firewall = ToolCallFirewall()
        
    async def complete_structured(
        self,
        messages: List[Dict[str, str]],
        model: str = "accounts/fireworks/models/llama-v3p1-70b-instruct",
        temperature: float = 0.3,
        timeout: float = 30.0,
        max_retries: int = 3,
        enforce_schema: bool = True,
        verbose: bool = False
    ) -> tuple[Optional[ReportSchema], Optional[str]]:
        """
        Structured completion with enforced schema validation
        Returns (parsed_report, raw_text) or (None, error_msg)
        """
        
        if not self.circuit_breaker.can_proceed():
            log.error("Circuit breaker OPEN - rejecting request")
            return None, "Circuit breaker active - too many recent failures"
        
        # Apply tool call firewall
        filtered_messages = self.firewall.filter_tool_calls(messages)
        
        # Enhanced system prompt for structured output
        base_prompt = """You are a crypto market analyst. Your response MUST follow this exact JSON structure:
{
  "title": "**MARKET ANALYSIS: [SYMBOL]** or **COMPREHENSIVE TECHNICAL ANALYSIS: [SYMBOL]**",
  "market_state": "Current market conditions and overall state",
  "timeframe_analysis": "Multi-timeframe technical analysis", 
  "indicator_analysis": "Advanced indicator analysis (RSI, MACD, etc.)",
  "trading_levels": "Key support/resistance levels and trading ranges",
  "outlook": "Concise outlook with strategic bias"
}

CRITICAL RULES:
1. Response MUST be valid JSON only - no markdown, no preamble, no meta commentary
2. Never start with "The key will be", "I'll", "The challenge is", "<think>" or any meta text
3. Title MUST start with **MARKET ANALYSIS:** or **COMPREHENSIVE TECHNICAL ANALYSIS:**
4. Each field must contain substantial analysis (minimum 20 words)
5. Do not include any text outside the JSON structure"""
        
        if verbose:
            base_prompt += """

VERBOSE MODE REQUIREMENTS:
- Fill ALL sections if data exists. If a section has no signal, write exactly: "No data"
- Include comprehensive analysis for ALL available indicators: RSI, Stochastic, MACD, ADX/DI, CCI, Williams %R, OBV, VWAP, ATR, SMA/EMA, Ichimoku, Fibonacci, Elliott Wave, SMC, Volume Profile
- Use concise, factual analysis; avoid meta commentary
- Do not omit any computed technical indicators"""
        
        system_prompt = base_prompt

        # Insert enhanced system prompt
        enhanced_messages = [
            {"role": "system", "content": system_prompt}
        ] + filtered_messages

        last_error = None
        
        for attempt in range(max_retries):
            try:
                log.info("LLM structured call attempt %d/%d", attempt + 1, max_retries)
                
                # Make the API call with timeout
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=model,
                        messages=enhanced_messages,
                        temperature=temperature,
                        stop=["</think>", "<think>", "```think", "Internal:", "Plan:", "The key will be", "I'll ", "I will "],
                        max_tokens=2000
                    ),
                    timeout=timeout
                )
                
                raw_content = response.choices[0].message.content
                log.debug("Raw LLM response: %s", raw_content[:200])
                
                if not raw_content:
                    raise ValueError("Empty response from LLM")
                
                # Try to parse as JSON first
                try:
                    parsed_json = json.loads(raw_content.strip())
                    report = ReportSchema(**parsed_json)
                    
                    # Additional validation: ensure title starts properly
                    title_upper = report.title.upper()
                    if not (title_upper.startswith("**MARKET ANALYSIS:") or title_upper.startswith("**COMPREHENSIVE TECHNICAL ANALYSIS:")):
                        raise ValidationError("Title must start with proper header", ReportSchema)
                    
                    log.info("Successfully parsed structured response")
                    self.circuit_breaker.record_success()
                    return report, raw_content
                    
                except (json.JSONDecodeError, ValidationError) as e:
                    if enforce_schema:
                        log.warning("Schema validation failed (attempt %d): %s", attempt + 1, str(e))
                        last_error = f"Schema validation failed: {str(e)}"
                        continue
                    else:
                        # Fallback: use postprocessing on free-text response
                        log.info("Schema enforcement disabled, falling back to post-processing")
                        cleaned = finalize_text(raw_content)
                        
                        # Try to construct ReportSchema from cleaned text
                        try:
                            constructed = self._construct_from_freetext(cleaned)
                            self.circuit_breaker.record_success()
                            return constructed, raw_content
                        except Exception as construct_error:
                            log.error("Failed to construct schema from free text: %s", str(construct_error))
                            last_error = f"Schema construction failed: {str(construct_error)}"
                            
            except asyncio.TimeoutError:
                last_error = f"Timeout after {timeout}s on attempt {attempt + 1}"
                log.warning(last_error)
                
            except Exception as e:
                last_error = f"API error on attempt {attempt + 1}: {str(e)}"
                log.error(last_error)
                
            # Exponential backoff between retries
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 0.5
                log.info("Retrying in %.1fs...", wait_time)
                await asyncio.sleep(wait_time)
        
        # All retries failed
        self.circuit_breaker.record_failure()
        log.error("All LLM attempts failed. Last error: %s", last_error)
        return None, last_error or "All retry attempts failed"
    
    def _construct_from_freetext(self, cleaned_text: str) -> ReportSchema:
        """Attempt to construct ReportSchema from cleaned free-text"""
        lines = cleaned_text.strip().split('\n')
        
        # Extract title (first line that starts with **...** or ###)
        title = ""
        for line in lines:
            if line.strip().startswith("**") and "ANALYSIS" in line.upper():
                title = line.strip()
                break
            elif line.strip().startswith("###") and "ANALYSIS" in line.upper():
                title = line.strip()
                break
        
        if not title:
            raise ValueError("No valid title found in free text")
        
        # Extract sections based on headers
        sections = {
            "market_state": "",
            "timeframe_analysis": "",
            "indicator_analysis": "",
            "trading_levels": "",
            "outlook": ""
        }
        
        current_section = None
        current_content = []
        
        for line in lines[1:]:  # Skip title line
            line = line.strip()
            if not line:
                if current_content:
                    current_content.append("")
                continue
                
            # Check if this is a section header
            upper_line = line.upper()
            if "MARKET STATE" in upper_line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = "market_state"
                current_content = []
            elif "TIMEFRAME" in upper_line or "MULTI-TIMEFRAME" in upper_line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = "timeframe_analysis"
                current_content = []
            elif "INDICATOR" in upper_line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = "indicator_analysis"
                current_content = []
            elif "TRADING LEVELS" in upper_line or "KEY LEVELS" in upper_line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = "trading_levels"
                current_content = []
            elif "OUTLOOK" in upper_line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = "outlook"
                current_content = []
            else:
                # This is content for the current section
                if current_section:
                    current_content.append(line)
        
        # Don't forget the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Fill empty sections with fallbacks
        for key in sections:
            if not sections[key]:
                sections[key] = f"Analysis pending for {key.replace('_', ' ')}"
        
        return ReportSchema(
            title=title,
            market_state=sections["market_state"],
            timeframe_analysis=sections["timeframe_analysis"],
            indicator_analysis=sections["indicator_analysis"],
            trading_levels=sections["trading_levels"],
            outlook=sections["outlook"]
        )
    
    async def complete_with_fallback(
        self,
        messages: List[Dict[str, str]],
        verbose: bool = False,
        **kwargs
    ) -> str:
        """
        Complete with structured enforcement and fallback to post-processing
        Returns clean text output
        """
        
        # Try structured first
        report, error = await self.complete_structured(
            messages, 
            enforce_schema=True,
            verbose=verbose,
            **kwargs
        )
        
        if report:
            # Convert structured report back to formatted text
            output = f"{report.title}\n\n"
            output += f"### INITIAL OVERALL MARKET STATE\n{report.market_state}\n\n"
            output += f"### MULTI-TIMEFRAME ANALYSIS\n{report.timeframe_analysis}\n\n"
            output += f"### ADVANCED INDICATOR ANALYSIS\n{report.indicator_analysis}\n\n"
            output += f"### KEY TRADING LEVELS\n{report.trading_levels}\n\n"
            output += f"### CONCISE OUTLOOK\n{report.outlook}"
            return output
        
        # Fallback to non-enforced with post-processing
        log.warning("Structured enforcement failed, using fallback: %s", error)
        report, error = await self.complete_structured(
            messages,
            enforce_schema=False,
            verbose=verbose,
            **kwargs
        )
        
        if report:
            output = f"{report.title}\n\n"
            output += f"### INITIAL OVERALL MARKET STATE\n{report.market_state}\n\n"
            output += f"### MULTI-TIMEFRAME ANALYSIS\n{report.timeframe_analysis}\n\n"
            output += f"### ADVANCED INDICATOR ANALYSIS\n{report.indicator_analysis}\n\n"
            output += f"### KEY TRADING LEVELS\n{report.trading_levels}\n\n"
            output += f"### CONCISE OUTLOOK\n{report.outlook}"
            return output
        
        # Last resort: return error message
        return f"**ANALYSIS UNAVAILABLE**\n\nSystem Error: {error or 'Unable to generate analysis'}"

__all__ = ["LLMCore", "ReportSchema", "CircuitBreaker", "ToolCallFirewall"]