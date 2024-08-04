import json
from langchain_community.llms import VLLM
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
# from splitter import filter_headings
# from splitter import extract_paragraphs
# from splitter import group_paragraphs_by_headings

def get_conversation_chain():
    llm = VLLM(
        model="baichuan-inc/Baichuan2-13B-Chat",
        trust_remote_code=True,  # mandatory for hf models
        max_new_tokens=4096,
        top_k=20,
        top_p=0.8,
        temperature=0.8,
        dtype="float16",
        tensor_parallel_size=8
    )
    
    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["question"],
        template="""
        Given the question, generate a correct accurate response strictly based on the instruction.

        Question: {question}
        
        Response:
        """
    )
    
    # Create the LLMChain
    conversation_chain = LLMChain(
        llm=llm,
        prompt=prompt_template
    )
    
    return conversation_chain


# Example function to group paragraphs by headings and evaluate them
def group_paragraphs_by_headings(paragraphs, headings, chain):
    grouped_content = {}
    current_heading = None

    for paragraph in paragraphs:
        # Check if the paragraph is a heading
        is_heading = False
        for heading in headings:
            if fuzz.ratio(heading, paragraph) > 80:  # Adjust similarity threshold as needed
                current_heading = heading
                is_heading = True
                if current_heading not in grouped_content:
                    grouped_content[current_heading] = []
                break

        if current_heading and not is_heading and len(paragraph) >= 10:
            paragraph = paragraph
            template_argument_identification = (
                "Evaluate the following paragraph to determine if it contains a conclusion, claim, "
                "or opinion that is substantiated and can contribute to a literature review discussing "
                "the pros and cons of this method. NOTE - Exclude any sections that are purely "
                "methodological or lack substantiation. Be extremely strict with these requirements. "
                "Use the examples provided as a guide. Answer with 'yes' only if confident in its usefulness, "
                "otherwise 'no'. Only respond with 'yes' or 'no' to this paragraph:\n\n" + paragraph +
                "\n\nExamples of valid content: \n1. 'This method significantly improves accuracy compared to previous approaches.'"
                "\n2. 'The technique offers a novel perspective that challenges conventional theories.'"
                "\n\nExamples of invalid content:\n1. 'The methodology involved multiple regression analyses.'"
                "\n2. 'Future research is needed to explore this further.'\n\nAnswer: Respond only with one word answer yes/no."
            )
            response = chain.run(question=template_argument_identification).strip().lower()
            print(response)
            marker = 1 if response == "yes" else 0
            grouped_content[current_heading].append(marker)
        

    return grouped_content


# Initialize the chain
chain = get_conversation_chain()

# Group paragraphs by headings based on similarity check and evaluate
grouped_paragraphs = group_paragraphs_by_headings(paragraphs, filter_headings, chain)

# Convert the grouped content to JSON
grouped_paragraphs_json = json.dumps(grouped_paragraphs, indent=4)

# Print grouped content as JSON
print(grouped_paragraphs_json)




