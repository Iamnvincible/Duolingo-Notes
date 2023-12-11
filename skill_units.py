from pathlib import Path
import json


def dump_current_skills(
    userinfo_file: str = "user_info.json", skills_file: str = "skills.json"
):
    file = Path(userinfo_file)
    if file.exists():
        with file.open("r", encoding="utf-8") as f:
            userinfo = json.load(f)
        skills = userinfo["currentCourse"]["skills"]
        with open(skills_file, "w") as f:
            json.dump(skills, f, indent=4)
        return skills
    return None


def dump_course_path(
    userinfo_file: str = "user_info.json", paths_file: str = "path.json"
):
    file = Path(userinfo_file)
    if file.exists():
        with file.open(encoding="utf-8") as f:
            userinfo = json.load(f)
        course_path = userinfo["currentCourse"]["pathSectioned"]
        with open(paths_file, "w") as f:
            json.dump(course_path, f, indent=4)
        return course_path


def get_units_legacy(course_path_file: str):
    file = Path(course_path_file)
    units_count = 0
    if file.exists():
        sub_teachingobjectives = []
        save_dir = Path("units")
        if not save_dir.exists():
            save_dir.mkdir()
        with file.open() as f:
            units = json.load(f)
        for unit in units:
            u = {}
            u["index"] = unit["unitIndex"] + 1
            u["guide"] = unit["guidebook"]
            u["theme"] = unit["teachingObjective"]
            u["cert"] = unit["cefrLevel"]
            u["levels"] = []
            for level in unit["levels"]:
                if (
                    level["type"] == "skill"
                    and level["pathLevelClientData"]["skillId"]
                    not in sub_teachingobjectives
                ):
                    sub_teachingobjectives.append(
                        level["pathLevelClientData"]["skillId"]
                    )
                    u["levels"].append(level)
            unit_path = Path(f'unit_{u["index"]}.json')
            unit_file = Path(save_dir, unit_path)
            with unit_file.open("w") as file:
                json.dump(u, file, indent=4)
            units_count += 1
    return units_count


def get_units(course_path_file: str = "path.json"):
    file = Path(course_path_file)
    units_count = 0
    if file.exists():
        sub_teachingobjectives = []
        save_dir = Path("units")
        if not save_dir.exists():
            save_dir.mkdir()
        with file.open() as f:
            sections = json.load(f)
        for section in sections:
            for unit in section['units']:
                u = {}
                u["index"] = unit["unitIndex"] + 1
                u["section"] = section['index'] + 1
                u["guide"] = unit["guidebook"]
                u["theme"] = unit["teachingObjective"]
                u["cert"] = unit["cefrLevel"]
                u["levels"] = []
                uniq_level_index = 1
                for level in unit["levels"]:
                    if (
                        level["type"] == "skill"
                        and level["pathLevelClientData"]["skillId"]
                        not in sub_teachingobjectives
                    ):
                        sub_teachingobjectives.append(
                            level["pathLevelClientData"]["skillId"]
                        )
                        level['level_index'] = uniq_level_index
                        u["levels"].append(level)
                    uniq_level_index += 1
                unit_path = Path(f'unit_{u["index"]}.json')
                unit_file = Path(save_dir, unit_path)
                with unit_file.open("w") as file:
                    json.dump(u, file, indent=4)
                units_count += 1
    return units_count


def get_skills(skills_file: str = "skills.json"):
    file = Path(skills_file)
    skills_count = 0
    if file.exists():
        save_dir = Path("skills")
        if not save_dir.exists():
            save_dir.mkdir()
        with file.open(encoding="utf-8") as f:
            skill_list = json.load(f)
        for arr in skill_list:
            for item in arr:
                skill_title = item["urlName"]
                skill_path = Path(f"{skills_count + 1}-{skill_title}.json")
                skill_file = Path(save_dir, skill_path)
                with skill_file.open("w") as file:
                    json.dump(item, file, indent=4)
                skills_count += 1
    return skills_count

def unit_path(path_file:str):
    path = Path(path_file)
    if path.exists():
        with path.open('r',encoding="utf-8") as f:
            path_json = json.load(f)
        for section in path_json:
            for unit in section['units']:
                unit_index = unit['unitIndex'] + 1
                save_name = f'unit-{unit_index}-path.json'
                save_file = Path(save_name)
                with save_file.open('w',encoding='utf-8') as f:
                    json.dump(unit,f,indent=4,ensure_ascii=False)

if __name__ == "__main__":
    userinfo_file = "user_info.json"
    path_file = "path.json"
    skills_file = "skills.json"
    user_info = Path(userinfo_file)
    if user_info.exists():
        dump_course_path(userinfo_file, path_file)
        dump_current_skills(userinfo_file, skills_file)
    get_units(path_file)
    get_skills()
    unit_path(path_file)
