"""
AdsonAI Python SDK - Version 2.0
Simple yet powerful SDK for contextual ad matching with AI

Features:
- Separate consumption of ads and conversations
- Enhanced AI matching algorithm integration  
- Advanced context and intent handling
- Detailed matching metadata
- Caching and performance optimization
- Full backward compatibility
"""

__version__ = "2.0.0"
__author__ = "AdsonAI Team"
__email__ = "developers@adsonai.com"
__description__ = "Python SDK for AdsonAI contextual advertising platform"
__url__ = "https://github.com/adsonai/adsonai-python-sdk"
__license__ = "MIT"

# Import main classes
from .client import AdsonAI
from .models import (
    Ad,
    MatchingContext, 
    ContentType,
    IntentType,
    ApiResponse,
    UsageStats
)

from .exceptions import (
    AdsonAIError,
    AuthenticationError, 
    APIError,
    ValidationError,
    NetworkError,
    RateLimitError,
    ConfigurationError,
    CacheError,
    ContentTypeError,
    MatchingError
)

# Import convenience functions
from .client import (
    get_ads_only,
    get_conversational_ads, 
    get_mixed_content,
    get_ads  # Legacy function
)

# Public API
__all__ = [
    # Main SDK class
    "AdsonAI",
    
    # Data models
    "Ad",
    "MatchingContext",
    "ContentType", 
    "IntentType",
    "ApiResponse",
    "UsageStats",
    
    # Convenience functions
    "get_ads_only",
    "get_conversational_ads",
    "get_mixed_content",
    "get_ads",  # Legacy function
    
    # Exceptions
    "AdsonAIError",
    "AuthenticationError", 
    "APIError",
    "ValidationError",
    "NetworkError",
    "RateLimitError",
    "ConfigurationError",
    "CacheError",
    "ContentTypeError",
    "MatchingError"
]

# Version info
def get_version():
    """Get SDK version"""
    return __version__

def get_version_info():
    """Get detailed version information"""
    return {
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "url": __url__,
        "license": __license__
    }

def get_features():
    """Get list of SDK features"""
    return [
        "separate_ad_conversation_consumption",
        "enhanced_ai_matching",
        "intent_classification", 
        "semantic_similarity",
        "context_awareness",
        "caching",
        "performance_optimization",
        "backward_compatibility",
        "detailed_error_handling",
        "usage_analytics"
    ]

# Migration and upgrade helpers
def check_legacy_usage():
    """
    Check if user is using legacy patterns and suggest updates
    This can be called manually by developers who want to upgrade
    """
    print("""
🔄 AdsonAI SDK v2.0 - New Features Available!

Your existing code will continue to work, but you now have access to:

NEW METHODS:
  • client.get_ads_only() - For pure advertising scenarios (e-commerce, search)
  • client.get_conversational_ads() - For chatbots and conversations  
  • client.get_mixed_content() - For content platforms and mixed scenarios

ENHANCED FEATURES:
  • Better AI matching with intent detection and semantic similarity
  • Separate optimization for ads vs conversations
  • Advanced context with user demographics and location
  • Detailed matching metadata (relevance, confidence, intent scores)
  • Built-in caching for better performance
  • Enhanced error handling and retry logic

EXAMPLE UPGRADE:
  # Old way (still works)
  ads = client.get_contextual_ads("running shoes")
  
  # New way - better results for different scenarios:
  
  # For e-commerce/advertising:
  ads = client.get_ads_only("running shoes", max_ads=3)
  
  # For chatbots:
  ads = client.get_conversational_ads("I need running shoes", max_ads=1)
  
  # For content/blogs:
  ads = client.get_mixed_content("running shoes guide", max_ads=2)
  
  # With enhanced context:
  from adsonai_sdk import MatchingContext, ContentType
  
  context = MatchingContext(
      content_type=ContentType.ADS_ONLY,
      user_location="San Francisco",
      user_demographics={"age": "25-35", "interests": ["fitness"]},
      semantic_boost=1.2
  )
  
  ads = client.get_ads_only("running shoes", context=context)

For full documentation: https://docs.adsonai.com/sdk/python
    """)

