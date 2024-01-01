from .utils import *
from langchain import PromptTemplate
import json

class Answer_chain:
    llm = None

    prompt = """Here are the paper title and abstract. Please read them and give a summary. Your summary should contain information related to the questions asked by the user. If none of the questions can be answered, you can give an empty summary. Your summary should be one paragraph and in JSON format. You do not need to include the paper title in your summary even if the user's question requests you to do so. You also need to give a score to evaluate how relevant this paper is to the questions. The score should be 0-5 where 0 means not relevant at all and 5 means very relevant. Here are some examples."""
    
    question = "Question: I want to know what databases ADRD papers use to conduct the research and what are the limitations of the databases. List each paper's title, the database used, and the limitations of the databases."
    example1 = [
        "Example 1:"
        "Title: Attention Is All You Need",
        "Abstract: We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        question,
        """Answer: {{\n"summary": "",\n"score": 0\n}}"""
    ]
    example2 = [
        "Example 2:"
        "Title: The disproportionate burden of Alzheimer's disease and related dementias (ADRD) in diverse older adults diagnosed with cancer",
        """Abstract: This study investigates the impact of cancer in older adults (aged 68+) with Alzheimer's and related dementias (ADRD), an under-researched group. Utilizing the SEER-Medicare database, it analyzes the prevalence of ADRD in patients with six primary cancer types (breast, cervical, colorectal, lung, oral, prostate) among 337,932 individuals, comparing it with a 5% non-cancer sample. The goal is to enhance our understanding of this vulnerable population's needs.""",
        question,
        """Answer: {{\n"summary": "The study used the SEER-Medicare database, which combines cancer registry data with Medicare administrative claims. However, the abstract does not explicitly mention the limitations of the SEER-Medicare database.",\n"score": 2\n}}"""
    ]
    example3 = [
        "Example 3:"
        "Title: Participatory Research Approaches in Alzheimer’s Disease and Related Dementias Literature: A Scoping Review",
        """Abstract:This scoping review examines the participatory research approaches in Alzheimer's disease and related dementias (ADRD) literature. A systematic search across CINAHL, SCOPUS, PsycInfo, and PubMed databases identified 163 English-language, peer-reviewed studies employing participatory methods in ADRD research from 1990 to 2022. Our analysis focused on terminology, application, and extent of nonacademic partnerships. Limitations include the English-language focus and the criterion for explicit mention of participatory terms, potentially omitting relevant studies not using specific terminologies or published outside peer-reviewed channels.""",
        question,
        """Answer: {{\n"summary": "The study systematically searched four multidisciplinary databases: CINAHL, SCOPUS, PsycInfo, and PubMed, analyzing 163 studies from 1990 to 2022. Limitations include a focus on English-language literature, potentially overlooking non-English studies, and the exclusion of studies not explicitly mentioning participatory methods in key sections of their publications.",  \n"relevance_score": 5\n}}"""   
        ]
    
    QA = [
        'Title:{title}',
        'Abstract:{abstract}',
        'Question: {question}',
        'answer:'
        ]


    prompt_template = None
    chain = None

    def __init__(self, llm):
        self.llm = llm
        self.prompt_template = list_format(self.prompt, self.example1,self.example2, self.example3, self.QA)
        self.chain = (
            {"title": lambda x: x["title"],
             "abstract": lambda x: x["abstract"],
             "question": lambda x: x["question"]}|
            PromptTemplate.from_template(self.prompt_template)|
            llm
        )
    
    
    def invoke(self, search_results, question):
        combo = [{"title":r["title"], "abstract":r["abstract"], "question":question} for r in search_results]
        result = [self.chain.invoke(c) for c in combo]
        result_json = []
        for r in result:
            try:
                r_json = json.loads(r)
                if "summary" not in r_json:
                    r_json["summary"] = ""
                if "score" not in r_json:
                    r_json["score"] = 0
                result_json.append(r_json)
            except:
                result_json.append({"summary":"", "score":0})

        result_all = [{"title":search_results[i]["title"], 
                       "abstract":search_results[i]["abstract"], 
                       "summary":r["summary"], 
                       "score":r["score"]} for i,r in enumerate(result_json)]
        return result_all

