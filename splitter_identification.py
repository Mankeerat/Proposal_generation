# %%
import fitz
import re

def extract_paragraphs(pdf_path):
    doc = fitz.open(pdf_path)
    paragraphs = []

    for page in doc:
        blocks = page.get_text("blocks")
        for block in blocks:
            text = block[4].strip()
            if text:  # Check if the block is not empty
                paragraphs.append(text)

    return paragraphs

def extract_headings(paragraphs, regex_pattern):
    headings = []
    pattern = re.compile(regex_pattern)

    for paragraph in paragraphs:
        if pattern.match(paragraph):
            headings.append(paragraph)

    return headings

# Extract paragraphs from the PDF
paragraphs = extract_paragraphs("/home/ubuntu/agent_testing/Report_generator/bertscore.pdf")

# Define your regex pattern for headings
# Example pattern: Assume headings start with one or more uppercase letters followed by a space
regex_pattern = r'\b(\d+(\.\d+)?|[IVXLCDM]+\.?|[A-Z]\.?)\s+([A-Z]+[a-zA-Z]*\s*)*[A-Z]+[a-zA-Z]*\b'

# Extract headings that match the regex pattern
headings = extract_headings(paragraphs, regex_pattern)

print(headings)

# %%
def filter_headings(headings, max_words=5):
    filtered_headings = [heading for heading in headings if len(heading.split()) <= max_words]
    return filtered_headings

# Filter headings to only include those with 6 words or fewer
filtered_headings = filter_headings(headings, max_words=6)

print(filtered_headings)


import json
from fuzzywuzzy import fuzz

def group_paragraphs_by_headings(paragraphs, headings):
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

        # Add the paragraph to the current heading if it is not a heading and has 10 or more characters
        if current_heading and not is_heading and len(paragraph) >= 10:
            grouped_content[current_heading].append(paragraph)

    return grouped_content



# Group paragraphs by headings based on similarity check
grouped_paragraphs = group_paragraphs_by_headings(paragraphs, filtered_headings)

# Convert the grouped content to JSON
grouped_paragraphs_json = json.dumps(grouped_paragraphs, indent=4)

# Print grouped content as JSON
print(grouped_paragraphs_json)



#%%
# Define the filename
filename = "/home/ubuntu/agent_testing/Report_generator/grouped_paragraphs.json"

# Write the JSON data to a file
with open(filename, "w") as file:
    file.write(grouped_paragraphs_json)

print(f"Data has been written to {filename}")



#%%
from langchain_community.llms import VLLM
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

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
            marker = 1 if "yes" in response else 0
            grouped_content[current_heading].append(marker)
        

    return grouped_content


# Initialize the chain
chain = get_conversation_chain()

# Group paragraphs by headings based on similarity check and evaluate
grouped_paragraphs = group_paragraphs_by_headings(paragraphs, filtered_headings, chain)

# Convert the grouped content to JSON
selected_paragraphs = json.dumps(grouped_paragraphs, indent=4)

# Print grouped content as JSON
print(grouped_paragraphs_json)





# %%
# Create a new dictionary with selected paragraphs
selected_paragraphs_dict = {}

# Iterate through the keys of the dictionaries
for key in grouped_paragraphs:
    # Get the list of paragraphs and selection markers
    paragraphs = grouped_paragraphs[key]
    selection = selected_paragraphs[key]

    # Filter paragraphs based on selection markers
    selected_paragraphs = [paragraph for paragraph, marker in zip(paragraphs, selection) if marker == 1]

    # Add the selected paragraphs to the new dictionary
    selected_paragraphs_dict[key] = selected_paragraphs

# Print the selected paragraphs dictionary
identified_paragraphs = json.dumps(selected_paragraphs_dict, indent=4)



# %%

def extract_crucial_conclusions(paragraph):
    # Define the valid and invalid examples
    valid_examples = [
        "This method significantly improves accuracy compared to previous approaches.",
        "The technique offers a novel perspective that challenges conventional theories."
    ]
    
    invalid_examples = [
        "The methodology involved multiple regression analyses.",
        "Future research is needed to explore this further."
    ]
    
    prompt_template = """
    Extract the crucial conclusions, claims, or substantiated opinions from the following paragraph. These should be statements that significantly contribute to a literature review discussing the pros and cons of the method in question. Only extract content that is clearly substantiated and provides valuable insights into the method's effectiveness, novelty, or theoretical implications. Exclude any content that is purely methodological or lacks strong support. Do not add any information of your own; only extract from the provided content.

    Paragraph:
    {}

    Examples of crucial conclusions and claims to extract:
    1. {}
    2. {}

    Examples of content to exclude:
    1. {}
    2. {}

    Extracted Crucial Conclusions and Claims:
    """.format(paragraph, valid_examples[0], valid_examples[1], invalid_examples[0], invalid_examples[1])

    return prompt_template


# Example function to group paragraphs by headings and evaluate them
def group_identified_paragraphs(identified_paragraphs, headings, chain):
    grouped_identified_content = {}
    current_identified_heading = None

    for paragraph in identified_paragraphs:
        # Check if the paragraph is a heading
        is_heading = False
        for heading in headings:
            if fuzz.ratio(heading, paragraph) > 80:  # Adjust similarity threshold as needed
                current_identified_heading = heading
                is_heading = True
                if current_identified_heading not in grouped_identified_content:
                    grouped_identified_content[current_identified_heading] = []
                break

        if current_identified_heading and not is_heading and len(paragraph) >= 10:
            paragraph = paragraph
            prompt_extraction = extract_crucial_conclusions(paragraph)
            response = chain.run(question=prompt_extraction).strip().lower()
            print(response)
            grouped_identified_content[current_identified_heading].append(response)
        

    return grouped_identified_content


# Group paragraphs by headings based on similarity check and evaluate
grouped_extracted_paragraphs_final = group_identified_paragraphs(identified_paragraphs, filtered_headings, chain)

# Convert the grouped content to JSON
selected_extracted_paragraphs = json.dumps(grouped_extracted_paragraphs_final, indent=4)

# Print grouped content as JSON
print(grouped_extracted_paragraphs_final)




