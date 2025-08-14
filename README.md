# AI Recipe Generator

An intelligent recipe generator application that creates personalized recipes based on available ingredients, with advanced dietary filtering and rating capabilities.

## Features

- **AI-Powered Recipe Generation**: Creates 2-3 unique recipe suggestions using Google's Gemini AI
- **Advanced Dietary Filtering**: Supports 10+ dietary restrictions including Vegetarian, Vegan, Gluten-Free, Keto, and more
- **Interactive Rating System**: Rate recipes with a 5-star system and track your favorites
- **Comprehensive Nutrition Info**: Detailed nutritional breakdown per serving
- **Smart Ingredient Processing**: Handles various ingredient formats and quantities
- **Export Functionality**: Download recipes in JSON or text format
- **Real-time Validation**: Ensures all recipes comply with selected dietary restrictions

## How to Run

### Prerequisites

1. Python 3.7 or higher
2. Google Gemini API key

### Setup

1. Install all required dependencies from the requirements file:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project directory with your API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   Get your API key from: https://makersuite.google.com/app/apikey

### Running the Application

Use the wrapper script to run the application with proper environment setup:

```bash
python run_recipe_app.py
```

This script (`run_recipe_app.py`) calls the main application (`recipe_generator5.py`) with optimized settings for library compatibility.

Alternatively, you can run the main script directly:

```bash
streamlit run recipe_generator5.py
```

### UI Demo

For a visual demonstration of the application interface and features, refer to `ui_video.mp4` included in this repository.

## Usage

1. Enter your available ingredients (comma-separated)
2. Select any dietary restrictions from the sidebar
3. Choose cuisine preferences, difficulty level, and cooking time
4. Click "Generate Filtered Recipes" to get personalized suggestions
5. Rate recipes using the star system to track your favorites
6. Download recipes in your preferred format

## Testing

The application includes comprehensive testing for both backend and frontend functionality:

### Backend Testing
Run the backend API test to verify Gemini integration:
```bash
python test_gemini_script.py
```
This script tests:
- API key validation
- Recipe generation functionality
- JSON response parsing
- Output structure validation

### Frontend Testing
Run the frontend UI tests using Playwright:
```bash
pytest tests/test_recipe_generator.py --headed
```
This test suite covers:
- Web application startup
- Form input validation
- Recipe generation workflow
- UI element interactions

**Note**: Frontend testing is currently a work in progress and may not work entirely. For testing, ensure the application is running on `localhost:8501` before executing tests.

**TODO**: Complete frontend test implementation and fix any remaining UI interaction issues.

## Technical Details

- **Framework**: Streamlit web application
- **AI Model**: Google Gemini 2.5 Flash
- **Output Format**: Structured JSON responses with comprehensive recipe data
- **Dietary Compliance**: Strict filtering ensures all recipes meet specified restrictions
- **Rating System**: Persistent session-based rating storage with statistics
- **Testing**: Backend API testing with `test_gemini_script.py`, Frontend UI testing with Playwright