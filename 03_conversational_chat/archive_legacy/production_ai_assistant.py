#!/usr/bin/env python3
"""
IntelliPart AI Conversational Assistant
Production-grade AI assistant with Gemini Pro, OpenAI, and Invertex AI integration
Handles technical queries, part identification, and productivity enhancement
"""

import json
import logging
import asyncio
import base64
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path

# Production logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Standardized AI response structure"""
    content: str
    confidence: float
    source: str
    processing_time: float
    error: Optional[str] = None
    suggestions: Optional[List[str]] = None

@dataclass
class QueryContext:
    """Context information for AI queries"""
    user_id: str
    session_id: str
    query_type: str
    priority: str
    department: str
    previous_queries: List[str]

class ProductionErrorHandler:
    """Production-grade error handling for AI operations"""
    
    def __init__(self):
        self.error_log = []
        self.fallback_responses = {
            "part_search": "I'm experiencing technical difficulties with advanced search. Please try a simpler query or contact support.",
            "technical_info": "Technical information is temporarily unavailable. Please refer to the part documentation or contact technical support.",
            "general": "I'm currently experiencing issues. Please try again in a moment or contact support for immediate assistance."
        }
    
    def handle_ai_error(self, error: Exception, context: QueryContext) -> AIResponse:
        """Handle AI service errors gracefully"""
        error_msg = str(error)
        self.error_log.append({
            "timestamp": datetime.now().isoformat(),
            "error": error_msg,
            "context": context.query_type,
            "user_id": context.user_id
        })
        
        logger.error(f"AI Error for user {context.user_id}: {error_msg}")
        
        fallback_content = self.fallback_responses.get(context.query_type, self.fallback_responses["general"])
        
        return AIResponse(
            content=fallback_content,
            confidence=0.0,
            source="fallback",
            processing_time=0.1,
            error=error_msg,
            suggestions=["Try rephrasing your question", "Contact technical support", "Use the search function"]
        )

class GeminiProAssistant:
    """Gemini Pro integration for automotive parts intelligence"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "gemini-pro"
        self.vision_model = "gemini-pro-vision"
        self.initialized = False
        
        try:
            # Import Gemini SDK
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.vision_model_instance = genai.GenerativeModel(self.vision_model)
            self.initialized = True
            logger.info("Gemini Pro assistant initialized successfully")
        except ImportError:
            logger.warning("Gemini SDK not available. Install google-generativeai package.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Pro: {str(e)}")
    
    async def process_text_query(self, query: str, context: QueryContext, part_data: Dict = None) -> AIResponse:
        """Process text-based queries using Gemini Pro"""
        
        if not self.initialized:
            raise Exception("Gemini Pro not properly initialized")
        
        start_time = datetime.now()
        
        try:
            # Prepare prompt with automotive context
            system_prompt = """You are an expert automotive parts specialist working for Mahindra & Mahindra. 
            You have deep knowledge of automotive parts, their specifications, compatibility, and maintenance.
            Provide accurate, helpful, and professional responses. Focus on practical solutions and safety considerations.
            If you're unsure about something, clearly state the uncertainty and suggest consulting technical documentation."""
            
            # Add part data context if available
            context_info = ""
            if part_data:
                context_info = f"\nCurrent part context: {json.dumps(part_data, indent=2)}"
            
            full_prompt = f"{system_prompt}\n\nUser Query: {query}{context_info}\n\nResponse:"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                content=response.text,
                confidence=0.9,  # Gemini typically provides high-quality responses
                source="gemini-pro",
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Gemini Pro query failed: {str(e)}")
            raise e
    
    async def analyze_part_image(self, image_path: str, query: str = "Identify this automotive part") -> AIResponse:
        """Analyze part images using Gemini Pro Vision"""
        
        if not self.initialized:
            raise Exception("Gemini Pro Vision not properly initialized")
        
        start_time = datetime.now()
        
        try:
            # Read and encode image
            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()
            
            # Prepare vision prompt
            vision_prompt = f"""Analyze this automotive part image and provide:
            1. Part identification and name
            2. Category and subcategory
            3. Visible specifications or markings
            4. Potential vehicle compatibility
            5. Condition assessment
            6. Safety considerations
            
            User query: {query}"""
            
            # Generate response with image
            response = self.vision_model_instance.generate_content([vision_prompt, image_data])
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                content=response.text,
                confidence=0.85,
                source="gemini-pro-vision",
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Gemini Pro Vision analysis failed: {str(e)}")
            raise e

