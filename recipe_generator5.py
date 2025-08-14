# Enhanced Recipe Generator with Dietary Filters & Recipe Rating
# pip install streamlit google-genai python-dotenv

import streamlit as st
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Configuration
@dataclass
class AppConfig:
    MODEL_NAME: str = "gemini-2.5-flash"
    MAX_RETRIES: int = 3
    TIMEOUT_SECONDS: int = 30
    DEFAULT_TEMPERATURE: float = 0.7

config = AppConfig()

class EnhancedGeminiClient:
    """Enhanced Gemini API client with dietary filtering and JSON output"""
    
    def __init__(self, api_key: str):
        try:
            self.client = genai.Client(api_key=api_key)
            self.chat = None
            self.system_prompt = self._create_system_prompt()
            self._initialize_chat()
        except Exception as e:
            st.error(f"Failed to initialize Gemini client: {str(e)}")
            raise
    
    def _create_system_prompt(self) -> str:
        """Create the structured system prompt with enhanced dietary filtering"""
        return """You are an expert chef and nutritionist AI. When users provide ingredients, you must:

IMPORTANT: Always respond with valid JSON format only, no additional text.

Generate 2-3 recipe suggestions using the provided ingredients with the following structure:

{
  "recipes": [
    {
      "recipe_name": "Name of the recipe",
      "ingredients": [
        {"ingredient": "ingredient name", "quantity": "amount with unit"}
      ],
      "instructions": [
        "Step 1 instruction",
        "Step 2 instruction",
        "etc."
      ],
      "cooking_time_minutes": 30,
      "difficulty_level": "Easy|Intermediate|Advanced",
      "servings": 4,
      "dietary_tags": ["Vegetarian", "Gluten-Free", "Low-Carb"],
      "nutritional_info": {
        "calories_per_serving": 350,
        "protein_grams": 25,
        "carbs_grams": 45,
        "fat_grams": 12,
        "fiber_grams": 8,
        "sugar_grams": 5
      },
      "cooking_tips": [
        "Helpful tip 1",
        "Helpful tip 2"
      ],
      "allergen_warnings": ["Contains nuts", "Contains dairy"]
    }
  ]
}

DIETARY RESTRICTIONS COMPLIANCE:
- If user specifies dietary restrictions, ALL recipes must comply with those restrictions
- Vegetarian: No meat, fish, or poultry
- Vegan: No animal products (meat, dairy, eggs, honey)
- Gluten-Free: No wheat, barley, rye, or gluten-containing ingredients
- Dairy-Free: No milk, cheese, butter, or dairy products
- Low-Carb: Maximum 20g carbs per serving
- Keto: Maximum 10g net carbs, high fat content
- Paleo: No grains, legumes, dairy, or processed foods
- Nut-Free: No tree nuts or peanuts
- Diabetic-Friendly: Low sugar, controlled carbs
- Heart-Healthy: Low sodium, low saturated fat

Requirements:
- Use primarily the ingredients provided by the user
- STRICTLY follow any dietary restrictions specified
- Suggest realistic quantities and additional ingredients that comply with dietary needs
- Include accurate dietary tags for each recipe
- List any allergen warnings
- Provide accurate cooking times and difficulty levels
- Include comprehensive nutritional estimates
- Give practical cooking tips
- Ensure all recipes are different from each other
- ALWAYS respond in valid JSON format only"""
    
    def _initialize_chat(self):
        """Initialize a new chat session with JSON output enforced"""
        try:
            self.chat = self.client.chats.create(
                model=config.MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=config.DEFAULT_TEMPERATURE,
                    response_mime_type="application/json"
                )
            )
        except Exception as e:
            st.error(f"Failed to create chat session: {str(e)}")
            raise
    
    def generate_recipes(self, ingredients: str, dietary_restrictions: List[str], additional_context: str = "") -> tuple[Optional[Dict], str, str]:
        """Generate 2-3 recipes with dietary filtering"""
        
        if not ingredients.strip():
            return None, "", ""
        
        # Enhanced prompt with dietary restrictions
        dietary_prompt = ""
        if dietary_restrictions:
            dietary_prompt = f"""
CRITICAL DIETARY REQUIREMENTS - ALL recipes must comply with:
{', '.join(dietary_restrictions)}

Ensure every recipe strictly follows these dietary restrictions. Do not suggest any recipes that violate these requirements."""
        
        formatted_prompt = f"""Generate 2-3 recipe suggestions using these ingredients: {ingredients}

{dietary_prompt}

Additional requirements:
{additional_context}

Remember to respond with valid JSON format only, following the exact structure specified in the system instructions. Include accurate dietary_tags and allergen_warnings for each recipe."""

        raw_response = ""
        
        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.chat.send_message(formatted_prompt)
                raw_response = response.text
                
                try:
                    parsed_json = json.loads(raw_response)
                    return parsed_json, raw_response, formatted_prompt
                except json.JSONDecodeError as e:
                    st.warning(f"JSON parsing failed (attempt {attempt + 1}): {str(e)}")
                    if attempt == config.MAX_RETRIES - 1:
                        return None, raw_response, formatted_prompt
                    continue
            
            except Exception as e:
                if attempt == config.MAX_RETRIES - 1:
                    raise e
                time.sleep(2 ** attempt)
        
        return None, raw_response, formatted_prompt
    
    def get_system_prompt(self) -> str:
        return self.system_prompt
    
    def reset_chat(self):
        self._initialize_chat()

