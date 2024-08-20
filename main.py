# import os
# import re
# import sys
# import spacy
# import json
# from fastapi import FastAPI



# app = FastAPI()

# nlp = spacy.load('en_core_web_sm')  

# def resource_path(relative):
#     if hasattr(sys, "_MEIPASS"):
#         return os.path.join(sys._MEIPASS, relative)
#     return os.path.join(relative)

# # Load the GI dictionary and lemma dictionary
# GI_list = open(resource_path('data_files/inquirerbasic.txt'), 'r').readlines()
# GI_dict = {}

# for line in GI_list:
#     entries = line.split("\t")  # Splits entries in .csv file at tab
#     GI_dict[entries[0]] = set(entries[1:])

# # Create dictionary for lemma list
# lemma_list = open(resource_path('data_files/e_lemma_py_format_lower.txt'), 'r').readlines()
# lemma_dict = {}

# # Creates lemma dictionary, which may or may not be necessary with this database
# for line in lemma_list:
#     if line[0] == '#':
#         continue
#     entries = line.split()
#     for word in entries:
#         lemma_dict[word] = entries[0]

# # Main function to process a list of texts
# def process_text_list(text_list):
#     result = []
#     punctuation = (".", "!", "?", ",", ":", ";", "'", '"')

#     for text in text_list:
#         variable_list = []
#         header_list = ["nwords"]

#         text = re.sub("‘", "'", text)  # Bottom heavy educated quote replaced by straight quotes
#         text = re.sub("’", "'", text)  # Top heavy educated quote replaced by straight quotes
#         nwords = len(text.split())

#         pre_text = text.lower().split()
#         text_2 = []

#         for word in pre_text:
#             if len(word) < 1:
#                 continue
#             if len(word) == 1 and word in punctuation:
#                 continue
#             if word[-1] in punctuation:
#                 word = word[:-1]
#             if word[0] in punctuation:
#                 word = word[1:]
#             text_2.append(word)

#         run_nrc(text_2, variable_list, header_list)

#         result.append({
#             "nwords": nwords,
#             "data": variable_list,
#             "headers": header_list
#         })

#     return json.dumps(result, indent=4)

# # Function to calculate NRC scores
# def run_nrc(text, variable_list, header_list, var=None):
#     if var is None:
#         pos = ""
#     else:
#         pos = var

#     ListDict_counter(GI_dict, 'Anger_NRC', text, "yes", pos, variable_list, header_list)
#     ListDict_counter(GI_dict, 'Anticipation_NRC', text, "yes", pos, variable_list, header_list)
#     ListDict_counter(GI_dict, 'Disgust_NRC', text, "yes", pos, variable_list, header_list)
#     ListDict_counter(GI_dict, 'Fear_NRC', text, "yes", pos, variable_list, header_list)
#     ListDict_counter(GI_dict, 'Joy_NRC', text, "yes", pos, variable_list, header_list)
#     ListDict_counter(GI_dict, 'Negative_NRC', text, "yes", pos, variable_list, header_list)
#     ListDict_counter(GI_dict, 'Positive_NRC', text, "yes", pos, variable_list, header_list)
#     ListDict_counter(GI_dict, 'Sadness_NRC', text, "yes", pos, variable_list, header_list)
#     ListDict_counter(GI_dict, 'Surprise_NRC', text, "yes", pos, variable_list, header_list)
#     ListDict_counter(GI_dict, 'Trust_NRC', text, "yes", pos, variable_list, header_list)

# # Function to count occurrences of words in GI_dict and calculate their frequency
# def ListDict_counter(list_dict, key, in_text, list_flag, pos, variable_list, header_list):
#     counter = 0
#     nwords = len(in_text)

#     for word in in_text:
#         if word in list_dict[key]:
#             counter += 1
#         else:
#             if word in lemma_dict and lemma_dict[word] in list_dict[key]:
#                 counter += 1

#     if list_flag == "yes":
#         variable_list.append(safe_divide(counter, nwords))
#         if pos == "":
#             if "NRC" in key:
#                 key = key.replace("NRC", "EmoLex")
#             header_list.append(key)
#         else:
#             if "NRC" in key:
#                 key = key.replace("NRC", "EmoLex")
#             header_list.append(key + pos)
#     else:
#         return safe_divide(counter, nwords)

# # This function handles safe division to avoid division by zero
# def safe_divide(numerator, denominator):
#     if denominator == 0:
#         index = 0
#     else:
#         index = numerator / denominator
#     return index








