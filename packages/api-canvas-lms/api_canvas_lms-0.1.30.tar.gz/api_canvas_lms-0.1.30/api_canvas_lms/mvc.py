""" 
Programa : Controller module for Canvas
Fecha Creacion : 12/08/2024
Version : 1.0.0
Author : Jaime Gomez
"""

import logging
from .base import BaseCanvas
from .user import User
from .account import Account
from .adda import BasicModuleCourseCanvasADDA
from .utils import remove_tilde, get_extra_info_course
from .exceptions import ManyTeachersException, NotFoundTeacherException, NotFoundCoursesException

# Create a logger for this module
logger = logging.getLogger(__name__)

class Semester():
    
    #account_id = "788"           # Account for -->  Diseño y Desarrollo de Software (C24)
    #enrollment_term_id = "8083"  # Semester    -->  PFR L 2024 - 1
    def __init__(self, account_id, enrollment_term_id):
        self.account_id = account_id
        self.enrollment_term_id = enrollment_term_id


class Controller(BaseCanvas):

    def __init__(self, access_token, api_rest_path):
        super().__init__(access_token, api_rest_path)

    def get_teachers_by_name_in_semester(self, teacher_name, semester):

        search_teacher_name = remove_tilde(teacher_name).lower()
        
        # Define accounts
        account = Account(semester.account_id, self.access_token, self.api_rest_path)

        # Get courses
        account.set_courses(
            account.get_courses_by_enrollment_term(semester.enrollment_term_id))

        # Get teachers
        teachers = account.get_teachers_by_enrollment_term(semester.enrollment_term_id)  
        logging.debug(teachers)

        # Match teacher
        matching_teachers = []
        for teacher_id, teacher_info in teachers.items():
            if search_teacher_name in teacher_info.get("name_search"):            
                logging.debug(f"Found '{teacher_name}' in teacher_id '{teacher_id}': {teacher_info.get('name')}")                                    
                matching_teachers.append({
                    'id': teacher_id,
                    'name': teacher_info.get('name'),
                    'name_search': teacher_info.get('name_search')
                })
                
        if len(matching_teachers) == 0 : raise NotFoundTeacherException
        
        return matching_teachers


    def valid_courses_adda_by_teacher_id_in_semester(self, teacher_id, semester ):

        teacher_id = int(teacher_id)
        response_adda = []
            
        # Define accounts
        account = Account(semester.account_id, self.access_token, self.api_rest_path)

        # Get courses
        account.set_courses(
            account.get_courses_by_enrollment_term(semester.enrollment_term_id))

        # Get courses of teacher
        courses_of_teacher = account.get_courses_by_enrollment_term_and_teacher(semester.enrollment_term_id,teacher_id )

        if len(courses_of_teacher) == 0 : raise NotFoundCoursesException

        # Validate Canvas
        for course in courses_of_teacher:
            logging.debug(course)
            mccsa = BasicModuleCourseCanvasADDA(str(course.get('id')), self.access_token, self.api_rest_path)
            res = mccsa.is_valid_structure()   
            logging.debug(res.get('status_adda'))
            logging.debug(res.get('course'))
            response_adda.append(res)
            
        return response_adda
            

    def valid_courses_adda_by_teacher_name_in_semester(self, teacher_raw_name, semester ):

        response_adda = []
        
        search_teacher_name = remove_tilde(teacher_raw_name).lower()
        
        account = Account(semester.account_id, self.access_token, self.api_rest_path)

        # Get courses
        account.set_courses(
            account.get_courses_by_enrollment_term(semester.enrollment_term_id))

        # Get teachers
        teachers = account.get_teachers_by_enrollment_term(semester.enrollment_term_id)  
        
        for teacher in teachers.values():
            logging.debug(teacher.get('name'))
        
        #You must only validate one teacher, no more two
        matching_teachers=[]
        for teacher_id, teacher_info in teachers.items():
            if search_teacher_name in teacher_info.get("name_search"):  
                matching_teachers.append( { 'id' : teacher_id,
                                            'name' : teacher_info.get('name')
                                           })
        
        if len(matching_teachers) == 0 : raise NotFoundTeacherException
        elif len(matching_teachers)> 1 : raise ManyTeachersException(teachers = matching_teachers )

        # Get courses of teacher
        teacher_name = matching_teachers[0].get('name')
        teacher_id = matching_teachers[0].get('id')        
        courses_of_teacher = account.get_courses_by_enrollment_term_and_teacher(semester.enrollment_term_id,teacher_id )
        logger.debug(courses_of_teacher)

        # Validate Canvas
        for course in courses_of_teacher:
            logging.debug(course)
            mccsa = BasicModuleCourseCanvasADDA(str(course.get('id')), self.access_token, self.api_rest_path)
            res = mccsa.is_valid_structure()   
            logging.debug(res.get('status_adda'))
            logging.debug(res.get('course'))
            response_adda.append(res)
            
        return teacher_name,response_adda


    def get_courses_by_teacher_in_term(self, teacher_id, term_id):

        user = User(teacher_id, self.access_token, self.api_rest_path)

        courses = user.get_courses_by_teacher_in_term(term_id)

        return courses  


    def get_courses_by_semester(self, semester):

        account = Account(semester.account_id, self.access_token, self.api_rest_path)

        courses = account.get_courses_by_enrollment_term(semester.enrollment_term_id)  

        return courses


    def validate_courses_by_ADDA(self, courses):

        responses = []

        for course in courses: 
            
            # {'id': 61308, 'name': 'Base de Datos Avanzado - C24 3ero B-L - C24 3ero A-L-L', 'short_name': 'Base de Datos Avanzado', 'term_id': 12199, 'specialities': ['C24'], 'cycles': ['3'], 'sections': ['A', 'B']}
            logger.debug(course) 
            
            course_id = str(course['id'])  
            mccsa = BasicModuleCourseCanvasADDA(course_id, self.access_token, self.api_rest_path)            
            status_adda, modules = mccsa.is_valid_structure()     

            '''
            # Get info details of sections
            specialities,cycles,sections = get_extra_info_course(course.get('sections'))
            
            # Get info details of course
            course_details = {
                        'id' : course_id,
                        'name' : course.get('name'),
                        'short_name' : course.get('name').split('-')[0].strip(),
                        'specialities' : specialities,
                        'cycles' : cycles,
                        'sections' : sections 
                        }
            '''
            #
            course_validate = {
                "status_adda":status_adda,
                "course": course,
                #"teachers": None,
                "modules": modules        
            }

            logger.debug(f"course_validate={course_validate}")
            responses.append(course_validate)

        return responses


    def validate_courses_by_semester(self, semester):
    

        courses = self.get_courses_by_semester(semester)

        responses = []

        for course in courses: 

            logger.debug(course) 
            mccsa = BasicModuleCourseCanvasADDA(str(course['id']), self.access_token, self.api_rest_path)            
            status_adda, modules = mccsa.is_valid_structure()    

            course_validate = {
                "status_adda":status_adda,
                "course": None,
                "teachers": None,
                "modules": modules        
            }

            logger.debug(f"course_validate={course_validate}")
            responses.append(course_validate)

        return responses