def initialize_session_state():
    """Initialize session state for recipe ratings"""
    if 'recipe_ratings' not in st.session_state:
        st.session_state.recipe_ratings = {}
    if 'recipe_history' not in st.session_state:
        st.session_state.recipe_history = []

def validate_ingredients(ingredients: str) -> tuple[bool, str]:
    """Validate the ingredients input"""
    if not ingredients or not ingredients.strip():
        return False, "Please enter some ingredients"
    
    ingredient_list = [ing.strip() for ing in ingredients.split(',') if ing.strip()]
    if len(ingredient_list) < 2:
        return False, "Please enter at least 2 ingredients separated by commas"
    
    return True, ""

def display_star_rating(recipe_id: str, current_rating: float = 0) -> float:
    """Display interactive star rating component"""
    st.markdown("**⭐ Rate this recipe:**")
    
    # Get current rating from session state
    if recipe_id in st.session_state.recipe_ratings:
        current_rating = st.session_state.recipe_ratings[recipe_id]['rating']
    
    # Create columns for stars
    cols = st.columns(5)
    
    for i in range(5):
        with cols[i]:
            # Show filled star if this position is rated
            star_icon = "⭐" if i < current_rating else "☆"
            if st.button(star_icon, key=f"star_{recipe_id}_{i}", help=f"Rate {i+1} stars"):
                new_rating = i + 1
                st.session_state.recipe_ratings[recipe_id] = {
                    'rating': new_rating,
                    'timestamp': datetime.now().isoformat()
                }
                st.rerun()
    
    # Display current rating text
    if current_rating > 0:
        st.write(f"Your rating: {current_rating}/5 stars")
    else:
        st.write("Click a star to rate this recipe")
    
    return current_rating

def get_recipe_rating(recipe_id: str) -> float:
    """Get current rating for a recipe"""
    if recipe_id in st.session_state.recipe_ratings:
        return st.session_state.recipe_ratings[recipe_id]['rating']
    return 0

