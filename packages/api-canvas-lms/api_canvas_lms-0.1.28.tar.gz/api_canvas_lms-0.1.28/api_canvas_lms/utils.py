""" 
Programa : Utils module for Canvas
Fecha Creacion : 07/08/2024
Fecha Update : None
Version : 1.0.0
Actualizacion : None
Author : Jaime Gomez
"""

import logging

import re
import unicodedata
import pandas as pd

# Create a logger for this module
logger = logging.getLogger(__name__)

# Function to clean HTML tags from the text
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def remove_tilde(text):
    # Normalize the text to decompose characters into base characters and diacritics
    normalized_text = unicodedata.normalize('NFD', text)
    # Filter out the diacritic marks
    filtered_text = ''.join([char for char in normalized_text if not unicodedata.combining(char)])
    return filtered_text

def remove_accents_and_lower(text):
    """ Remove tildes and traslate to lower """
    if pd.isna(text):
        return text
    text = str(text).lower().strip()
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')


# Function to find all numbers in a given text
def find_first_number(text):
    # This regex finds all occurrences of one or more digits
    matches = re.findall(r'\d+', text)
    numbers = [int(num) for num in matches]
    logging.debug(text)
    logging.debug(numbers)
    if len(numbers)>0:
        return numbers[0]
    else:
        return -1

# 'Construcción y Pruebas de Software - C24 4to C-L - C24 4to D-L-L'
def get_course_info_from_raw_coursename(raw_coursename):

    logging.debug(raw_coursename)
    fields_coursename = raw_coursename.split(' - ')
    coursename = fields_coursename[0]
    logging.debug(coursename)

    specialities = set()
    cycles = set()
    sections = set()
    for fields in fields_coursename[1:]:
        logging.debug(fields)
        _splits = fields.split('-')
        if len(_splits)>1:
            subfields = _splits[0].split()
            logging.debug(subfields)
            specialities.add(subfields[0])
            cycles.add(subfields[1])
            sections.add(subfields[-1])
    
    return { "course_name" : coursename,
             "specialities" : sorted(list(specialities)),
             "cycles" : sorted(list(cycles)),
             "sections" : sorted(list(sections)) }


def get_extra_info_course(struct_sections):

    specialities = set()
    cycles = set()
    sections = set()
    
    for section in struct_sections:
        info = section.get('name').split(' ')
        if len(info) >= 3 :
            specialities.add(info[0])
            cycles.add(info[1][0])  # first character
            sections.add(info[2][0]) # first character

    return sorted(list(specialities)), sorted(list(cycles)), sorted(list(sections)) 


if __name__ == '__main__':
    '''
    raw ='Construcción y Pruebas de Software - C24 4to C-L - C24 4to D-L-L'
    data = get_course_info_from_raw_coursename(raw)
    print(data)
    data = remove_accents_and_lower(raw)
    print(data)
    '''
    struct_sections = [{'id': 81483, 'name': 'C24 5to A-L', 'start_at': None, 'end_at': None}, {'id': 81484, 'name': 'C24 5to B-L', 'start_at': None, 'end_at': None}]
    sp,cy,se = get_extra_info_course(struct_sections)
    print(sp,cy,se)
