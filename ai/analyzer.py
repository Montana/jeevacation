import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import anthropic

logger = logging.getLogger(__name__)


@dataclass
class ContextAnalysis:
    category: str
    sentiment: str
    summary: str
    confidence: float
    key_facts: List[str]


class AIAnalyzer:
    
    CATEGORIES = [
        "witness",
        "victim",
        "employee",
        "business_associate",
        "legal_professional",
        "family_friend",
        "incidental_mention",
        "other"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("No Anthropic API key provided. AI analysis will be disabled.")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def analyze_mentions(
        self,
        name: str,
        excerpts: List[str],
        position: Optional[str] = None,
        company: Optional[str] = None
    ) -> Optional[ContextAnalysis]:
        if not self.client:
            return None
        
        try:
            combined_text = "\n\n---\n\n".join(excerpts[:10])
            
            context_parts = [f"Name: {name}"]
            if position:
                context_parts.append(f"Position: {position}")
            if company:
                context_parts.append(f"Company: {company}")
            context = "\n".join(context_parts)
            
            prompt = f"""You are analyzing mentions of a person in the Jeffrey Epstein court documents.

Person Information:
{context}

Document Excerpts:
{combined_text}

Please analyze how this person is mentioned and provide:

1. Category (choose one): {', '.join(self.CATEGORIES)}
2. Sentiment (neutral/concerning/benign): Based on whether the mentions suggest potential wrongdoing
3. A brief 2-3 sentence summary of how the person is mentioned
4. Your confidence level (0.0-1.0) in this analysis
5. Key facts extracted from the mentions

Important: A mention does not imply wrongdoing. Many people are mentioned as witnesses, employees, or in other neutral contexts.

Respond in this exact format:
CATEGORY: [category]
SENTIMENT: [sentiment]
CONFIDENCE: [0.0-1.0]
SUMMARY: [your summary]
KEY_FACTS:
- [fact 1]
- [fact 2]
- [fact 3]
        lines = response.strip().split('\n')
        
        category = "other"
        sentiment = "neutral"
        confidence = 0.5
        summary = ""
        key_facts = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("CATEGORY:"):
                category = line.split(":", 1)[1].strip().lower()
            elif line.startswith("SENTIMENT:"):
                sentiment = line.split(":", 1)[1].strip().lower()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    confidence = 0.5
            elif line.startswith("SUMMARY:"):
                summary = line.split(":", 1)[1].strip()
                current_section = "summary"
            elif line.startswith("KEY_FACTS:"):
                current_section = "facts"
            elif line.startswith("-") and current_section == "facts":
                fact = line.lstrip("- ").strip()
                if fact:
                    key_facts.append(fact)
            elif current_section == "summary" and line and not line.startswith(("CATEGORY", "SENTIMENT", "CONFIDENCE", "KEY_FACTS")):
                summary += " " + line
        
        return ContextAnalysis(
            category=category,
            sentiment=sentiment,
            summary=summary.strip(),
            confidence=confidence,
            key_facts=key_facts
        )
    
    def calculate_false_positive_score(
        self,
        name: str,
        excerpts: List[str],
        position: Optional[str] = None,
        company: Optional[str] = None
    ) -> float:
        score = 0.0
        
        common_first = ['john', 'james', 'michael', 'david', 'robert', 'mary', 'patricia', 'jennifer']
        common_last = ['smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis']
        
        name_parts = name.lower().split()
        if len(name_parts) >= 2:
            if name_parts[0] in common_first:
                score += 0.3
            if name_parts[-1] in common_last:
                score += 0.3
        
        if len(excerpts) == 1:
            score += 0.2
        
        avg_excerpt_length = sum(len(e) for e in excerpts) / len(excerpts) if excerpts else 0
        if avg_excerpt_length < 100:
            score += 0.2
        
        if position or company:
            score -= 0.3
        
        return min(1.0, max(0.0, score))