def display_recipe_card(recipe: Dict, index: int, recipe_id: str = None):
    """Display a single recipe with rating functionality"""
    if recipe_id is None:
        recipe_id = f"recipe_{index}_{hash(recipe.get('recipe_name', ''))}"
    
    with st.container():
        # Recipe header with rating
        current_rating = get_recipe_rating(recipe_id)
        stars_display = "⭐" * int(current_rating) + "☆" * (5 - int(current_rating))
        
        st.markdown(f"""
        <div style="border: 2px solid #667eea; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; background: #f8f9fa;">
            <h3 style="color: #667eea; margin-top: 0;">🍽️ Recipe {index + 1}: {recipe.get('recipe_name', 'Unknown Recipe')}</h3>
            <p style="margin: 0; color: #666;">Rating: {stars_display} ({current_rating}/5)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Recipe details in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**⏱️ Cooking Time:**")
            st.write(f"{recipe.get('cooking_time_minutes', 'N/A')} minutes")
            
        with col2:
            st.markdown("**📊 Difficulty:**")
            difficulty = recipe.get('difficulty_level', 'N/A')
            if difficulty == 'Easy':
                st.success(difficulty)
            elif difficulty == 'Intermediate':
                st.warning(difficulty)
            else:
                st.error(difficulty)
            
        with col3:
            st.markdown("**👥 Servings:**")
            st.write(recipe.get('servings', 'N/A'))
        
        # Dietary tags and allergen warnings
        col1, col2 = st.columns(2)
        
        with col1:
            dietary_tags = recipe.get('dietary_tags', [])
            if dietary_tags:
                st.markdown("**🏷️ Dietary Tags:**")
                for tag in dietary_tags:
                    st.markdown(f'<span style="background: #e8f5e8; color: #2e7d32; padding: 0.2rem 0.5rem; border-radius: 10px; margin: 0.1rem; display: inline-block; font-size: 0.8rem;">{tag}</span>', unsafe_allow_html=True)
        
        with col2:
            allergen_warnings = recipe.get('allergen_warnings', [])
            if allergen_warnings:
                st.markdown("**⚠️ Allergen Warnings:**")
                for warning in allergen_warnings:
                    st.markdown(f'<span style="background: #ffebee; color: #c62828; padding: 0.2rem 0.5rem; border-radius: 10px; margin: 0.1rem; display: inline-block; font-size: 0.8rem;">{warning}</span>', unsafe_allow_html=True)
        
        # Ingredients
        st.markdown("**🛒 Ingredients:**")
        ingredients = recipe.get('ingredients', [])
        if ingredients:
            for ing in ingredients:
                if isinstance(ing, dict):
                    st.write(f"• {ing.get('quantity', '')} {ing.get('ingredient', '')}")
                else:
                    st.write(f"• {ing}")
        
        # Instructions
        st.markdown("**👨‍🍳 Instructions:**")
        instructions = recipe.get('instructions', [])
        if instructions:
            for i, instruction in enumerate(instructions, 1):
                st.write(f"{i}. {instruction}")
        
        # Enhanced Nutritional Information
        nutrition = recipe.get('nutritional_info', {})
        if nutrition:
            st.markdown("**📊 Nutritional Information (per serving):**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                calories = nutrition.get('calories_per_serving', 'N/A')
                st.metric("Calories", calories)
            with col2:
                protein = nutrition.get('protein_grams', 'N/A')
                st.metric("Protein", f"{protein}g" if protein != 'N/A' else 'N/A')
            with col3:
                carbs = nutrition.get('carbs_grams', 'N/A')
                st.metric("Carbs", f"{carbs}g" if carbs != 'N/A' else 'N/A')
            with col4:
                fat = nutrition.get('fat_grams', 'N/A')
                st.metric("Fat", f"{fat}g" if fat != 'N/A' else 'N/A')
            
            # Additional nutrition info
            col1, col2 = st.columns(2)
            with col1:
                fiber = nutrition.get('fiber_grams', 'N/A')
                if fiber != 'N/A':
                    st.metric("Fiber", f"{fiber}g")
            with col2:
                sugar = nutrition.get('sugar_grams', 'N/A')
                if sugar != 'N/A':
                    st.metric("Sugar", f"{sugar}g")
        
        # Cooking Tips
        tips = recipe.get('cooking_tips', [])
        if tips:
            st.markdown("**💡 Cooking Tips:**")
            for tip in tips:
                st.write(f"• {tip}")
        
        # Rating component
        new_rating = display_star_rating(recipe_id, current_rating)
        
        # Save to history if rated
        if new_rating > 0:
            recipe_with_rating = recipe.copy()
            recipe_with_rating['rating'] = new_rating
            recipe_with_rating['recipe_id'] = recipe_id
            recipe_with_rating['rated_at'] = datetime.now().isoformat()
            
            # Add to history if not already there
            existing_recipe = next((r for r in st.session_state.recipe_history if r.get('recipe_id') == recipe_id), None)
            if existing_recipe:
                existing_recipe.update(recipe_with_rating)
            else:
                st.session_state.recipe_history.append(recipe_with_rating)
        
        st.markdown("---")

def display_rating_statistics():
    """Display rating statistics in sidebar"""
    if st.session_state.recipe_ratings:
        st.subheader("📊 Rating Statistics")
        
        ratings = [r['rating'] for r in st.session_state.recipe_ratings.values()]
        avg_rating = sum(ratings) / len(ratings)
        
        st.metric("Average Rating", f"{avg_rating:.1f}/5.0")
        st.metric("Total Rated Recipes", len(ratings))
        
        # Rating distribution
        rating_counts = {i: ratings.count(i) for i in range(1, 6)}
        for rating, count in rating_counts.items():
            if count > 0:
                st.write(f"{'⭐' * rating}: {count} recipe(s)")

def display_recipe_history():
    """Display previously rated recipes"""
    if st.session_state.recipe_history:
        st.subheader("📚 Your Rated Recipes")
        
        for recipe in sorted(st.session_state.recipe_history, key=lambda x: x.get('rated_at', ''), reverse=True)[:5]:
            rating = recipe.get('rating', 0)
            stars = '⭐' * int(rating)
            st.write(f"{stars} **{recipe.get('recipe_name', 'Unknown')}** - {rating}/5")

def main():
    # Initialize session state
    initialize_session_state()
    
    # Page configuration
    st.set_page_config(
        page_title="AI Recipe Generator - Enhanced",
        page_icon="👨‍🍳",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: -1rem -1rem 2rem -1rem;
            border-radius: 0 0 15px 15px;
        }
        .debug-section {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #ff6b6b;
            margin: 1rem 0;
        }
        .ingredient-chip {
            background: #e3f2fd;
            color: #1565c0;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            margin: 0.2rem;
            display: inline-block;
            font-size: 0.9rem;
        }
        .stButton > button {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.5rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🍳 AI Recipe Generator</h1>
            <p>Generate recipes with dietary filtering & rating system</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key check
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            st.error("🔑 GEMINI_API_KEY not found in environment!")
            st.info("""
            Please create a `.env` file in your project directory with:
            ```
            GEMINI_API_KEY=your_api_key_here
            ```
            Get your API key from: https://makersuite.google.com/app/apikey
            """)
            return
        else:
            st.success("🔑 API Key loaded from environment")
        
        # Enhanced Dietary Restrictions
        st.subheader("🥗 Dietary Restrictions")
        dietary_restrictions = st.multiselect(
            "Select dietary requirements (all recipes will comply)",
            [
                "Vegetarian",
                "Vegan", 
                "Gluten-Free",
                "Dairy-Free",
                "Low-Carb",
                "Keto",
                "Paleo",
                "Nut-Free",
                "Diabetic-Friendly",
                "Heart-Healthy"
            ],
            help="All generated recipes will strictly follow these dietary restrictions"
        )
        
        if dietary_restrictions:
            st.success(f"Filtering for: {', '.join(dietary_restrictions)}")
        
        # Recipe preferences
        st.subheader("🍽️ Recipe Preferences")
        
        cuisine_type = st.selectbox(
            "Preferred Cuisine",
            ["Any", "Italian", "Asian", "Mexican", "Mediterranean", "Indian", "American", "French", "Thai", "Japanese"]
        )
        
        difficulty_level = st.selectbox(
            "Difficulty Level",
            ["Any", "Easy", "Intermediate", "Advanced"]
        )
        
        cooking_time = st.selectbox(
            "Cooking Time",
            ["Any", "Under 30 mins", "30-60 mins", "Over 1 hour"]
        )
        
        # Debug options
        st.subheader("🔍 Debug Options")
        show_system_prompt = st.checkbox("Show System Prompt", value=False)
        show_raw_response = st.checkbox("Show Raw LLM Response", value=False)
        show_formatted_prompt = st.checkbox("Show Formatted Prompt", value=False)
        
        # Rating statistics
        display_rating_statistics()
        
        # Recipe history
        display_recipe_history()
        
        # Reset options
        st.subheader("🔄 Reset Options")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset Chat"):
                if 'gemini_client' in st.session_state:
                    st.session_state.gemini_client.reset_chat()
                st.success("Chat reset!")
        
        with col2:
            if st.button("Clear Ratings"):
                st.session_state.recipe_ratings = {}
                st.session_state.recipe_history = []
                st.success("Ratings cleared!")
                st.rerun()
    
    # Initialize Gemini client
    try:
        if 'gemini_client' not in st.session_state:
            with st.spinner("Initializing AI chef..."):
                st.session_state.gemini_client = EnhancedGeminiClient(api_key)
                st.success("AI chef is ready!")
    except Exception as e:
        st.error(f"Failed to initialize AI: {str(e)}")
        return
    
    # Debug sections
    if show_system_prompt:
        st.markdown('<div class="debug-section">', unsafe_allow_html=True)
        st.subheader("🔍 System Prompt Structure")
        with st.expander("View System Prompt", expanded=True):
            st.code(st.session_state.gemini_client.get_system_prompt(), language="text")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🥕 Enter Your Ingredients")
        
        # Ingredients input
        ingredients = st.text_area(
            "List your available ingredients (comma-separated)",
            placeholder="e.g., chicken breast, broccoli, rice, garlic, olive oil",
            height=100,
            help="Enter ingredients separated by commas. Be as specific as possible!"
        )
        
        # Additional context
        additional_notes = st.text_area(
            "Additional Notes (optional)",
            placeholder="e.g., I want something spicy, or I'm cooking for 4 people",
            height=80
        )
        
        # Generate button
        generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
        with generate_col2:
            generate_button = st.button("🍳 Generate Filtered Recipes", use_container_width=True)
    
    with col2:
        st.header("📋 Your Ingredients")
        if ingredients:
            ingredient_list = [ing.strip() for ing in ingredients.split(',') if ing.strip()]
            for ingredient in ingredient_list:
                st.markdown(f'<span class="ingredient-chip">{ingredient.title()}</span>', 
                          unsafe_allow_html=True)
        else:
            st.info("Enter ingredients to see them listed here")
        
        # Show active dietary restrictions
        if dietary_restrictions:
            st.header("🥗 Active Dietary Filters")
            for restriction in dietary_restrictions:
                st.markdown(f'<span style="background: #e8f5e8; color: #2e7d32; padding: 0.3rem 0.6rem; border-radius: 15px; margin: 0.2rem; display: inline-block; font-size: 0.8rem;">✓ {restriction}</span>', unsafe_allow_html=True)
    
    # Recipe generation
    if generate_button:
        # Validate input
        is_valid, error_message = validate_ingredients(ingredients)
        
        if not is_valid:
            st.error(error_message)
            return
        
        # Prepare additional context
        context_parts = []
        if cuisine_type != "Any":
            context_parts.append(f"Cuisine type: {cuisine_type}")
        if difficulty_level != "Any":
            context_parts.append(f"Difficulty level: {difficulty_level}")
        if cooking_time != "Any":
            context_parts.append(f"Cooking time: {cooking_time}")
        if additional_notes.strip():
            context_parts.append(f"Additional notes: {additional_notes}")
        
        additional_context = "\n".join(context_parts)
        
        # Generate recipes with dietary filtering
        try:
            with st.spinner("🍳 Our AI chef is creating filtered recipes for you..."):
                parsed_recipes, raw_response, formatted_prompt = st.session_state.gemini_client.generate_recipes(
                    ingredients, dietary_restrictions, additional_context
                )
            
            # Debug sections
            if show_formatted_prompt:
                st.markdown('<div class="debug-section">', unsafe_allow_html=True)
                st.subheader("🔍 Formatted Prompt Sent to LLM")
                with st.expander("View Formatted Prompt", expanded=True):
                    st.code(formatted_prompt, language="text")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if show_raw_response:
                st.markdown('<div class="debug-section">', unsafe_allow_html=True)
                st.subheader("🔍 Raw LLM Response")
                with st.expander("View Raw Response", expanded=True):
                    st.code(raw_response, language="json")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display results
            if parsed_recipes and 'recipes' in parsed_recipes:
                recipes = parsed_recipes['recipes']
                filter_text = f" (Filtered for: {', '.join(dietary_restrictions)})" if dietary_restrictions else ""
                st.header(f"🍽️ Your {len(recipes)} Custom Recipes{filter_text}")
                
                # Display each recipe with rating
                for i, recipe in enumerate(recipes):
                    recipe_id = f"recipe_{int(time.time())}_{i}"
                    display_recipe_card(recipe, i, recipe_id)
                
                # Download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📄 Download Recipes (JSON)",
                        data=json.dumps(parsed_recipes, indent=2),
                        file_name="filtered_recipes.json",
                        mime="application/json"
                    )
                
                with col2:
                    # Create enhanced text version
                    text_recipes = []
                    for i, recipe in enumerate(recipes):
                        ingredients_text = "\n".join([f"- {ing.get('quantity', '')} {ing.get('ingredient', '')}" for ing in recipe.get('ingredients', [])])
                        instructions_text = "\n".join([f"{i+1}. {inst}" for i, inst in enumerate(recipe.get('instructions', []))])
                        tips_text = "\n".join([f"- {tip}" for tip in recipe.get('cooking_tips', [])])
                        dietary_tags_text = ", ".join(recipe.get('dietary_tags', []))
                        allergen_warnings_text = ", ".join(recipe.get('allergen_warnings', []))
                        
                        nutrition = recipe.get('nutritional_info', {})
                        nutrition_text = f"""- Calories: {nutrition.get('calories_per_serving', 'N/A')}
- Protein: {nutrition.get('protein_grams', 'N/A')}g
- Carbs: {nutrition.get('carbs_grams', 'N/A')}g
- Fat: {nutrition.get('fat_grams', 'N/A')}g
- Fiber: {nutrition.get('fiber_grams', 'N/A')}g
- Sugar: {nutrition.get('sugar_grams', 'N/A')}g"""
                        
                        text_recipe = f"""Recipe {i+1}: {recipe.get('recipe_name', 'Unknown')}
Cooking Time: {recipe.get('cooking_time_minutes', 'N/A')} minutes
Difficulty: {recipe.get('difficulty_level', 'N/A')}
Servings: {recipe.get('servings', 'N/A')}
Dietary Tags: {dietary_tags_text}
Allergen Warnings: {allergen_warnings_text}

Ingredients:
{ingredients_text}

Instructions:
{instructions_text}

Nutritional Info (per serving):
{nutrition_text}

Cooking Tips:
{tips_text}

---"""
                        text_recipes.append(text_recipe)
                    
                    st.download_button(
                        label="📄 Download Recipes (Text)",
                        data="\n\n".join(text_recipes),
                        file_name="filtered_recipes.txt",
                        mime="text/plain"
                    )
                
                # Success message with dietary compliance check
                compliance_msg = ""
                if dietary_restrictions:
                    compliance_msg = f" All recipes comply with: {', '.join(dietary_restrictions)}"
                
                st.success(f"Generated {len(recipes)} recipes successfully!{compliance_msg} 🎉")
                
                # Requirements summary
                st.info(f"""
                ✅ **Enhanced Features:**
                - Generated {len(recipes)} dietary-filtered recipe suggestions
                - Interactive rating system (rate each recipe 1-5 stars)
                - Enhanced nutritional information with dietary tags
                - Allergen warnings and dietary compliance
                - Rating statistics and recipe history tracking
                """)
                
            else:
                st.error("Failed to generate recipes in proper JSON format. Please try again.")
                if raw_response:
                    st.warning("Raw response received, but JSON parsing failed.")
                    with st.expander("View Raw Response"):
                        st.code(raw_response, language="text")
                
        except Exception as e:
            st.error(f"Error generating recipes: {str(e)}")
            st.info("Please check your API key and try again.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            Made with ❤️ using Streamlit and Google Gemini API<br>
            <small>Enhanced with dietary filtering, recipe rating system, and comprehensive nutrition tracking!</small>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()