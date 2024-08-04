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


# %%
# import json
# from fuzzywuzzy import fuzz

# def group_paragraphs_by_headings(paragraphs, headings):
#     grouped_content = {}
#     current_heading = None

#     for paragraph in paragraphs:
#         # Find the closest heading with a high similarity score
#         for heading in headings:
#             if fuzz.ratio(heading, paragraph) > 80:  # Adjust similarity threshold as needed
#                 current_heading = heading
#                 if current_heading not in grouped_content:
#                     grouped_content[current_heading] = []
#                 break

#         if current_heading:
#             grouped_content[current_heading].append(paragraph)

#     return grouped_content

# # Group paragraphs by headings based on similarity check
# grouped_paragraphs = group_paragraphs_by_headings(paragraphs, filtered_headings)

# # Convert the grouped content to JSON
# grouped_paragraphs_json = json.dumps(grouped_paragraphs, indent=4)

# # Print grouped content as JSON
# print(grouped_paragraphs_json)


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