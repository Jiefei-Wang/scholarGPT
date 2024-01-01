from .utils import *
from langchain import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

class Keyword_chain():
    prompt = "Help me to find the search keywords for Google Scholar for the following question. Do not make the search keywords too similar, be creative. Here is an example:"
    examples = [
        "Question: I want to know what databases do ADRD papers use to conduct the research and what is the limitation of the databases. List each paper's title, database used, and the limitation with the databases.",
        "Answer: ADRD study database, Alzheimer's Disease Related Disorders research data, ADRD study data source, Database issues in ADRD research, Data validity in Alzheimer's Disease studies, Alzheimer's research database problems, ADRD data reliability, Data challenges in ADRD studies"
    ]
    QA = QATemplate()
    chain = None
    prompt_template: str = None
    num_keys: int = 10
    llm = None

    def __init__(self, llm, num_keys = 10, prompt = None, examples = None, QA = None):
        self.num_keys = num_keys
        self.llm = llm
        if prompt is not None:
            self.prompt = prompt
        if examples is not None:
            self.examples = examples
        if QA is not None:
            self.QA = QA
        self.make_chain()
        
    def make_chain(self):
        self.prompt_template = list_format(self.prompt, self.examples, self.QA)
        self.chain = (
            {"question": RunnablePassthrough()}|
            PromptTemplate.from_template(self.prompt_template)|
            self.llm
        )

    def invoke(self, question):
        self.make_chain()
        keys = self.chain.invoke(question)
        ## remove .
        key2 = keys.replace(".","")
        ## split the keys
        keys2 = [r.strip() for r in key2.split(",")]
        ## remove all blanks
        keys3 = [r for r in keys2 if r!=""]
        ## limit the total number of keys
        keys4 = keys3[:self.num_keys]
        return keys4