class OpenAIAssistant:
    """OpenAI GPT integration for automotive intelligence"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "gpt-4-turbo"
        self.vision_model = "gpt-4-vision-preview"
        self.initialized = False
        
        try:
            # Import OpenAI SDK
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.initialized = True
            logger.info("OpenAI assistant initialized successfully")
        except ImportError:
            logger.warning("OpenAI SDK not available. Install openai package.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {str(e)}")
    
    async def process_text_query(self, query: str, context: QueryContext, part_data: Dict = None) -> AIResponse:
        """Process text queries using GPT-4"""
        
        if not self.initialized:
            raise Exception("OpenAI not properly initialized")
        
        start_time = datetime.now()
        
        try:
            # Prepare messages with context
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert automotive parts specialist for Mahindra & Mahindra with 20+ years of experience. 
                    You excel at technical troubleshooting, part identification, compatibility analysis, and maintenance guidance.
                    Always prioritize safety and provide practical, actionable advice. Be concise but thorough."""
                },
                {
                    "role": "user", 
                    "content": query
                }
            ]
            
            # Add part data context if available
            if part_data:
                messages.insert(1, {
                    "role": "system",
                    "content": f"Current part context: {json.dumps(part_data)}"
                })
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                content=response.choices[0].message.content,
                confidence=0.9,
                source="openai-gpt4",
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"OpenAI query failed: {str(e)}")
            raise e

class InvertexAIConnector:
    """Invertex AI integration for specialized automotive queries"""
    
    def __init__(self, api_endpoint: str, api_key: str):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.initialized = False
        
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
            self.initialized = True
            logger.info("Invertex AI connector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Invertex AI: {str(e)}")
    
    async def process_query(self, query: str, context: QueryContext) -> AIResponse:
        """Process queries using Invertex AI"""
        
        if not self.initialized:
            raise Exception("Invertex AI not properly initialized")
        
        start_time = datetime.now()
        
        try:
            payload = {
                "model": "invertex-automotive",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an automotive parts expert. Provide accurate technical information."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "context": {
                    "department": context.department,
                    "user_type": "technical"
                }
            }
            
            response = self.session.post(
                f"{self.api_endpoint}/chat/completions",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                content=result["choices"][0]["message"]["content"],
                confidence=0.85,
                source="invertex-ai",
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Invertex AI query failed: {str(e)}")
            raise e

class IntelliPartAIAssistant:
    """Main AI assistant orchestrating multiple AI services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.error_handler = ProductionErrorHandler()
        self.assistants = {}
        
        # Initialize available AI services
        self._initialize_assistants()
        
        logger.info(f"IntelliPart AI Assistant initialized with {len(self.assistants)} services")
    
    def _initialize_assistants(self):
        """Initialize all available AI assistants"""
        
        # Gemini Pro
        if self.config.get("gemini_api_key"):
            try:
                self.assistants["gemini"] = GeminiProAssistant(self.config["gemini_api_key"])
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {str(e)}")
        
        # OpenAI
        if self.config.get("openai_api_key"):
            try:
                self.assistants["openai"] = OpenAIAssistant(self.config["openai_api_key"])
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {str(e)}")
        
        # Invertex AI
        if self.config.get("invertex_endpoint") and self.config.get("invertex_api_key"):
            try:
                self.assistants["invertex"] = InvertexAIConnector(
                    self.config["invertex_endpoint"],
                    self.config["invertex_api_key"]
                )
            except Exception as e:
                logger.warning(f"Invertex AI initialization failed: {str(e)}")
    
    async def process_query(self, query: str, context: QueryContext, part_data: Dict = None) -> AIResponse:
        """Process user query using the best available AI service"""
        
        # Determine best AI service based on query type and availability
        preferred_service = self._select_ai_service(context.query_type)
        
        try:
            if preferred_service == "gemini" and "gemini" in self.assistants:
                return await self.assistants["gemini"].process_text_query(query, context, part_data)
            elif preferred_service == "openai" and "openai" in self.assistants:
                return await self.assistants["openai"].process_text_query(query, context, part_data)
            elif preferred_service == "invertex" and "invertex" in self.assistants:
                return await self.assistants["invertex"].process_query(query, context)
            else:
                # Fallback to any available service
                for service_name, assistant in self.assistants.items():
                    try:
                        if hasattr(assistant, 'process_text_query'):
                            return await assistant.process_text_query(query, context, part_data)
                        elif hasattr(assistant, 'process_query'):
                            return await assistant.process_query(query, context)
                    except Exception as e:
                        logger.warning(f"Service {service_name} failed, trying next: {str(e)}")
                        continue
                
                # No services available
                raise Exception("No AI services available")
                
        except Exception as e:
            logger.error(f"All AI services failed for query: {query}")
            return self.error_handler.handle_ai_error(e, context)
    
    def _select_ai_service(self, query_type: str) -> str:
        """Select the best AI service based on query type"""
        
        service_preferences = {
            "technical_specs": "gemini",
            "troubleshooting": "openai", 
            "part_identification": "gemini",
            "compatibility": "openai",
            "general": "invertex"
        }
        
        return service_preferences.get(query_type, "gemini")
    
    async def analyze_image(self, image_path: str, query: str, context: QueryContext) -> AIResponse:
        """Analyze part images using vision-capable AI"""
        
        try:
            # Try Gemini Pro Vision first
            if "gemini" in self.assistants:
                return await self.assistants["gemini"].analyze_part_image(image_path, query)
            else:
                raise Exception("No vision-capable AI services available")
                
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            return self.error_handler.handle_ai_error(e, context)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all AI services"""
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "overall_health": "healthy"
        }
        
        for service_name, assistant in self.assistants.items():
            try:
                # Simple health check - verify initialization
                is_healthy = hasattr(assistant, 'initialized') and assistant.initialized
                status["services"][service_name] = {
                    "status": "healthy" if is_healthy else "degraded",
                    "initialized": is_healthy
                }
            except Exception as e:
                status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                status["overall_health"] = "degraded"
        
        if not self.assistants:
            status["overall_health"] = "unhealthy"
        
        return status

