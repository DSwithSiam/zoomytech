import re

def remove_extra_c(text):
    cleaned_text = re.sub(r'(\*\*|#{2,})', '', text)
    return cleaned_text