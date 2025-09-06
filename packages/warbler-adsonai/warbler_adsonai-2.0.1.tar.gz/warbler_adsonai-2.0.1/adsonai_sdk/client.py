"""
AdsonAI Python SDK Client - Updated Version 2.1
Main client for AdsonAI SDK with separate consumption modes and enhanced matching
Now includes conversational context + styled ads functionality
"""

import requests
import json
import logging
import time
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from .models import Ad, MatchingContext, ContentType, IntentType
from .exceptions import AdsonAIError, AuthenticationError, APIError, ValidationError, NetworkError

# Configure logging
logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://adsonai.vercel.app"
DEFAULT_TIMEOUT = 30

@dataclass
class ConversationContext:
    """Contains the AI response context and formatting hints"""
    response_text: str
    user_query: str
    context_type: str = "conversational"
    conversation_stage: str = "consideration"
    intent_confidence: float = 0.0
    suggested_placement: str = "inline"  # inline, sidebar, footer
    integration_style: str = "natural"   # natural, highlighted, separated

@dataclass
class AdDisplay:
    """Contains styling and display information for ads"""
    style: str = "conversational"  # conversational, banner, card, minimal
    background_color: str = "#f8fafc"  # Light gray-blue background
    border_color: str = "#e2e8f0"      # Light gray border
    text_color: str = "#334155"        # Dark gray text
    accent_color: str = "#3b82f6"      # Blue accent
    max_width: str = "400px"
    border_radius: str = "8px"
    padding: str = "12px"
    margin: str = "8px 0"
    separator_line: bool = True
    show_brand_icon: bool = True
    show_ad_label: bool = True
    ad_label_text: str = "Sponsored"

@dataclass
class ConversationalResult:
    """Enhanced result containing context + styled ads"""
    context: ConversationContext
    ads: List[Ad]
    ad_display: AdDisplay
    total_ads_found: int
    matching_confidence: float
    suggestions: List[str]  # Suggestions for better integration

    def __str__(self):
        return f"ConversationalResult: {len(self.ads)} ads, {self.matching_confidence:.1%} confidence"


