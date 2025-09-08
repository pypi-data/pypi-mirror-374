""" 
Programa : Course module for Canvas
Fecha Creacion : 11/08/2024
Fecha Update : None
Version : 1.0.0
Actualizacion : None
Author : Jaime Gomez
"""

import logging
from .base import BaseCanvas
from .utils import get_course_info_from_raw_coursename

ID =  'id'
NAME =  'name'
EMAIL = 'email'
'''
SHORT_NAME =  'short_name'
SPECIALITIES =  'specialities'
CYCLES =  'cycles'
SECTIONS =  'sections'
TEACHERS = 'teachers'
'''
# Create a logger for this module
logger = logging.getLogger(__name__)

class Course(BaseCanvas):

    def __init__(self, course_id, access_token, api_rest_path):
        super().__init__(access_token, api_rest_path)
        # 
        self.course_id = course_id
        # CONNECTOR
        self.url_course        = '<path>/courses/<course_id>'
        self.url_course_users  = '<path>/courses/<course_id>/search_users'


    def get(self, params = None):
        url = self.url_course
        url = url.replace('<course_id>', self.course_id)
        return super().get(url,params)

    '''
    def get_summary(self, params = None):

        params = {
                'enrollment_type': 'teacher',
                'enrollment_state': 'active',
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

        course =  self.get(params)
        print("INFO -> " )
        print( course)
        
        # {'id': 60006, 'name': 'Desarrollo de Soluciones en la Nube - C24 5to A-L - C24 5to B-L-L', 'account_id': 1385, 'uuid': 'Ljt0r91HNvvRPonIZkTKVTRuOAm7Ytuup16oVW8N', 'start_at': None, 'grading_standard_id': None, 'is_public': False, 'created_at': '2025-08-04T21:43:52Z', 'course_code': 'DesSolNube', 'default_view': 'wiki', 'root_account_id': 1, 'enrollment_term_id': 12199, 'license': 'private', 'grade_passback_setting': None, 'end_at': None, 'public_syllabus': False, 'public_syllabus_to_auth': False, 'storage_quota_mb': 524, 'is_public_to_auth_users': False, 'homeroom_course': False, 'course_color': None, 'friendly_name': None, 'hide_final_grades': False, 'apply_assignment_group_weights': False, 'sections': [{'id': 81483, 'name': 'C24 5to A-L', 'start_at': None, 'end_at': None}, {'id': 81484, 'name': 'C24 5to B-L', 'start_at': None, 'end_at': None}], 'total_students': 38, 'calendar': {'ics': 'https://tecsup.instructure.com/feeds/calendars/course_Ljt0r91HNvvRPonIZkTKVTRuOAm7Ytuup16oVW8N.ics'}, 'time_zone': 'America/Lima', 'blueprint': False, 'template': False, 'sis_course_id': None, 'integration_id': None, 'enrollments': [], 'workflow_state': 'available', 'restrict_enrollments_to_course_dates': False}

        raw_coursename =  course[NAME]

        print(course[NAME].split('-')[0])

        #course_info = get_course_info_from_raw_coursename(raw_coursename)

        specialities = set()
        cycles = set()
        sections = set()
        for section in course.get(SECTIONS):
            info = section.get(NAME).split(' ')
            specialities.add(info[0])
            cycles.add(info[1])
            sections.add(info[2])
            

        return  {
                    ID : course[ID],
                    NAME : course[NAME],
                    SHORT_NAME : course[NAME].split('-')[0],
                    SPECIALITIES : sorted(list(specialities)),
                    CYCLES : sorted(list(cycles)),
                    SECTIONS : sorted(list(sections)) 
                }
    '''

    def get_users(self, params = None):
        url = self.url_course_users
        url = url.replace('<course_id>', str(self.course_id))
        return self.get_all_pages(url,params)

    
    def get_teachers(self):
        
        teachers = list()
        
        # Parameters to filter by enrollment type 'teacher'
        params = {
            'enrollment_type[]': 'teacher',
            'enrollment_role[]': 'TeacherEnrollment'
        }
        
        _teachers = self.get_users(params)
        logger.debug(_teachers)

        for teacher in _teachers:
            
            info_teacher = {
                            ID  : teacher.get(ID), 
                            NAME  : teacher.get(NAME), 
                            EMAIL : teacher.get(EMAIL, "Not Available") 
                            }

            teachers.append(info_teacher)

        return teachers
    