from .db import AgentDB
from .exceptions import StudyMaterialNotFound



def get_study_material_links(db: AgentDB,course_name: str, course_type: str, year: int, part: int):
    if not year and not part :
        study_materials = db.get_study_materials(course_name, course_type)
    elif year and part:
        study_materials = db.get_study_materials_by_year_and_part(course_name, course_type, year, part)
    elif year:
        study_materials = db.get_study_materials_by_year(course_name, course_type, year)
    else:
        study_materials = db.get_study_materials_by_part(course_name, course_type, part)
    


    if not study_materials:
        raise StudyMaterialNotFound(f'No study material found for {course_name} {course_type} {year} {part}')
    return [material.link for material in study_materials]