from .db import AgentDB
from .exceptions import StudyMaterialNotFound



def get_study_material_links(db: AgentDB,course_name: str, course_type: str, year: int, part: int, session: str):
    if not (year or part or session):
        study_materials = db.get_study_materials(course_name, course_type)
    elif year and part and session:
        study_materials = db.get_study_materials_by_year_session_and_part(course_name, course_type, year, session, part)
    elif year and part:
        study_materials = db.get_study_materials_by_year_and_part(course_name, course_type, year, part)
    elif year and session:
        study_materials = db.get_study_materials_by_year_and_session(course_name, course_type, year, session)
    elif part and session:
        study_materials = db.get_study_materials_by_part_and_session(course_name, course_type, part, session)
    elif year:
        study_materials = db.get_study_materials_by_year(course_name, course_type, year)
    elif part:
        study_materials = db.get_study_materials_by_part(course_name, course_type, part)
    elif session:
        study_materials = db.get_study_materials_by_session(course_name, course_type, session)
    



    if not study_materials:
        raise StudyMaterialNotFound(f'No study materials found for {course_name} {course_type} {year if year is not None else ""} {part if part is not None else ""} {session if session is not None else ""}')
    return [material.link for material in study_materials]