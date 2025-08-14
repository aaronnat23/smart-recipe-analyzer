// tests/recipe-generator.spec.js

const { test, expect } = require('@playwright/test');

test('should generate a recipe and print the result', async ({ page }) => {

  // 1. Navigate to your web application
  // Streamlit apps usually run on localhost port 8501 by default.
  // Replace this with the actual URL if it's different.
  await page.goto('http://localhost:8501');

  // 2. Input the ingredients
  // We'll find the text area by its label, which is very reliable.
  const ingredientsInput = page.getByLabel('List your available ingredients (comma-separated)');

  // The text to input into the ingredients field.
  const ingredientsText = 'dough (flour, yeast, water, salt, olive oil), tomato sauce, and mozzarella cheese';
  
  // Fill the input field with our ingredients.
  await ingredientsInput.fill(ingredientsText);

  // 3. Click the "Generate" button
  // We'll find the button by its role and visible text.
  const generateButton = page.getByRole('button', { name: 'Generate 2-3 Recipes' });
  await generateButton.click();

  // 4. Wait for the response and print it
  // After clicking the button, the app will process and display the recipes.
  // We need to wait for the results to appear. Results in Streamlit are often
  // inside a generic container. We will wait for a new element to appear
  // that contains the text "Recipe".
  console.log('\nWaiting for recipe to be generated...');

  // We will wait up to 30 seconds for an element containing the recipe to appear.
  // This locator looks for the main part of the page and then finds the first
  // visible markdown element inside it. This is a common pattern for Streamlit output.
  const resultArea = page.locator('section[data-testid="st-main"] .stMarkdown').first();
  
  // Wait for the element to be visible, with a longer timeout for the AI response.
  await resultArea.waitFor({ state: 'visible', timeout: 30000 }); 

  // Retrieve all the text content from the result area.
  const resultText = await resultArea.textContent();

  // Print the retrieved text to your terminal for verification.
  console.log('--- GENERATED RECIPE ---');
  console.log(resultText);
  console.log('------------------------');

  // (Optional but highly recommended) Add an assertion to verify the result.
  // This confirms the test passed automatically. For example, check if the
  // word "Instructions" is present in the output.
  await expect(resultArea).toContainText('Instructions');
});