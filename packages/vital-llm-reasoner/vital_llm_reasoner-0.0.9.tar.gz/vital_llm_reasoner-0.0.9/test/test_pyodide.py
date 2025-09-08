import asyncio
from playwright.async_api import async_playwright

async def run_python_with_pyodide(code_string):
    async with async_playwright() as p:
        # Launch Chromium in headless mode
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Load Pyodide via CDN using a data URL
        await page.goto(
            'data:text/html,<script src="https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js"></script>'
        )

        # Evaluate the Python code in Pyodide, capturing stdout.
        # We pass the `code_string` as an argument to avoid interpolation issues.
        result = await page.evaluate(
            """async (code) => {
                const pyodide = await loadPyodide();
                try {
                    // Redirect stdout in Pyodide
                    pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
                    `);
                    // Execute the provided Python code
                    pyodide.runPython(code);
                    // Retrieve the stdout content
                    const std_output = pyodide.runPython("sys.stdout.getvalue()");
                    return { success: true, output: std_output };
                } catch (error) {
                    return { success: false, error: error.toString() };
                }
            }""",
            code_string
        )

        await browser.close()
        return result

# Example usage
async def main():
    code = """
sentence = "how many vowels are in this exact sentence?"
vowels = "aeiouAEIOU"
count = 0
for char in sentence:
    if char in vowels:
        count += 1
print(f"Vowel Count: {count}")
"""
    # Run the code in Pyodide and get the result
    result = await run_python_with_pyodide(code)
    if result['success']:
        print("Output from Pyodide:")
        print(result['output'])
    else:
        print("Error in Pyodide:", result['error'])

if __name__ == "__main__":
    asyncio.run(main())
