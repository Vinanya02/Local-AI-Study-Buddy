# Fixed Local AI Study Buddy (Streamlit + Ollama)
import streamlit as st
import ollama
import logging

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Local AI Study Buddy",
    page_icon="🎓",
    layout="wide"
)

# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# GET AVAILABLE OLLAMA MODELS
# ---------------------------------------------------
@st.cache_data

def get_available_models():
    try:
        models_response = ollama.list()
        model_names = []

        # New Ollama API format
        if hasattr(models_response, "models"):
            for model in models_response.models:
                if hasattr(model, "model"):
                    model_names.append(model.model)

        # Remove duplicates
        model_names = list(set(model_names))

        # Sort models
        preferred_order = [
            "gemma3",
            "gemma3:latest",
            "llama3",
            "mistral",
            "deepseek-coder"
        ]

        ordered_models = []

        # Add preferred models first
        for preferred in preferred_order:
            for model in model_names:
                if preferred.lower() in model.lower() and model not in ordered_models:
                    ordered_models.append(model)

        # Add remaining models
        for model in model_names:
            if model not in ordered_models:
                ordered_models.append(model)

        return ordered_models

    except Exception as e:
        logger.error(f"Ollama Error: {e}")
        st.error(f"⚠️ Cannot connect to Ollama: {e}")
        st.info("Run this command in terminal: ollama serve")
        return []

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------
st.title("🎓 Local AI Study Buddy")
st.caption("Private AI Tutor powered by Ollama + Gemma3")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:

    st.header("🎯 Learning Preferences")

    education_level = st.selectbox(
        "Select your education level",
        ["School", "High School", "Graduate", "PG/PhD"],
        index=1
    )

    subject = st.selectbox(
        "Choose a subject",
        [
            "Computer Science",
            "Math",
            "Physics",
            "Chemistry",
            "Biology",
            "History"
        ],
        index=0
    )

    mode = st.radio(
        "Select mode",
        ["Explain a Topic", "Generate a Quiz"]
    )

    st.markdown("---")

    # Load available models
    available_models = get_available_models()

    if available_models:

        model_name = st.selectbox(
            "AI Model",
            available_models,
            index=0
        )

        if "gemma3" in model_name.lower():
            st.success("✅ Gemma3 detected")

    else:

        model_name = None

        st.error("⚠️ No Ollama models found")

        st.markdown("### Install Gemma3")

        st.code("ollama pull gemma3", language="bash")

        st.markdown("### Start Ollama Server")

        st.code("ollama serve", language="bash")

    st.markdown("---")

    st.success("🔒 100% Local & Private")

# ---------------------------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------
# USER INPUT
# ---------------------------------------------------
prompt = st.chat_input(f"Ask a {subject} question...")

if prompt:

    if not model_name:
        st.stop()

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):

        message_placeholder = st.empty()
        full_response = ""

        # ---------------------------------------------------
        # CUSTOM PROMPTS
        # ---------------------------------------------------
        if mode == "Explain a Topic":

            custom_prompt = f"""
You are an expert {subject} tutor.

Teach at {education_level} level.

Explain this topic clearly and step-by-step:

{prompt}

Rules:
- Use simple language
- Use examples
- Keep explanation structured
- Avoid unnecessary complexity
"""

        else:

            custom_prompt = f"""
Create a {education_level}-level quiz for {subject}.

Topic: {prompt}

Requirements:
- 1 MCQ question
- 4 options (A, B, C, D)
- Mark correct answer
- Give short explanation
"""

        # ---------------------------------------------------
        # OLLAMA RESPONSE
        # ---------------------------------------------------
        try:

            stream = ollama.chat(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": custom_prompt
                    }
                ],
                stream=True
            )

            for chunk in stream:

                if "message" in chunk:
                    content = chunk["message"]["content"]
                    full_response += content

                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:

            error_message = f"❌ Error: {str(e)}"

            logger.error(error_message)

            message_placeholder.error(error_message)

            full_response = error_message

    # Store assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })

