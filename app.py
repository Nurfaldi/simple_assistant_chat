import streamlit as st
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# Set page config
st.set_page_config(page_title="Minerba GPT", page_icon="🤖")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = None
if "assistant" not in st.session_state:
    st.session_state.assistant = None

# API configuration
api_key = OPENAI_API_KEY
assistant_id = OPENAI_ASSISTANT_ID
    
try:
    # Initialize OpenAI client
    st.session_state.client = OpenAI(api_key=api_key)
    # Retrieve assistant
    st.session_state.assistant = st.session_state.client.beta.assistants.retrieve(assistant_id)
    # st.success("Assistant initialized successfully!")
except Exception as e:
    st.error(f"Error initializing assistant: {str(e)}")

# Main chat interface
st.title("⛏️ Minerba GPT")
# st.caption("🚀")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and processing
if prompt := st.chat_input("What's up?"):
    # Check if assistant is initialized
    if not st.session_state.client or not st.session_state.assistant:
        st.error("Please initialize the assistant in the sidebar first")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Create assistant response
    def get_assistant_response(question):
        try:
            # Create a thread
            thread = st.session_state.client.beta.threads.create()
            
            # Add message to thread
            st.session_state.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=question
            )
            
            # Create run
            run = st.session_state.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=st.session_state.assistant.id
            )
            
            # Wait for completion
            while run.status != "completed":
                time.sleep(0.5)
                run = st.session_state.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            # Get messages
            messages = st.session_state.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            return messages.data[0].content[0].text.value
        
        except Exception as e:
            return f"Error: {str(e)}"

    # Generate response
    response = get_assistant_response(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})