class AdsonAI:
    """
    AdsonAI Python SDK Client v2.1
    
    Features:
    - Separate ad and conversation consumption
    - Enhanced matching algorithm integration
    - Advanced context and intent handling
    - Detailed matching metadata
    - Caching and performance optimization
    - NEW: Conversational context + styled ads
    - Full backward compatibility with v1.0
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = DEFAULT_BASE_URL, 
        timeout: int = DEFAULT_TIMEOUT,
        enable_caching: bool = True,
        cache_ttl: int = 300  # 5 minutes
    ):
        """
        Initialize AdsonAI client
        
        Args:
            api_key: Your AdsonAI API key
            base_url: API base URL
            timeout: Request timeout in seconds
            enable_caching: Whether to cache responses
            cache_ttl: Cache time-to-live in seconds
        """
        if not api_key or not api_key.startswith('adsonai_'):
            raise ValueError("Invalid API key format. Key should start with 'adsonai_'")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self._cache = {} if enable_caching else None
        
        # Enhanced session configuration
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'AdsonAI-Python-SDK/2.1.0',
            'Accept': 'application/json'
        })
        
        logger.info(f"AdsonAI SDK v2.1 initialized")

    def get_ads_only(
        self, 
        query: str, 
        max_ads: int = 3,
        context: Optional[MatchingContext] = None,
        filters: Optional[Dict] = None
    ) -> List[Ad]:
        """
        Get ads only - optimized for pure advertising scenarios
        
        Args:
            query: Search query or context
            max_ads: Maximum number of ads to return
            context: Enhanced matching context
            filters: Additional filters (category, budget, etc.)
            
        Returns:
            List of matched ads with detailed metadata
        """
        if context is None:
            context = MatchingContext(content_type=ContentType.ADS_ONLY)
        else:
            context.content_type = ContentType.ADS_ONLY
            
        return self._get_contextual_ads_enhanced(
            query=query,
            max_ads=max_ads,
            context=context,
            filters=filters
        )
    
    def get_conversational_ads(
        self,
        conversation: Union[str, List[str]],
        max_ads: int = 1,
        context: Optional[MatchingContext] = None,
        conversation_context: Optional[Dict] = None,
        return_enhanced: bool = True
    ) -> Union[List[Ad], ConversationalResult]:
        """
        ENHANCED: Get ads for conversational interfaces with context + styling
        
        Args:
            conversation: Single message or list of conversation history
            max_ads: Maximum ads (usually 1 for conversations)
            context: Enhanced matching context
            conversation_context: Additional conversation metadata
            return_enhanced: If True, returns ConversationalResult with context + styling
            
        Returns:
            ConversationalResult (enhanced) or List[Ad] (legacy)
        """
        if context is None:
            context = MatchingContext(content_type=ContentType.CONVERSATIONS)
        else:
            context.content_type = ContentType.CONVERSATIONS
            
        # Process conversation history
        if isinstance(conversation, list):
            query = conversation[-1]  # Latest message
            context.conversation_history = conversation[:-1]
        else:
            query = conversation
            
        # Add conversation-specific context
        if conversation_context:
            context.user_location = conversation_context.get('location')
            context.session_id = conversation_context.get('session_id')
            context.user_demographics = conversation_context.get('demographics')
        
        # Get ads using enhanced method
        ads = self._get_contextual_ads_enhanced(
            query=query,
            max_ads=max_ads,
            context=context,
            optimize_for_conversation=True
        )
        
        # Return enhanced result or legacy format
        if return_enhanced:
            return self._create_conversational_result(query, ads, context)
        else:
            return ads  # Legacy format for backward compatibility
    
    def get_mixed_content(
        self,
        query: str,
        max_ads: int = 3,
        context: Optional[MatchingContext] = None,
        content_preferences: Optional[Dict] = None
    ) -> List[Ad]:
        """
        Get mixed ad and content recommendations
        
        Args:
            query: Search query
            max_ads: Maximum ads to return
            context: Enhanced matching context
            content_preferences: User content preferences
            
        Returns:
            List of ads optimized for mixed content scenarios
        """
        if context is None:
            context = MatchingContext(content_type=ContentType.MIXED)
        else:
            context.content_type = ContentType.MIXED
            
        return self._get_contextual_ads_enhanced(
            query=query,
            max_ads=max_ads,
            context=context,
            content_preferences=content_preferences
        )
    
    def _create_conversational_result(
        self, 
        user_query: str, 
        ads: List[Ad], 
        context: MatchingContext
    ) -> ConversationalResult:
        """Create enhanced conversational result with context + styling"""
        
        # Generate AI response context
        conversation_context = ConversationContext(
            response_text=self._generate_ai_response(user_query, ads),
            user_query=user_query,
            context_type="conversational",
            conversation_stage=self._determine_conversation_stage(user_query, ads),
            intent_confidence=self._calculate_intent_confidence(ads),
            suggested_placement=self._determine_ad_placement(user_query, ads),
            integration_style="natural"
        )
        
        # Create ad display styling
        ad_display = AdDisplay(
            style="conversational",
            background_color="#f8fafc",  # Very light gray-blue
            border_color="#e2e8f0",     # Light gray border
            text_color="#334155",       # Dark gray text
            accent_color="#3b82f6",     # Blue accent
            separator_line=True,
            show_brand_icon=True,
            show_ad_label=True,
            ad_label_text="Sponsored"
        )
        
        # Generate integration suggestions
        suggestions = self._generate_integration_suggestions(user_query, ads, conversation_context)
        
        # Calculate overall confidence
        avg_confidence = sum(ad.confidence_level for ad in ads) / len(ads) if ads else 0.0
        
        return ConversationalResult(
            context=conversation_context,
            ads=ads,
            ad_display=ad_display,
            total_ads_found=len(ads),
            matching_confidence=avg_confidence,
            suggestions=suggestions
        )
    
    def _generate_ai_response(self, user_query: str, ads: List[Ad]) -> str:
        """Generate contextual AI response that naturally incorporates ads"""
        if not ads:
            return f"I understand you're looking for information about '{user_query}'. Let me help you with that."
        
        # Create natural response based on user intent
        query_lower = user_query.lower()
        
        if any(keyword in query_lower for keyword in ["running", "shoes", "marathon", "training"]):
            return "Great choice! Running shoes are essential for comfort and performance. Here are some excellent options I'd recommend:"
        elif any(keyword in query_lower for keyword in ["laptop", "computer", "programming", "development"]):
            return "Finding the right laptop depends on your specific needs. Here are some top-rated options:"
        elif any(keyword in query_lower for keyword in ["crm", "customer", "management", "sales"]):
            return "Customer relationship management is crucial for business growth. Here are some powerful solutions:"
        elif any(keyword in query_lower for keyword in ["headphones", "audio", "music"]):
            return "Good audio quality makes a huge difference! Here are some highly-rated options:"
        elif any(keyword in query_lower for keyword in ["camera", "photography", "video"]):
            return "Photography equipment can really enhance your creative work. Here are some excellent choices:"
        else:
            return f"I can help you find what you're looking for regarding '{user_query}'. Here are some highly-rated options:"
    
    def _determine_conversation_stage(self, user_query: str, ads: List[Ad]) -> str:
        """Determine conversation stage based on query and ad relevance"""
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ["buy", "purchase", "order", "get", "need now"]):
            return "decision"
        elif any(word in query_lower for word in ["compare", "vs", "difference", "better"]):
            return "consideration"
        elif any(word in query_lower for word in ["learn", "understand", "what is", "how does"]):
            return "awareness"
        else:
            return "consideration"  # Default
    
    def _calculate_intent_confidence(self, ads: List[Ad]) -> float:
        """Calculate intent confidence based on ad scores"""
        if not ads:
            return 0.0
        
        avg_relevance = sum(ad.relevance_score for ad in ads) / len(ads)
        avg_intent = sum(ad.intent_score for ad in ads) / len(ads)
        
        return (avg_relevance + avg_intent) / 2
    
    def _determine_ad_placement(self, user_query: str, ads: List[Ad]) -> str:
        """Determine optimal ad placement in conversation"""
        if len(ads) == 1:
            return "inline"  # Single ad works well inline
        elif len(ads) > 2:
            return "sidebar"  # Multiple ads better in sidebar
        else:
            return "footer"   # Two ads work well at the end
    
    def _generate_integration_suggestions(
        self, 
        user_query: str, 
        ads: List[Ad], 
        context: ConversationContext
    ) -> List[str]:
        """Generate suggestions for optimal ad integration"""
        suggestions = []
        
        if context.intent_confidence > 0.8:
            suggestions.append("High intent detected - consider showing ads prominently")
        elif context.intent_confidence < 0.3:
            suggestions.append("Low intent - use subtle ad placement")
        
        if len(ads) == 1:
            suggestions.append("Single ad integration - use natural language mention")
        elif len(ads) > 1:
            suggestions.append("Multiple ads - consider comparison format or list presentation")
        
        # Check for premium brands
        premium_brands = ["nike", "apple", "microsoft", "adobe", "tesla"]
        if any(brand.lower() in ad.brand_name.lower() for ad in ads for brand in premium_brands):
            suggestions.append("Premium brand detected - emphasize quality and trust signals")
        
        if context.conversation_stage == "decision":
            suggestions.append("User ready to purchase - include strong call-to-action")
        elif context.conversation_stage == "awareness":
            suggestions.append("Educational stage - focus on informative content")
        
        suggestions.append("Use conversational tone to maintain chat flow")
        suggestions.append("Include clear call-to-action but keep it natural")
        
        return suggestions
    
    def format_conversational_display(self, result: ConversationalResult) -> str:
        """Format the complete conversational response with styled ads"""
        output = []
        
        # Add the AI response context
        output.append("🤖 AI Assistant:")
        output.append(result.context.response_text)
        output.append("")
        
        # Add styled ads section
        if result.ads:
            output.append("📢 Sponsored Recommendations:")
            output.append("=" * 50)
            
            for i, ad in enumerate(result.ads, 1):
                output.append(f"\n🏷️  {ad.brand_name} | {result.ad_display.ad_label_text}")
                output.append(f"📦 {ad.product_name}")
                output.append(f"💬 {ad.ad_text}")
                if ad.landing_url:
                    output.append(f"🔗 Learn more: {ad.landing_url}")
                output.append(f"⭐ Relevance: {ad.relevance_score:.1%}")
                
                if i < len(result.ads):
                    output.append("-" * 30)
        
        # Add integration suggestions
        if result.suggestions:
            output.append("\n💡 Integration Tips:")
            for suggestion in result.suggestions:
                output.append(f"  • {suggestion}")
        
        return "\n".join(output)
    
    # Legacy method for backward compatibility
    def get_contextual_ads(self, query: str, max_ads: int = 3, context: dict = None) -> List[Ad]:
        """
        Legacy method for backward compatibility with v1.0
        
        Args:
            query: User query or conversation context
            max_ads: Maximum ads to return (1-10)
            context: Additional context for matching (dict format)
            
        Returns:
            List of matched ads
        """
        # Convert legacy context to new MatchingContext
        matching_context = None
        if context:
            matching_context = MatchingContext(
                user_location=context.get('user_location'),
                user_demographics=context.get('user_demographics')
            )
        
        return self._get_contextual_ads_enhanced(
            query=query,
            max_ads=max_ads,
            context=matching_context
        )
    
    def _get_contextual_ads_enhanced(
        self, 
        query: str, 
        max_ads: int = 3, 
        context: Optional[MatchingContext] = None,
        filters: Optional[Dict] = None,
        optimize_for_conversation: bool = False,
        content_preferences: Optional[Dict] = None
    ) -> List[Ad]:
        """
        Enhanced internal method for getting contextual ads
        """
        # Input validation
        if not query.strip():
            raise ValidationError("Query cannot be empty")
        if not 1 <= max_ads <= 10:
            raise ValidationError("max_ads must be between 1 and 10")
            
        # Check cache
        cache_key = self._generate_cache_key(query, max_ads, context, filters)
        if self._cache and cache_key in self._cache:
            cached_result = self._cache[cache_key]
            if time.time() - cached_result['timestamp'] < self.cache_ttl:
                logger.info(f"Cache hit for query: '{query[:50]}'")
                return cached_result['data']
        
        # Prepare enhanced request payload
        payload = {
            "query": query,
            "max_ads": max_ads,
            "enhanced_matching": True,
            "context": {
                "content_type": context.content_type.value if context else "mixed",
                "user_location": context.user_location if context else None,
                "user_demographics": context.user_demographics if context else None,
                "conversation_history": context.conversation_history if context else None,
                "session_id": context.session_id if context else None,
                "intent_override": context.intent_override.value if context and context.intent_override else None,
                "semantic_boost": context.semantic_boost if context else 1.0,
                "bid_weight": context.bid_weight if context else 1.0,
                "recency_preference": context.recency_preference if context else False,
                "optimize_for_conversation": optimize_for_conversation,
                "filters": filters or {},
                "content_preferences": content_preferences or {}
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/match-ads",
                json=payload,
                timeout=self.timeout
            )
            
            # Handle errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise APIError("Rate limit exceeded", status_code=429)
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Bad request')
                except:
                    error_msg = 'Bad request'
                raise ValidationError(f"Validation error: {error_msg}")
            elif response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    pass
                raise APIError(error_msg, status_code=response.status_code)
            
            # Parse response
            result = response.json()
            if not result.get('success'):
                raise APIError(result.get('error', 'API returned unsuccessful response'))
            
            # Convert to enhanced ad objects
            ads_data = result.get('data', {}).get('matches', [])
            ads = []
            
            for ad_data in ads_data:
                # Extract matching metadata if available
                metadata = ad_data.get('matching_metadata', {})
                
                ad = Ad(
                    id=ad_data.get('id', ''),
                    brand_name=ad_data.get('brandName', ''),
                    product_name=ad_data.get('productName', ''),
                    description=ad_data.get('description', ''),
                    ad_text=ad_data.get('adText', ''),
                    bid_amount=float(ad_data.get('bidAmount', 0)),
                    landing_url=ad_data.get('landingUrl'),
                    target_keywords=ad_data.get('targetKeywords', ''),
                    status=ad_data.get('status', 'active'),
                    relevance_score=metadata.get('relevance_score', 0.0),
                    intent_score=metadata.get('intent_score', 0.0),
                    semantic_score=metadata.get('semantic_score', 0.0),
                    entity_match_score=metadata.get('entity_match_score', 0.0),
                    sentiment_alignment=metadata.get('sentiment_alignment', 0.5),
                    confidence_level=metadata.get('confidence_level', 0.0)
                )
                ads.append(ad)
            
            # Cache results
            if self._cache:
                self._cache[cache_key] = {
                    'data': ads,
                    'timestamp': time.time()
                }
            
            logger.info(f"Retrieved {len(ads)} ads for query: '{query[:50]}'")
            return ads
            
        except requests.exceptions.Timeout:
            raise NetworkError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Failed to connect to AdsonAI API")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {e}")
    
    def _generate_cache_key(
        self, 
        query: str, 
        max_ads: int, 
        context: Optional[MatchingContext], 
        filters: Optional[Dict]
    ) -> str:
        """Generate cache key for request"""
        import hashlib
        
        cache_data = {
            'query': query,
            'max_ads': max_ads,
            'context': context.__dict__ if context else None,
            'filters': filters
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True, default=str)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear the response cache"""
        if self._cache:
            self._cache.clear()
            logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        if not self._cache:
            return {"caching": "disabled"}
            
        return {
            "caching": "enabled",
            "cache_size": len(self._cache),
            "cache_ttl": self.cache_ttl
        }
    
    def test_connection(self) -> bool:
        """Test connection to AdsonAI API"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def close(self):
        """Clean up resources"""
        if self.session:
            self.session.close()
        if self._cache:
            self._cache.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions
def get_ads_only(api_key: str, query: str, max_ads: int = 3, **kwargs) -> List[Ad]:
    """Quick function to get ads only"""
    with AdsonAI(api_key=api_key) as client:
        return client.get_ads_only(query, max_ads, **kwargs)


def get_conversational_ads(api_key: str, conversation: Union[str, List[str]], **kwargs) -> ConversationalResult:
    """Quick function to get enhanced conversational ads"""
    with AdsonAI(api_key=api_key) as client:
        return client.get_conversational_ads(conversation, **kwargs)


def get_mixed_content(api_key: str, query: str, max_ads: int = 3, **kwargs) -> List[Ad]:
    """Quick function to get mixed content"""
    with AdsonAI(api_key=api_key) as client:
        return client.get_mixed_content(query, max_ads, **kwargs)


# Legacy convenience function (backward compatibility)
def get_ads(api_key: str, query: str, max_ads: int = 3):
    """
    Legacy function for backward compatibility with v1.0
    
    Args:
        api_key: Your AdsonAI API key
        query: Search query
        max_ads: Maximum ads to return
        
    Returns:
        List of Ad objects
    """
    with AdsonAI(api_key=api_key) as client:
        return client.get_contextual_ads(query, max_ads)