"""Eco Chatbot service using Gemini 1.5 Flash for environmental transportation advice."""

import google.generativeai as genai
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.utils.config import config

logger = logging.getLogger(__name__)

class EcoChatbotService:
    """AI-powered eco chatbot using Gemini 1.5 Flash."""
    
    def __init__(self):
        """Initialize the eco chatbot service."""
        self.model = None
        self.chat_session = None
        self.conversation_history = []
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model."""
        try:
            if config.GEMINI_API_KEY and config.GEMINI_API_KEY != "demo_key":
                genai.configure(api_key=config.GEMINI_API_KEY)
                
                # Use Gemini 1.5 Flash for fast responses
                self.model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 1000,
                    },
                    system_instruction=self._get_system_prompt()
                )
                
                # Start chat session
                self.chat_session = self.model.start_chat(history=[])
                logger.info("Gemini 1.5 Flash eco chatbot initialized successfully")
                
            else:
                logger.warning("Gemini API key not configured, chatbot will use fallback responses")
                
        except Exception as e:
            logger.error(f"Error initializing Gemini eco chatbot: {e}")
            self.model = None
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the eco chatbot."""
        return """You are EcoBot, an AI assistant specialized in sustainable transportation and environmental impact reduction. Your expertise includes:

- Eco-friendly route planning and optimization
- Public transportation recommendations
- Carbon footprint calculations and reduction strategies
- Air quality awareness and health impacts
- Sustainable mobility solutions (cycling, walking, electric vehicles)
- Real-time environmental data interpretation
- Traffic pattern analysis for emission reduction

Guidelines:
- Always prioritize environmental sustainability
- Provide practical, actionable advice
- Include specific data when possible (CO2 savings, time estimates)
- Consider user context (location, weather, air quality)
- Be encouraging and positive about eco-friendly choices
- Explain environmental benefits clearly
- Suggest alternatives when eco options aren't available

IMPORTANT FORMATTING RULES:
- Use ONLY plain text in your responses
- Do NOT use any markdown formatting like **bold**, *italic*, or # headers
- Do NOT use bullet points with * or -
- Use simple numbered lists (1. 2. 3.) if needed
- Keep responses conversational and easy to read without any special formatting

Keep responses concise but informative, and always include at least one specific eco tip."""
    
    async def get_chat_response(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get AI response from the eco chatbot."""
        try:
            if not self.model or not self.chat_session:
                return self._get_fallback_response(user_message)
            
            # Add context to the message if provided
            enhanced_message = self._enhance_message_with_context(user_message, context)
            
            # Get response from Gemini
            response = self.chat_session.send_message(enhanced_message)
            
            # Store conversation history
            self.conversation_history.append({
                'user': user_message,
                'bot': response.text,
                'timestamp': datetime.now().isoformat(),
                'context': context
            })
            
            # Extract any actionable suggestions
            suggestions = self._extract_suggestions(response.text)
            
            return {
                'response': response.text,
                'suggestions': suggestions,
                'timestamp': datetime.now().isoformat(),
                'model': 'gemini-1.5-flash',
                'conversation_id': len(self.conversation_history)
            }
            
        except Exception as e:
            logger.error(f"Error getting chatbot response: {e}")
            return self._get_fallback_response(user_message)
    
    def _enhance_message_with_context(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        """Enhance user message with relevant context."""
        if not context:
            return message
        
        context_parts = []
        
        # Add location context
        if 'location' in context:
            context_parts.append(f"User location: {context['location']}")
        
        # Add current route context
        if 'current_route' in context:
            route = context['current_route']
            context_parts.append(f"Current route: {route.get('from', 'Unknown')} to {route.get('to', 'Unknown')}")
            if 'distance' in route:
                context_parts.append(f"Distance: {route['distance']} km")
        
        # Add vehicle context
        if 'vehicle_type' in context:
            context_parts.append(f"Vehicle type: {context['vehicle_type']}")
        
        # Add environmental data context
        if 'air_quality' in context:
            aq = context['air_quality']
            context_parts.append(f"Current air quality: AQI {aq.get('aqi', 'unknown')}")
        
        if context_parts:
            enhanced_message = f"Context: {'; '.join(context_parts)}\n\nUser question: {message}"
            return enhanced_message
        
        return message
    
    def _extract_suggestions(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract actionable suggestions from the AI response."""
        suggestions = []
        
        # Look for common suggestion patterns
        suggestion_keywords = [
            'recommend', 'suggest', 'try', 'consider', 'use', 'switch to',
            'opt for', 'choose', 'go with', 'take the'
        ]
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in suggestion_keywords):
                if len(line) > 20 and len(line) < 200:  # Reasonable suggestion length
                    suggestions.append({
                        'text': line,
                        'type': 'recommendation',
                        'actionable': True
                    })
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def get_eco_tips(self, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get personalized eco tips based on context."""
        try:
            if not self.model:
                return self._get_fallback_tips()
            
            # Build context-aware prompt
            prompt = "Provide 3 specific eco-friendly transportation tips"
            
            if context:
                if 'location' in context:
                    prompt += f" for someone in {context['location']}"
                if 'commute_distance' in context:
                    prompt += f" with a typical commute of {context['commute_distance']} km"
            
            prompt += ". Make each tip specific, actionable, and include estimated environmental impact. Use plain text only, no markdown formatting."
            
            response = self.model.generate_content(prompt)
            
            # Parse tips from response
            tips = []
            lines = response.text.split('\n')
            current_tip = ""
            tip_count = 0

            # Enhanced categories and icons mapping
            category_mapping = {
                'public': {'category': 'Public Transport', 'icon': '🚌', 'impact': 'high'},
                'bus': {'category': 'Public Transport', 'icon': '🚌', 'impact': 'high'},
                'train': {'category': 'Public Transport', 'icon': '🚊', 'impact': 'high'},
                'cycle': {'category': 'Active Transport', 'icon': '🚴', 'impact': 'high'},
                'bike': {'category': 'Active Transport', 'icon': '🚴', 'impact': 'high'},
                'walk': {'category': 'Active Transport', 'icon': '🚶', 'impact': 'high'},
                'drive': {'category': 'Driving Efficiency', 'icon': '⚡', 'impact': 'medium'},
                'fuel': {'category': 'Driving Efficiency', 'icon': '⛽', 'impact': 'medium'},
                'route': {'category': 'Route Planning', 'icon': '🗺️', 'impact': 'medium'},
                'trip': {'category': 'Trip Planning', 'icon': '🗺️', 'impact': 'medium'},
                'electric': {'category': 'Clean Energy', 'icon': '🔋', 'impact': 'high'},
                'carpool': {'category': 'Shared Transport', 'icon': '👥', 'impact': 'medium'}
            }

            for line in lines:
                line = line.strip()
                if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or
                           line.startswith('•') or line.startswith('-')):
                    if current_tip:
                        # Determine category and icon based on tip content
                        tip_lower = current_tip.lower()
                        category_info = {'category': 'Eco Transport', 'icon': '🌱', 'impact': 'medium'}

                        for keyword, info in category_mapping.items():
                            if keyword in tip_lower:
                                category_info = info
                                break

                        # Extract potential savings information
                        savings = "Reduces emissions"
                        if "kg" in current_tip and "co2" in tip_lower:
                            # Try to extract CO2 savings
                            import re
                            co2_match = re.search(r'(\d+\.?\d*)\s*kg.*co2', tip_lower)
                            if co2_match:
                                savings = f"{co2_match.group(1)} kg CO₂ saved"
                        elif "%" in current_tip:
                            # Try to extract percentage savings
                            import re
                            percent_match = re.search(r'(\d+)%', current_tip)
                            if percent_match:
                                savings = f"{percent_match.group(1)}% emission reduction"

                        tips.append({
                            'tip': current_tip.strip(),
                            'category': category_info['category'],
                            'impact': category_info['impact'],
                            'icon': category_info['icon'],
                            'savings': savings
                        })
                        tip_count += 1
                    current_tip = line
                elif line and current_tip:
                    current_tip += " " + line

            # Add the last tip
            if current_tip and tip_count < 3:
                tip_lower = current_tip.lower()
                category_info = {'category': 'Eco Transport', 'icon': '🌱', 'impact': 'medium'}

                for keyword, info in category_mapping.items():
                    if keyword in tip_lower:
                        category_info = info
                        break

                savings = "Reduces emissions"
                if "kg" in current_tip and "co2" in tip_lower:
                    import re
                    co2_match = re.search(r'(\d+\.?\d*)\s*kg.*co2', tip_lower)
                    if co2_match:
                        savings = f"{co2_match.group(1)} kg CO₂ saved"
                elif "%" in current_tip:
                    import re
                    percent_match = re.search(r'(\d+)%', current_tip)
                    if percent_match:
                        savings = f"{percent_match.group(1)}% emission reduction"

                tips.append({
                    'tip': current_tip.strip(),
                    'category': category_info['category'],
                    'impact': category_info['impact'],
                    'icon': category_info['icon'],
                    'savings': savings
                })

            return tips[:3]  # Return top 3 tips
            
        except Exception as e:
            logger.error(f"Error getting eco tips: {e}")
            return self._get_fallback_tips()
    
    def _get_fallback_response(self, user_message: str) -> Dict[str, Any]:
        """Provide fallback response when Gemini is unavailable."""
        fallback_responses = {
            'route': "I'd recommend checking public transportation options or cycling routes for a more eco-friendly journey. These alternatives can significantly reduce your carbon footprint!",
            'traffic': "During heavy traffic, consider using public transit or planning your trip for off-peak hours to reduce emissions and save time.",
            'weather': "Weather conditions can affect your travel choices. On clear days, cycling or walking are great eco-friendly options!",
            'default': "I'm here to help you make more sustainable transportation choices! Consider public transit, cycling, or walking when possible to reduce your environmental impact."
        }
        
        # Simple keyword matching for fallback
        message_lower = user_message.lower()
        if any(word in message_lower for word in ['route', 'direction', 'way']):
            response_key = 'route'
        elif any(word in message_lower for word in ['traffic', 'congestion', 'jam']):
            response_key = 'traffic'
        elif any(word in message_lower for word in ['weather', 'rain', 'sunny']):
            response_key = 'weather'
        else:
            response_key = 'default'
        
        return {
            'response': fallback_responses[response_key],
            'suggestions': [],
            'timestamp': datetime.now().isoformat(),
            'model': 'fallback',
            'note': 'AI service temporarily unavailable'
        }
    
    def _get_fallback_tips(self) -> List[Dict[str, Any]]:
        """Provide fallback eco tips when Gemini is unavailable."""
        return [
            {
                'tip': 'Switch to public transportation for your daily commute. Buses and trains can reduce your carbon footprint by up to 45% compared to driving alone, while saving you money on fuel and parking costs.',
                'category': 'Public Transport',
                'impact': 'high',
                'icon': '🚌',
                'savings': 'Up to 2.3 kg CO₂ per day'
            },
            {
                'tip': 'Choose cycling or walking for trips under 5 kilometers. These zero-emission options provide excellent exercise while completely eliminating transportation-related carbon emissions for short journeys.',
                'category': 'Active Transport',
                'impact': 'high',
                'icon': '🚴',
                'savings': '100% emission reduction'
            },
            {
                'tip': 'Plan and combine multiple errands into a single trip. Trip chaining can reduce your fuel consumption by 20-30% and significantly decrease the number of cold engine starts, which are less efficient.',
                'category': 'Trip Planning',
                'impact': 'medium',
                'icon': '🗺️',
                'savings': '0.5-1.2 kg CO₂ per week'
            },
            {
                'tip': 'Maintain optimal driving speeds between 50-80 km/h on highways. This speed range maximizes fuel efficiency and can improve your gas mileage by up to 15% compared to aggressive driving.',
                'category': 'Driving Efficiency',
                'impact': 'medium',
                'icon': '⚡',
                'savings': '0.8 kg CO₂ per 100km'
            },
            {
                'tip': 'Use eco-friendly route options that avoid heavy traffic and steep inclines. Smart routing can reduce fuel consumption by 10-20% and decrease travel time while lowering emissions.',
                'category': 'Route Optimization',
                'impact': 'medium',
                'icon': '🌱',
                'savings': '0.3-0.6 kg CO₂ per trip'
            }
        ]

    def is_available(self) -> bool:
        """Check if the chatbot service is available."""
        return self.model is not None and self.chat_session is not None

# Global service instance
eco_chatbot_service = EcoChatbotService()