def show_migration_examples():
    """Show specific migration examples"""
    examples = {
        "E-commerce Integration": """
# Before (v1.0)
client = AdsonAI(api_key="your_key")
ads = client.get_contextual_ads("smartphones", max_ads=5)

# After (v2.0) - Better for e-commerce
context = MatchingContext(
    content_type=ContentType.ADS_ONLY,
    user_location="California",
    user_demographics={"age": "25-35", "budget": "high"},
    semantic_boost=1.3,
    bid_weight=1.2
)
ads = client.get_ads_only("smartphones", max_ads=5, context=context)
        """,
        
        "Chatbot Integration": """
# Before (v1.0)
client = AdsonAI(api_key="your_key")
ads = client.get_contextual_ads(user_message, max_ads=1)

# After (v2.0) - Better for conversations
conversation_history = ["Hi", "Looking for tech products", "Budget is $500"]
ads = client.get_conversational_ads(
    conversation=conversation_history + [user_message],
    max_ads=1,
    conversation_context={
        "session_id": session_id,
        "user_preferences": user_prefs,
        "location": user_location
    }
)
        """,
        
        "Content Platform": """
# Before (v1.0)
client = AdsonAI(api_key="your_key")
ads = client.get_contextual_ads(article_keywords, max_ads=2)

# After (v2.0) - Better for content
context = MatchingContext(
    content_type=ContentType.MIXED,
    semantic_boost=1.1,
    bid_weight=0.8,  # Lower bid influence for content
    recency_preference=True
)
ads = client.get_mixed_content(
    article_keywords, 
    max_ads=2, 
    context=context,
    content_preferences={"tone": "informational", "audience": "professionals"}
)
        """
    }
    
    print("📝 Migration Examples:\n")
    for title, example in examples.items():
        print(f"## {title}")
        print(example)
        print()

# Performance and debugging helpers
def enable_debug_logging():
    """Enable debug logging for the SDK"""
    import logging
    
    logger = logging.getLogger('adsonai_sdk')
    logger.setLevel(logging.DEBUG)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    print("🐛 Debug logging enabled for AdsonAI SDK")

def get_system_info():
    """Get system information for debugging"""
    import sys
    import platform
    
    try:
        import requests
        requests_version = requests.__version__
    except:
        requests_version = "Not installed"
    
    return {
        "sdk_version": __version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "requests_version": requests_version,
        "features": get_features()
    }

# Quick start helper
def quick_start_guide():
    """Display quick start guide"""
    print(f"""
🚀 AdsonAI SDK v{__version__} Quick Start Guide

1. INSTALLATION:
   pip install adsonai-sdk

2. GET API KEY:
   Visit: https://adsonai.vercel.app/api-keys
   Create new API key (starts with 'adsonai_')

3. BASIC USAGE:
   from adsonai_sdk import AdsonAI
   
   client = AdsonAI(api_key="your_adsonai_api_key")
   
   # For advertising/e-commerce:
   ads = client.get_ads_only("running shoes", max_ads=3)
   
   # For chatbots:
   ads = client.get_conversational_ads("I need a laptop", max_ads=1)
   
   # For content/blogs:
   ads = client.get_mixed_content("productivity tips", max_ads=2)

4. ENHANCED CONTEXT:
   from adsonai_sdk import MatchingContext, ContentType
   
   context = MatchingContext(
       content_type=ContentType.ADS_ONLY,
       user_location="Your City",
       user_demographics={{"age": "25-35"}},
       semantic_boost=1.2
   )
   
   ads = client.get_ads_only("query", context=context)

5. VIEW RESULTS:
   for ad in ads:
       print(f"{{ad.brand_name}}: {{ad.ad_text}}")
       print(f"Relevance: {{ad.relevance_score:.2f}}")
       print(f"Confidence: {{ad.confidence_level:.2f}}")

For complete documentation: https://docs.adsonai.com/sdk/python
For support: developers@adsonai.com
    """)

# Initialize SDK information on import (optional)
def _check_environment():
    """Check environment and provide helpful warnings"""
    import sys
    import warnings
    
    # Check Python version
    if sys.version_info < (3, 7):
        warnings.warn(
            f"AdsonAI SDK v{__version__} requires Python 3.7 or higher. "
            f"Current version: {sys.version}. Please upgrade for full compatibility.",
            UserWarning,
            stacklevel=2
        )
    
    # Check if requests is available
    try:
        import requests
        if tuple(map(int, requests.__version__.split('.')[:2])) < (2, 25):
            warnings.warn(
                f"AdsonAI SDK works best with requests>=2.25.0. "
                f"Current version: {requests.__version__}",
                UserWarning,
                stacklevel=2
            )
    except ImportError:
        raise ImportError(
            "AdsonAI SDK requires the 'requests' library. "
            "Install it with: pip install requests"
        )

# Run environment check on import
try:
    _check_environment()
except Exception:
    # Don't fail import if environment check fails
    pass

# Module-level convenience for really quick usage
def quick_ads(api_key: str, query: str, content_type: str = "ads", max_ads: int = 3):
    """
    Ultra-quick function for getting ads without creating client
    
    Args:
        api_key: Your AdsonAI API key
        query: Search query
        content_type: "ads", "conversation", or "mixed"
        max_ads: Maximum ads to return
        
    Returns:
        List of ads
    """
    if content_type.lower() in ["ads", "advertising", "ads_only"]:
        return get_ads_only(api_key, query, max_ads)
    elif content_type.lower() in ["conversation", "conversational", "chat"]:
        return get_conversational_ads(api_key, query, max_ads)
    elif content_type.lower() in ["mixed", "content"]:
        return get_mixed_content(api_key, query, max_ads)
    else:
        return get_ads(api_key, query, max_ads)  # Legacy fallback

# Add quick_ads to public API
__all__.append("quick_ads")