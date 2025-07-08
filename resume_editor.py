import re

def change_email(latex, new_email):
    return re.sub(r'\\email\{[^\}]*\}', f'\\email{{{new_email}}}', latex)

def change_name(latex, new_name):
    return re.sub(r'\\name\{[^\}]*\}', f'\\name{{{new_name}}}', latex)

def change_location(latex, new_location):
    return re.sub(r'\\location\{[^\}]*\}', f'\\location{{{new_location}}}', latex)

# Add more as needed
