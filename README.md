PromptPilot: Autonomous Prompt Debugger & Optimizer
PromptPilot is a powerful tool for AI prompt engineers to debug, optimize, and test prompts using the free OpenRouter API. Built with a professional Streamlit UI, it analyzes prompt issues, suggests improvements, and provides side-by-side testing with OpenRouter's free-tier models (e.g., LLaMA 3.1 8B Instruct).
Features

Prompt Analysis: Identifies issues like vagueness, lack of context, or missing specificity using chain-of-thought reasoning.
Prompt Optimization: Generates improved prompts with role-based engineering and few-shot learning.
Side-by-Side Testing: Compares original and optimized prompt outputs across multiple iterations using OpenRouter.
Modern UI: Streamlit-based interface with Tailwind CSS for a user-friendly experience.
Extensible: Modular design with support for adding new OpenRouter models and prompt examples.

Installation

Clone the repository:
git clone https://github.com/yourusername/promptpilot.git
cd promptpilot


Install dependencies:
pip install streamlit requests python-dotenv


Set up your OpenRouter API key in a .env file:
OPENROUTER_API_KEY=your_openrouter_api_key


Run the app:
streamlit run app.py



Usage

Open the app in your browser (default: http://localhost:8501).
Paste your prompt in the input box.
Select an OpenRouter model and configure testing options (e.g., iterations, debug mode).
Click "Analyze & Optimize" to view issues, optimized prompt, and side-by-side test results.
Download results as a JSON file for further analysis.

File Structure

app.py: Main Streamlit application with the UI and core logic.
prompt_utils.py: Prompt analysis, optimization, and testing functions.
models_config.py: OpenRouter model configurations and client initialization.
examples/: JSON files with predefined good and bad prompt examples.
README.md: Project documentation.

Notes

Ensure your OpenRouter API key is valid and has access to free-tier models.
The free tier has rate limits, so testing iterations are capped at 3 to avoid exceeding quotas.
Replace YOUR_OPENROUTER_API_KEY in models_config.py or use a .env file for security.

Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub. Ensure your code follows PEP 8 and includes tests where applicable.
License
MIT License. See LICENSE for details.
