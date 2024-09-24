import spacy
import re
import json

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
        header_list = []  # Initialize headers with word count

        # Replace both types of quotes with straight quotes
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
                'Sadness_NRC', 'Surprise_NRC', 'Trust_NRC'] # ,'Negative_NRC', 'Positive_NRC'

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
        key = key.replace("_NRC", "")
    header_list.append(key)

def safe_divide(numerator, denominator):
    # If denominator is zero, return 0 to avoid division error
    return numerator / denominator if denominator != 0 else 0