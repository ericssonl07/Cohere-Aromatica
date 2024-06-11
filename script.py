import streamlit as st # Streamlit library
import cohere # Cohere chat API
import rag # RAG text extraction function; file rag.py
import instructions # Strings to guide the chatbot; file instructions.py
import os # Access and manipulate file and directory names and paths

# API key management
api_key_found = False
if hasattr(st, "secrets"):
    if "COHERE_API_KEY" in st.secrets.keys():
        if st.secrets["COHERE_API_KEY"] not in ["", "PASTE YOUR API KEY HERE"]:
            api_key_found = True

# Sidebar with API key input and reference upload
with st.sidebar:
    if api_key_found:
        cohere_api_key = st.secrets["COHERE_API_KEY"]
    else:
        cohere_api_key = st.text_input("Cohere API Key",
                                       key = "chatbot_api_key",
                                       type = "password")
        st.markdown("[Get a Cohere API Key](https://dashboard.cohere.ai/api-keys)")
    uploaded_files = st.file_uploader("Upload your organic chemistry reference here", 
                                    accept_multiple_files = True)

# Writing files to a temporary directory to facilitate usage with PyPDF2
for i in range(len(uploaded_files)):
    bytes_data = uploaded_files[i].read()
    with open(os.path.join("/tmp", uploaded_files[i].name), "wb") as f:
        f.write(bytes_data)

# Cohere Client
co = cohere.Client(api_key = cohere_api_key)

# Cohere Aromatica- mimicking Wolfram Mathematica's naming style, referencing aromatic compounds
st.title("Cohere Aromatica")

# Check if messages exist; if not, fill with the introduction message
if "messages" not in st.session_state:
    st.session_state.messages = [{'role': "Cohere", 
                                  "content": instructions.organic_chemistry_introduction}]

# Reconstruct chat history based on st.session_state.messages
chat_history = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    if message["role"] == "User":
        chat_history.append({'role': "USER", "message": message["content"]})
    else:
        chat_history.append({'role': "CHATBOT", "message": message["content"]})

# Check if a prompt has been given
if prompt := st.chat_input("Chat with Cohere"):
    # Throw an error if no reference files are given
    if uploaded_files is None:
        st.error("Please upload your organic chemistry reference first.")
        st.stop()
    
    # Display the user's query
    with st.chat_message("User"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "User", "content": prompt})

    # Overwritable placeholder to enable response streaming
    response_placeholder = st.empty()
    # Show a status message
    response_placeholder.write("Parsing documents...", unsafe_allow_html = True)

    # Initialize a chat stream response
    response_stream = co.chat_stream(message = prompt, # User's query
                                     preamble = instructions.organic_chemistry_instructions, # Prompt engineering
                                     documents = rag.extract_ranked_citations(client = co,
                                                                              source = '/tmp',
                                                                              query = prompt,
                                                                              model = 'rerank-english-v3.0',
                                                                              n_results = 10), # Relevant information
                                     chat_history = chat_history)
    
    # Initialize an empty response string; response will be written to the placeholder.
    response = ""
    # Iterate through the response stream, accessing events as they become available
    for event in response_stream:
        # Show all generated text
        if event.event_type == 'text-generation':
            response += event.text
            response_placeholder.write(response, unsafe_allow_html = True)
    # Update the history
    st.session_state.messages.append({"role": "Cohere", "content": response})