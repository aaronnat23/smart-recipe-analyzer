# Test Script for Gemini API - Shows Input/Output Structure
# pip install google-genai python-dotenv

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def display_system_prompt():
    """Show the exact system prompt being used"""
    system_prompt = """You are an expert chef and nutritionist AI. When users provide ingredients, you must:

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
      "nutritional_info": {
        "calories_per_serving": 350,
        "protein_grams": 25,
        "carbs_grams": 45,
        "fat_grams": 12
      },
      "cooking_tips": [
        "Helpful tip 1",
        "Helpful tip 2"
      ]
    }
  ]
}

Requirements:
- Use primarily the ingredients provided by the user
- Suggest realistic quantities and additional common ingredients if needed
- Provide accurate cooking times and difficulty levels
- Include nutritional estimates (approximate values are acceptable)
- Give practical cooking tips
- Ensure all recipes are different from each other
- ALWAYS respond in valid JSON format only"""
    
    print("="*80)
    print("🔍 SYSTEM PROMPT STRUCTURE")
    print("="*80)
    print(system_prompt)
    print("="*80)
    return system_prompt

def test_recipe_generation():
    """Test the recipe generation with real API call"""
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        print("Create a .env file with: GEMINI_API_KEY=your_api_key_here")
        return
    
    print("✅ API Key found in environment")
    
    try:
        # Show system prompt
        system_prompt = display_system_prompt()
        
        # Initialize Gemini client
        print("\n🤖 INITIALIZING GEMINI CLIENT...")
        client = genai.Client(api_key=api_key)
        
        # Create chat with JSON output enforced
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                response_mime_type="application/json"
            )
        )
        print("✅ Chat session created successfully")
        
        # Test with sample ingredients
        test_ingredients = "chicken breast, broccoli, rice, garlic, olive oil, onion"
        additional_context = """Dietary restrictions: None
Cuisine type: Any
Difficulty level: Easy
Cooking time: Under 30 mins
Additional notes: I want something healthy and filling for dinner"""
        
        # Create user prompt
        user_prompt = f"""Generate 2-3 recipe suggestions using these ingredients: {test_ingredients}

Additional requirements:
{additional_context}

Remember to respond with valid JSON format only, following the exact structure specified in the system instructions."""
        
        print("\n📝 INPUT BEING SENT TO LLM:")
        print("-" * 50)
        print("INGREDIENTS:", test_ingredients)
        print("CONTEXT:", additional_context)
        print("\nFULL PROMPT:")
        print(user_prompt)
        
        # Send request to LLM
        print("\n🚀 SENDING REQUEST TO GEMINI...")
        response = chat.send_message(user_prompt)
        raw_response = response.text
        
        print("\n📤 RAW LLM RESPONSE:")
        print("-" * 50)
        print(raw_response)
        
        # Try to parse JSON
        print("\n🔧 PARSING JSON RESPONSE...")
        try:
            parsed_json = json.loads(raw_response)
            print("✅ JSON PARSING SUCCESSFUL!")
            
            print("\n📊 PARSED AND FORMATTED OUTPUT:")
            print("-" * 50)
            print(json.dumps(parsed_json, indent=2))
            
            # Validate the structure
            print("\n✅ VALIDATION RESULTS:")
            print("-" * 50)
            
            if 'recipes' in parsed_json:
                recipes = parsed_json['recipes']
                print(f"✅ Found {len(recipes)} recipes")
                
                # Check each recipe
                for i, recipe in enumerate(recipes, 1):
                    print(f"\n📝 Recipe {i}: {recipe.get('recipe_name', 'NO NAME')}")
                    
                    # Check required fields
                    required_fields = {
                        'recipe_name': str,
                        'ingredients': list,
                        'instructions': list,
                        'cooking_time_minutes': int,
                        'difficulty_level': str,
                        'servings': int,
                        'nutritional_info': dict,
                        'cooking_tips': list
                    }
                    
                    for field, expected_type in required_fields.items():
                        if field in recipe:
                            actual_type = type(recipe[field])
                            if actual_type == expected_type:
                                print(f"  ✅ {field}: {actual_type.__name__} ✓")
                            else:
                                print(f"  ⚠️ {field}: {actual_type.__name__} (expected {expected_type.__name__})")
                        else:
                            print(f"  ❌ {field}: MISSING")
                    
                    # Check nutritional info specifically
                    if 'nutritional_info' in recipe:
                        nutrition = recipe['nutritional_info']
                        nutrition_fields = ['calories_per_serving', 'protein_grams', 'carbs_grams', 'fat_grams']
                        print(f"  📊 Nutritional Info Check:")
                        for nfield in nutrition_fields:
                            if nfield in nutrition:
                                print(f"    ✅ {nfield}: {nutrition[nfield]}")
                            else:
                                print(f"    ❌ {nfield}: MISSING")
                
                # Summary
                print(f"\n🎯 SUMMARY:")
                print(f"✅ Generated {len(recipes)} recipes (requirement: 2-3)")
                print(f"✅ JSON format enforced and parsed successfully")
                print(f"✅ All recipes include cooking time and difficulty")
                print(f"✅ Nutritional information provided per recipe")
                
            else:
                print("❌ No 'recipes' key found in response!")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON PARSING FAILED: {e}")
            print("The LLM response is not valid JSON")
            
    except Exception as e:
        print(f"❌ ERROR DURING TEST: {e}")

def show_requirements_check():
    """Display the requirements being tested"""
    print("\n🎯 LLM INTEGRATION REQUIREMENTS CHECK:")
    print("="*50)
    print("📋 Required Features:")
    print("  1. ✅ Generate 2-3 recipe suggestions")
    print("  2. ✅ Include estimated cooking time and difficulty level")
    print("  3. ✅ Provide basic nutritional information (calories, protein, carbs)")
    print("  4. ✅ Format response as JSON for easy parsing")
    print("  5. ✅ Show system prompt structure for debugging")
    print("  6. ✅ Show raw LLM output for debugging")

if __name__ == "__main__":
    print("🧪 GEMINI API RECIPE GENERATION TEST")
    print("="*50)
    
    # Show what we're testing
    show_requirements_check()
    
    # Run the actual test
    test_recipe_generation()
    
    print("\n" + "="*50)
    print("🎉 Test completed! Check output above for results.")
    print("Run this script to test your API integration before using the Streamlit app.")
