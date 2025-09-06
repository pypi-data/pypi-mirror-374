"""
Data models for AdsonAI SDK - Version 2.0
Includes enhanced models with matching metadata and context handling
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class ContentType(Enum):
    """Content type for different consumption modes"""
    ADS_ONLY = "ads_only"
    CONVERSATIONS = "conversations" 
    MIXED = "mixed"


class IntentType(Enum):
    """User intent classifications"""
    HIGH_INTENT = "HIGH_INTENT"
    RESEARCH_INTENT = "RESEARCH_INTENT"
    CASUAL_MENTION = "CASUAL_MENTION"
    NEGATIVE_INTENT = "NEGATIVE_INTENT"


@dataclass
class MatchingContext:
    """
    Enhanced context for ad matching with detailed personalization options
    """
    # Core matching settings
    content_type: ContentType = ContentType.MIXED
    
    # User context
    user_location: Optional[str] = None
    user_demographics: Optional[Dict[str, Any]] = None
    
    # Conversation context
    conversation_history: Optional[List[str]] = None
    session_id: Optional[str] = None
    
    # Advanced matching controls
    intent_override: Optional[IntentType] = None
    semantic_boost: float = 1.0
    bid_weight: float = 1.0
    recency_preference: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests"""
        return {
            "content_type": self.content_type.value,
            "user_location": self.user_location,
            "user_demographics": self.user_demographics,
            "conversation_history": self.conversation_history,
            "session_id": self.session_id,
            "intent_override": self.intent_override.value if self.intent_override else None,
            "semantic_boost": self.semantic_boost,
            "bid_weight": self.bid_weight,
            "recency_preference": self.recency_preference
        }


@dataclass 
class Ad:
    """
    Enhanced ad object with detailed matching metadata
    """
    # Core ad information
    id: str
    brand_name: str
    product_name: str
    description: str
    ad_text: str
    bid_amount: float
    landing_url: Optional[str]
    target_keywords: str
    status: str
    
    # Enhanced matching metadata (new in v2.0)
    relevance_score: float = 0.0
    intent_score: float = 0.0
    semantic_score: float = 0.0
    entity_match_score: float = 0.0
    sentiment_alignment: float = 0.5
    confidence_level: float = 0.0
    
    # Additional metadata (optional)
    category: Optional[str] = None
    rating: Optional[float] = None
    conversion_rate: Optional[float] = None
    historical_ctr: Optional[float] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        """Validate and process ad data after initialization"""
        # Ensure scores are within valid ranges
        self.relevance_score = max(0.0, min(1.0, self.relevance_score))
        self.intent_score = max(0.0, min(1.0, self.intent_score))
        self.semantic_score = max(0.0, min(1.0, self.semantic_score))
        self.entity_match_score = max(0.0, min(1.0, self.entity_match_score))
        self.sentiment_alignment = max(0.0, min(1.0, self.sentiment_alignment))
        self.confidence_level = max(0.0, min(1.0, self.confidence_level))
        
        # Ensure bid_amount is positive
        self.bid_amount = max(0.0, self.bid_amount)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            # Core ad data
            "id": self.id,
            "brand_name": self.brand_name,
            "product_name": self.product_name, 
            "description": self.description,
            "ad_text": self.ad_text,
            "bid_amount": self.bid_amount,
            "landing_url": self.landing_url,
            "target_keywords": self.target_keywords,
            "status": self.status,
            
            # Enhanced metadata
            "matching_metadata": {
                "relevance_score": self.relevance_score,
                "intent_score": self.intent_score,
                "semantic_score": self.semantic_score,
                "entity_match_score": self.entity_match_score,
                "sentiment_alignment": self.sentiment_alignment,
                "confidence_level": self.confidence_level
            },
            
            # Optional fields
            "category": self.category,
            "rating": self.rating,
            "conversion_rate": self.conversion_rate,
            "historical_ctr": self.historical_ctr,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ad':
        """Create Ad instance from dictionary"""
        metadata = data.get('matching_metadata', {})
        
        return cls(
            # Core fields
            id=data.get('id', ''),
            brand_name=data.get('brand_name', ''),
            product_name=data.get('product_name', ''),
            description=data.get('description', ''),
            ad_text=data.get('ad_text', ''),
            bid_amount=float(data.get('bid_amount', 0)),
            landing_url=data.get('landing_url'),
            target_keywords=data.get('target_keywords', ''),
            status=data.get('status', 'active'),
            
            # Enhanced metadata
            relevance_score=metadata.get('relevance_score', 0.0),
            intent_score=metadata.get('intent_score', 0.0),
            semantic_score=metadata.get('semantic_score', 0.0),
            entity_match_score=metadata.get('entity_match_score', 0.0),
            sentiment_alignment=metadata.get('sentiment_alignment', 0.5),
            confidence_level=metadata.get('confidence_level', 0.0),
            
            # Optional fields
            category=data.get('category'),
            rating=data.get('rating'),
            conversion_rate=data.get('conversion_rate'),
            historical_ctr=data.get('historical_ctr'),
            created_at=data.get('created_at')
        )
    
    def get_display_text(self, format_type: str = "standard") -> str:
        """Get formatted display text for different contexts"""
        if format_type == "conversational":
            return f"💡 {self.brand_name}: {self.ad_text}"
        elif format_type == "sponsored":
            return f"Sponsored: {self.product_name} - {self.ad_text}"
        elif format_type == "inline":
            return f"*{self.brand_name}* - {self.ad_text}"
        else:  # standard
            return f"{self.brand_name} - {self.product_name}: {self.ad_text}"
    
    def is_high_quality(self, threshold: float = 0.7) -> bool:
        """Check if ad meets high quality thresholds"""
        return (
            self.relevance_score >= threshold and
            self.confidence_level >= threshold and
            self.bid_amount >= 1.0
        )
    
    def get_performance_score(self) -> float:
        """Calculate overall performance score"""
        weights = {
            'relevance': 0.3,
            'confidence': 0.2,
            'intent': 0.2,
            'semantic': 0.15,
            'sentiment': 0.1,
            'entity': 0.05
        }
        
        return (
            self.relevance_score * weights['relevance'] +
            self.confidence_level * weights['confidence'] +
            self.intent_score * weights['intent'] +
            self.semantic_score * weights['semantic'] +
            self.sentiment_alignment * weights['sentiment'] +
            self.entity_match_score * weights['entity']
        )


# Legacy support - alias for backward compatibility
class AdMatch(Ad):
    """Legacy alias for Ad class - for backward compatibility"""
    pass


@dataclass
class ApiResponse:
    """
    Response wrapper for API calls
    """
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    request_id: Optional[str] = None
    processing_time_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UsageStats:
    """
    Usage statistics for API key
    """
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_hits: int = 0
    avg_response_time_ms: float = 0.0
    last_used: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate"""
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests


# Export all models
__all__ = [
    'Ad', 'AdMatch',  # AdMatch for backward compatibility
    'MatchingContext', 
    'ContentType', 
    'IntentType',
    'ApiResponse',
    'UsageStats'
]