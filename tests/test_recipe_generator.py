# tests/test_recipe_generator.py

import re
from playwright.sync_api import Page, expect

def test_recipe_generator_final_version(page: Page):
    """
    This test uses a highly specific CSS selector to target the Streamlit button,
    bypassing potential issues with standard locators that fail on this app.
    """
    
    # 1. Navigate and fill the forms as before
    page.goto("http://localhost:8501/")
    print("AI chef is ready. Starting test...")
    expect(page.get_by_text("AI chef is ready!")).to_be_visible()

    print("Filling in form fields...")
    page.get_by_label("List your available ingredients (comma-separated)").fill("chicken breast, broccoli, rice, garlic, olive oil")
    page.get_by_label("Additional Notes (optional)").fill("make it spicy and quick to prepare")
    print("Forms filled.")

    # 3. Locate and click the button using a direct CSS selector
    # This is the key change to make the script work.
    # It looks for a <button> that contains a <p> with the specific text.
    print("Locating the generate button with a specific CSS selector...")
    generate_button = page.locator("button:has-text('Generate 2-3 Recipes')")

    # We still wait for it to be visible and enabled, which is good practice.
    # A long timeout here ensures the app has time to render the button.
    print("Waiting for the generate button to appear and be enabled...")
    expect(generate_button).to_be_visible(timeout=30000)
    expect(generate_button).to_be_enabled(timeout=30000)
    
    print("Button located. Clicking now.")
    generate_button.click()

    # 4. Wait for the result and print it
    print("\nWaiting for recipe to be generated...")
    result_area = page.locator('section[data-testid="st-main"] .stMarkdown').first
    result_area.wait_for(state="visible", timeout=60000)

    result_text = result_area.text_content()
    print("--- GENERATED RECIPE ---")
    print(result_text)
    print("------------------------")

    # 5. Assert the result to confirm the test worked
    expect(result_area).to_contain_text("Instructions")
    print("\nTest assertion passed: Recipe was generated successfully.")