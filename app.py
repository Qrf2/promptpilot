import streamlit as st
import prompt_utils as pu
import models_config as mc
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Streamlit page configuration
st.set_page_config(
    page_title="PromptPilot: Autonomous Prompt Debugger & Optimizer",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    """Main function to run the PromptPilot Streamlit app."""
    # Custom CSS for Tailwind-like styling
    st.markdown("""
        <style>
        @import url('https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css');
        .main-header { @apply text-4xl font-bold text-gray-800 mb-6; }
        .sub-header { @apply text-2xl font-semibold text-gray-700 mb-4; }
        .card { @apply bg-white p-6 rounded-lg shadow-md mb-4; }
        .button { @apply bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600; }
        .input-box { @apply border border-gray-300 p-2 rounded w-full mb-4; }
        .sidebar-section { @apply mb-6; }
        .result-box { @apply bg-gray-100 p-4 rounded-lg mb-4; }
        </style>
    """, unsafe_allow_html=True)

    # Validate API key
    try:
        api_valid = mc.validate_api_keys()
        if not api_valid:
            st.error("Invalid or missing OpenRouter API key. Please ensure it is set correctly in the `.env` file.")
            st.markdown("1. Verify your API key in `promptpilot/.env`: `OPENROUTER_API_KEY=sk-or-v1-...`")
            st.markdown("2. Get a free key from [OpenRouter](https://openrouter.ai/keys).")
            st.markdown("3. Restart the app after updating the `.env` file.")
            return
    except Exception as e:
        st.error(f"Failed to validate OpenRouter API key: {str(e)}")
        st.markdown("Check your API key and internet connection, then restart the app.")
        logger.error(f"API key validation error: {str(e)}")
        return

    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="sub-header">PromptPilot Controls</h2>', unsafe_allow_html=True)
        model_choice = st.selectbox(
            "Select OpenRouter Model",
            list(mc.MODEL_CONFIG.keys()),
            help="Choose the OpenRouter model to test your prompts."
        )
        debug_mode = st.checkbox("Enable Debug Mode", value=False, help="Show detailed analysis steps.")
        test_iterations = st.slider(
            "Test Iterations", 1, 3, 1, help="Number of test runs (limited for free tier)."
        )
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.info("Paste your prompt, analyze issues, and get optimized versions with side-by-side testing using OpenRouter.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Main content
    st.markdown('<h1 class="main-header">PromptPilot: Debug & Optimize Your AI Prompts</h1>', unsafe_allow_html=True)
    st.markdown("Paste your prompt, and let PromptPilot analyze, optimize, and test it using OpenRouter's free models.", unsafe_allow_html=True)

    # Input section
    col1, col2 = st.columns([3, 1])
    with col1:
        user_prompt = st.text_area(
            "Enter Your Prompt",
            height=150,
            placeholder="e.g., 'Write a story about a dragon' or 'Summarize this text: ...'",
            help="Input the prompt you want to debug and optimize.",
            key="prompt_input"
        )
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if st.button("Analyze & Optimize", key="analyze_button", help="Start the analysis and optimization process"):
            if not user_prompt:
                st.error("Please enter a prompt to analyze.")
            else:
                with st.spinner("Analyzing prompt..."):
                    try:
                        # Analyze the prompt
                        analysis = pu.analyze_prompt(user_prompt)
                        logger.info(f"Prompt analysis completed: {analysis['issues']}")

                        # Optimize the prompt
                        optimized_prompt = pu.optimize_prompt(user_prompt, analysis)
                        logger.info("Prompt optimization completed.")

                        # Store results in session state
                        st.session_state['analysis'] = analysis
                        st.session_state['optimized_prompt'] = optimized_prompt
                        st.session_state['original_prompt'] = user_prompt

                    except Exception as e:
                        logger.error(f"Error during analysis: {str(e)}")
                        st.error(f"Error analyzing prompt: {str(e)}")

    # Display results if available
    if 'analysis' in st.session_state and 'optimized_prompt' in st.session_state:
        st.markdown('<h2 class="sub-header">Analysis Results</h2>', unsafe_allow_html=True)
        with st.expander("View Detailed Analysis", expanded=debug_mode):
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.json(st.session_state['analysis'])
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<h2 class="sub-header">Optimized Prompt</h2>', unsafe_allow_html=True)
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.write(st.session_state['optimized_prompt'])
        st.markdown('</div>', unsafe_allow_html=True)

        # Side-by-side testing
        st.markdown('<h2 class="sub-header">Side-by-Side Testing</h2>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        original_output = "Failed to generate output due to API error."
        optimized_output = "Failed to generate output due to API error."

        with col3:
            st.markdown('<h3>Original Prompt Output</h3>', unsafe_allow_html=True)
            with st.spinner("Running original prompt..."):
                try:
                    original_output = pu.test_prompt(
                        st.session_state['original_prompt'],
                        model_choice,
                        test_iterations
                    )
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.write(original_output)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    logger.error(f"Error testing original prompt: {str(e)}")
                    st.error(f"Error testing original prompt: {str(e)}")
                    original_output = f"Error: {str(e)}"

        with col4:
            st.markdown('<h3>Optimized Prompt Output</h3>', unsafe_allow_html=True)
            with st.spinner("Running optimized prompt..."):
                try:
                    optimized_output = pu.test_prompt(
                        st.session_state['optimized_prompt'],
                        model_choice,
                        test_iterations
                    )
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.write(optimized_output)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    logger.error(f"Error testing optimized prompt: {str(e)}")
                    st.error(f"Error testing optimized prompt: {str(e)}")
                    optimized_output = f"Error: {str(e)}"

        # Download results
        results = {
            "timestamp": datetime.now().isoformat(),
            "original_prompt": st.session_state['original_prompt'],
            "analysis": st.session_state['analysis'],
            "optimized_prompt": st.session_state['optimized_prompt'],
            "original_output": original_output,
            "optimized_output": optimized_output
        }
        st.download_button(
            label="Download Results",
            data=json.dumps(results, indent=2),
            file_name=f"promptpilot_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key="download_button"
        )

if __name__ == "__main__":
    main()