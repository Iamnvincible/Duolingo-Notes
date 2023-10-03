from pathlib import Path
import json

def filter_skills_from_userinfo(userinfo: str):
    file = Path(userinfo)
    if file.exists():
        with file.open(encoding='utf-8') as f:
            userinfo = json.load(f)
        skills = userinfo['currentCourse']['skills']
        with open("skills.json", "w") as f:
            json.dump(skills, f, indent=4)

def get_path(userinfo: str):
    file = Path(userinfo)
    if file.exists():
        with file.open(encoding='utf-8') as f:
            userinfo = json.load(f)
        path = userinfo['currentCourse']['path']
        with open("path.json", "w") as f:
            json.dump(path, f, indent=4)

def get_units(path: str):
    file = Path(path)
    if file.exists():
        sub_teachingobjectives = []
        save_dir = Path('units')
        if not save_dir.exists():
            save_dir.mkdir()
        with file.open() as f:
            units = json.load(f)
        for unit in units:
            u = {}
            u["index"] = unit['unitIndex'] + 1
            u["guide"] = unit['guidebook']
            u['theme'] = unit['teachingObjective']
            u['cert'] = unit['cefrLevel']
            u['levels'] = []
            for level in unit['levels']:
                if level['type'] == "skill" and level['pathLevelClientData']['skillId'] not in sub_teachingobjectives:
                    sub_teachingobjectives.append(
                        level['pathLevelClientData']['skillId'])
                    u['levels'].append(level)
            unit_path = Path(f'unit_{u["index"]}.json')
            unit_file = Path(save_dir, unit_path)
            with unit_file.open("w") as file:
                json.dump(u, file, indent=4)

def get_skills(skills: str):
    file = Path(skills)
    if file.exists():
        sub_teachingobjectives = []
        save_dir = Path('skills')
        if not save_dir.exists():
            save_dir.mkdir()
        with file.open(encoding='utf-8') as f:
            skill_list = json.load(f)
        for arr in skill_list:
            for item in arr:
                skill_title = item['urlName']
                skill_path = Path(f'{skill_title}.json')
                skill_file = Path(save_dir, skill_path)
                with skill_file.open("w") as file:
                    json.dump(item, file, indent=4)


if __name__ == "__main__":
    header_file = "headers"
    userinfo_file = "user_info.json"
    path_file = "path.json"
    skills_file = "skills.json"
    user_info = Path(userinfo_file)
    if user_info.exists():
        skills = Path(skills_file)
        path = Path(path_file)
        if not skills.exists():
            filter_skills_from_userinfo(userinfo_file)
        get_skills(skills_file)
        if not path.exists():
            get_path(userinfo_file)
    else:
        headers = process_header_file(header_file)
        user_fields(headers)
    get_units(path_file)
    #get_skills(skills_file)