# Production configuration loader
def load_ai_config() -> Dict[str, Any]:
    """Load AI configuration from environment variables or config file"""
    
    config = {
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "invertex_endpoint": os.getenv("INVERTEX_ENDPOINT"),
        "invertex_api_key": os.getenv("INVERTEX_API_KEY")
    }
    
    # Try loading from config file if environment variables not set
    config_file = Path("ai_config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                config.update({k: v for k, v in file_config.items() if v})
        except Exception as e:
            logger.warning(f"Failed to load config file: {str(e)}")
    
    return config

# Demo function
async def demo_ai_assistant():
    """Demonstrate AI assistant capabilities"""
    
    config = load_ai_config()
    assistant = IntelliPartAIAssistant(config)
    
    # Demo context
    context = QueryContext(
        user_id="demo_user",
        session_id="demo_session",
        query_type="technical_specs",
        priority="normal",
        department="engineering",
        previous_queries=[]
    )
    
    # Demo queries
    queries = [
        "What are the specifications for brake pads in XUV300?",
        "How do I check brake pad wear?",
        "Which engine oil is compatible with 1.5L diesel engine?",
        "What's the replacement interval for air filters?"
    ]
    
    print("🤖 IntelliPart AI Assistant Demo")
    print("=" * 50)
    
    for query in queries:
        print(f"\n📝 Query: {query}")
        try:
            response = await assistant.process_query(query, context)
            print(f"🎯 Response ({response.source}): {response.content[:200]}...")
            print(f"⏱️  Processing time: {response.processing_time:.2f}s")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Health status
    print(f"\n🏥 Health Status:")
    health = assistant.get_health_status()
    for service, status in health["services"].items():
        print(f"   {service}: {status['status']}")

if __name__ == "__main__":
    asyncio.run(demo_ai_assistant())
