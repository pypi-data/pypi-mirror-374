""" 
Programa : User module for Canvas
Fecha Creacion : 05/08/2024
Fecha Update : 07/09/2025
Version : 1.1.0
Actualizacion : None
Author : Jaime Gomez
"""

import logging
from .base import BaseCanvas
from .utils import get_extra_info_course
ID = 'id'
NAME = 'name'
SHORT_NAME = 'short_name'
SPECIALITIES = 'specialities'
CYCLES = 'cycles'
SECTIONS = 'sections'
TERM_ID = 'term_id'
ENROLLMENT_TERM_ID = 'enrollment_term_id'
EMAIL = 'email'
TEACHERS = 'teachers'

# Create a logger for this module
logger = logging.getLogger(__name__)

class User(BaseCanvas):

    def __init__(self, user_id, access_token, api_rest_path):
        super().__init__(access_token, api_rest_path)
        # 
        self.user_id = str(user_id)
        # CONNECTOR
        
        # self.url_users       = '<path>/courses/<course_id>/users'
        
        self.url_courses     = '<path>/users/<teacher_id>/courses'


    def get_courses(self, params = None):
        url = self.url_courses
        url = url.replace('<teacher_id>', self.user_id)
        return self.get_all_pages(url,params)


    def get_courses_by_teacher_in_term(self, term_id):
        
        courses = list()

        params = {
                'enrollment_type': 'teacher',
                'enrollment_state': 'active',
                'enrollment_term_id': term_id,  # KEY PARAMETER
                'state[]': ['available', 'completed'],      # Include both active and completed
                'include[]': [
                    'term',
                    'total_students', 
                    'teachers',
                    'sections',
                    'course_progress'
                ],
                'per_page': 100
            }

        courses_raw = self.get_courses(params)
        logger.debug(courses_raw)

        for course in courses_raw:
            
            """
            {
                'id': '61261', 
                'name': 'Construcción y Pruebas de Software - C24 4to A-L - C24 4to B-L - C24 4to C-L - C24 4to D-L - C24 4to E-L-L', 
                'course_code': 'Const Pruebas', 
                'sis_course_id': None, 
                'enrollment_term_id': '12199', 
                'term': {'id': '12199', 'name': 'PFR L 2025 - 2'}, 
                'workflow_state': 'available', 
                'total_students': 94, 
                'start_at': None, 
                'end_at': None, 
                'created_at': '2025-08-13T20:57:16Z', 
                'teachers': ['Farfán Madariaga, Jaime Moshe', 'Gómez Marín, Jaime'], 
                'sections': [{'id': '83486', 'name': 'C24 4to E-L', 'course_id': ''}, {'id': '83482', 'name': 'C24 4to A-L', 'course_id': ''}, {'id': '83484', 'name': 'C24 4to C-L', 'course_id': ''}, {'id': '83485', 'name': 'C24 4to D-L', 'course_id': ''}], 
                'account_id': '1236', 
                'uuid': 'RuivUC3Qf2iJHJ3Q8NhnugVn6gHGFjfuRzHVCKNZ', 
                'default_view': 'wiki'
            }
            """
  

            if term_id == str(course.get(ENROLLMENT_TERM_ID)):
            
                # Get info details of sections
                specialities,cycles,sections = get_extra_info_course(course.get(SECTIONS))
                
                # Build info course
                info_course = {
                                ID  : course.get(ID), 
                                NAME  : course.get(NAME), 
                                SHORT_NAME : course.get(NAME).split('-')[0].strip(),
                                TERM_ID : course.get(ENROLLMENT_TERM_ID),
                                SPECIALITIES : specialities,
                                CYCLES : cycles,
                                SECTIONS : sections 
                                }

                courses.append(info_course)

        return courses