# @app.post("/Emotion-Analysis/")
# async def process_texts(text_list: list[str]):
#     output_json = process_text_list(text_list)
#     return json.loads(output_json)

# def test_process_text_list():
#     example_text_list = [
#         "I feel very stressed out.",
#         "I feel happy and joyful today!",
#         "This is a test sentence for processing."
#     ]

#     output_json = process_text_list(example_text_list)

#     output_file_path = "output.json"

#     with open(output_file_path, "w") as json_file:
#         json_file.write(output_json)

#     print("JSON fiel created")

# # Call the function to test
# test_process_text_list()


import os
import re
import sys
import spacy
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

app = FastAPI()

nlp = spacy.load('en_core_web_sm')  

GI_list = open('data_files/inquirerbasic.txt', 'r').readlines() 
GI_dict = {}

for line in GI_list:
    entries = line.split("\t")  # Split each line by tabs into different entries
    GI_dict[entries[0]] = set(entries[1:])  # First entry is the key, rest are values in a set


lemma_list = open('data_files/e_lemma_py_format_lower.txt', 'r').readlines()
lemma_dict = {}

for line in lemma_list:
    if line[0] == '#':  # Skip lines starting with '#' as they are comments
        continue
    entries = line.split()  # Split line by spaces
    for word in entries:
        lemma_dict[word] = entries[0]  # Assign the first word as the lemma for all subsequent words


# Main function to process a list of texts
def process_text_list(text_list):
    result = []
    punctuation = ".!?',:;\""

    for text in text_list:
        variable_list = []
        header_list = ["nwords"]  # Initialize headers with word count

        # Replace both types of smart quotes with straight quotes
        text = re.sub("‘|’", "'", text)  
        nwords = len(text.split())  #


        pre_text = text.lower().split()
        # Remove punctuation from the start and end of each word
        text_2 = [word.strip(punctuation) for word in pre_text if word.strip(punctuation)]

        # Run the NRC emotion analysis
        run_nrc(text_2, variable_list, header_list)

        # Append the result for each text
        result.append({
            "sentence": text,
            "nwords": nwords,
            "data": variable_list,  # Emotion scores
            "headers": header_list  # Emotion categories
        })

    # Convert the result into JSON
    return json.dumps(result, indent=4)

# Function to calculate NRC scores for emotions
def run_nrc(text, variable_list, header_list):
    # List of emotions to analyze using NRC
    emotions = ['Anger_NRC', 'Anticipation_NRC', 'Disgust_NRC', 'Fear_NRC', 'Joy_NRC',
                'Negative_NRC', 'Positive_NRC', 'Sadness_NRC', 'Surprise_NRC', 'Trust_NRC']

    # Calculate frequency of each emotion in the text
    for emotion in emotions:
        ListDict_counter(GI_dict, emotion, text, variable_list, header_list)

# Function to count occurrences of words in GI_dict and calculate their frequency
def ListDict_counter(list_dict, key, in_text, variable_list, header_list):
    # Count how many words in the text match the words in the GI dictionary
    counter = sum(1 for word in in_text if word in list_dict[key] or lemma_dict.get(word) in list_dict[key])

    # Safely divide the count by the number of words to get frequency
    variable_list.append(safe_divide(counter, len(in_text)))

    if "NRC" in key:
        key = key.replace("NRC", "EmoLex")
    header_list.append(key)

def safe_divide(numerator, denominator):
    # If denominator is zero, return 0 to avoid division error
    return numerator / denominator if denominator != 0 else 0



# *********************************************************************************************** #

# # FastAPI endpoint
# @app.post("/Emotion-Analysis/")
# async def process_texts(text_list: list[str]):
#     output_json = process_text_list(text_list)  # Process the input text list
#     return json.loads(output_json)  # Return the JSON response

@app.post("/Emotion-Analysis/")
async def process_texts(request: Request):
    try:
        data = await request.json()
        text_list = data.get("text_list", [])
        output_json = process_text_list(text_list)
        return JSONResponse(content=json.loads(output_json))
    except ValidationError as e:
        return JSONResponse(status_code=422, content={"detail": e.errors()})

# Test function
def test_process_text_list():
    example_text_list = [
        "I feel very stressed out.",
        "I feel happy and joyful today!",
        "This is a test sentence for processing."
    ]

    output_json = process_text_list(example_text_list)

    output_file_path = "output.json"
    with open(output_file_path, "w") as json_file:
        json_file.write(output_json)

    print("JSON file created")


test_process_text_list()

# *********************************************************************************************** #