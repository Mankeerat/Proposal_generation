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
    
    # Template for the prompt
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

# Example usage
paragraph_updated_argument_contained = ""
prompt_extraction = extract_crucial_conclusions(paragraph_updated_argument_contained)
print(prompt_extraction)


response_argument_extraction = chain.run(question=prompt_extraction)
print(response_argument_extraction)