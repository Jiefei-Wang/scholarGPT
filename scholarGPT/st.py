import os

import streamlit as st
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback


from scholarGPT import Keyword_chain
from scholarGPT import Search_chain
from scholarGPT import Search_engine_crossref
from scholarGPT import Answer_chain

class Progress():
    tokens = 0
    cost = 0
    widget = None
    messages = []
    def __init__(self, widget):
        self.widget = widget

    def push_message(self, message):
        self.messages = message
        self.widget.markdown(f"Cost: {self.cost},  Tokens: {self.tokens}:  {message}", unsafe_allow_html=True)
    
    def push_temp_message(self, message):
        self.push_message(message)

    def push_cost(self, cost, tokens):
        self.cost += cost
        self.tokens += tokens
        self.widget.markdown(f"Cost: {self.cost},  Tokens: {self.tokens}:  {self.messages}", unsafe_allow_html=True)
    
    def show(self):
        msg = "<br/>".join(self.messages)
        self.widget.markdown(f"Cost: {self.cost}<br/> Tokens: {self.tokens}:  {msg}", unsafe_allow_html=True)
    


def format_message(progress_message, cost, tokens, *messages):
    messages = [f"{i+1}. {m}" for i, m in enumerate(messages)]
    messages = "<br/>".join(messages)
    progress_message.markdown(f"Cost: {cost}, Tokens: {tokens}<br/>{messages}", unsafe_allow_html=True)






# Function to generate a dataframe for demonstration purposes
def generate_data(question):
    progress = st.session_state.progress
    if question == "":
        return ""
    llm = st.session_state['llm']

    cost = 0
    tokens = 0

    progress.push_temp_message("Generating keywords...")
    search_chain = Keyword_chain(llm)
    with get_openai_callback() as cb:
        keys = search_chain.invoke(question)
    progress.push_cost(cost, tokens)
    keyword_msg = f"Total keywords: {len(keys)} (" + ", ".join(keys[:2]) + "...)"
    progress.push_message(keyword_msg)
    
    progress.push_temp_message("Searching publications...")
    search_engine = st.session_state['search_engine']
    search_chain = Search_chain(search_engine, total_num_search=st.session_state['max_search_number'])
    search_results = search_chain.invoke(keys)
    search_msg = f"Search results: {len(search_results)}"
    progress.push_message(search_msg)
    
    progress.push_temp_message("Generating answers...")
    answer_chain = Answer_chain(llm)
    with get_openai_callback() as cb:
        answers = answer_chain.invoke(search_results, question)
        progress.push_cost(cost, tokens)
    answer_msg = f"Total answers: {len(answers)}"
    progress.push_message(answer_msg)
    
    ## sort answers by score
    answers = sorted(answers, key=lambda k: k['score'], reverse=True)

    ## create a user readable output
    output = [f"1. **{r['title']}**<br/><br/>{r['summary']}" for r in answers]
    output = "\n\n".join(output)
    return output



answer_box = st.markdown("", unsafe_allow_html=True)
st.session_state.answer_box = answer_box

user_input = st.chat_input(placeholder="What's in your mind today?")


progress = Progress(answer_box)
st.session_state.progress = progress

if user_input:
    answers = generate_data(user_input)
    answer_box.markdown(answers, unsafe_allow_html=True)


# Sidebar options (you can move these inside columns if you prefer)
st.sidebar.write("Model option")
max_search_each_key = st.sidebar.number_input("Max search each keyword", value=100, step=1)
max_search_number = st.sidebar.number_input("Max search number", value=10, step=1)
search_engine = st.sidebar.selectbox("Search Engine", ["CrossRef"])
language_engine = st.sidebar.selectbox("Language Engine", ["LM Studio","OpenAI"])



if language_engine == "OpenAI":
    api_key = st.sidebar.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY"))
    model_name = st.sidebar.text_input("model", value="gpt-3.5-turbo-instruct")
    temperature = st.sidebar.slider("temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
    if api_key != None and api_key != "":
        llm = OpenAI(temperature=temperature,model=model_name, openai_api_key=api_key)
        st.session_state['llm'] = llm

if language_engine == "LM Studio":
    url = st.sidebar.text_input("url", value="http://localhost:1234/v1")
    temperature = st.sidebar.slider("temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
    llm = OpenAI(temperature=temperature,
                openai_api_key="not-needed", 
                base_url=url)
    st.session_state['llm'] = llm


if search_engine == "CrossRef":
    st.session_state['search_engine'] = Search_engine_crossref(max_search_each_key)


st.session_state['max_search_number'] = max_search_number