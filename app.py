import streamlit as st
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Fetch values from environment variables or Streamlit secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID") or st.secrets.get("OPENAI_ASSISTANT_ID")

# Set page config
st.set_page_config(page_title="Minerba AI", page_icon="🤖")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = None
if "assistant" not in st.session_state:
    st.session_state.assistant = None
if "thread" not in st.session_state:  # Add thread to session state
    st.session_state.thread = None

# API configuration
api_key = OPENAI_API_KEY
assistant_id = OPENAI_ASSISTANT_ID
    
try:
    # Initialize OpenAI client
    st.session_state.client = OpenAI(api_key=api_key)
    # Retrieve assistant
    st.session_state.assistant = st.session_state.client.beta.assistants.retrieve(assistant_id)
    print("Debug: Assistant initialized successfully")  # Debug log
except Exception as e:
    st.error(f"Error initializing assistant: {str(e)}")

# Main chat interface
st.title("⛏️ Minerba AI")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and processing
if prompt := st.chat_input("What's up?"):
    # Check if assistant is initialized
    if not st.session_state.client or not st.session_state.assistant:
        st.error("Please initialize the assistant first")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Create assistant response
    def get_assistant_response(question):
        try:
            # Create thread if not exists
            if not st.session_state.thread:
                st.session_state.thread = st.session_state.client.beta.threads.create()
                print(f"Debug: Created new thread - {st.session_state.thread.id}")  # Debug log
            
            # Add message to existing thread
            st.session_state.client.beta.threads.messages.create(
                thread_id=st.session_state.thread.id,
                role="user",
                content=question
            )
            print(f"Debug: Added message to thread - {st.session_state.thread.id}")  # Debug log
            
            # Create run
            run = st.session_state.client.beta.threads.runs.create(
                thread_id=st.session_state.thread.id,
                assistant_id=st.session_state.assistant.id
            )
            print(f"Debug: Created run - {run.id}")  # Debug log
            
            # Wait for completion with status updates
            while run.status != "completed":
                time.sleep(0.5)
                run = st.session_state.client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread.id,
                    run_id=run.id
                )
                print(f"Debug: Run status - {run.status}")  # Debug log
                if run.status == "failed":
                    st.error("Run failed, check the OpenAI dashboard for details")
                    return "Error: Run failed"
            
            # Get messages
            messages = st.session_state.client.beta.threads.messages.list(
                thread_id=st.session_state.thread.id
            )
            print(f"Debug: Retrieved {len(messages.data)} messages")  # Debug log
            
            return messages.data[0].content[0].text.value
        
        except Exception as e:
            print(f"Error: {str(e)}")  # Error log
            return f"Error: {str(e)}"

    # Generate response
    response = get_assistant_response(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})