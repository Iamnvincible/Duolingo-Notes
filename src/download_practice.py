import requests
from pathlib import Path
import json


def process_req_body(practice_class: str, practice_type: str, skill_ids: list):
    # file = Path("json.json")
    skill_body = "request_skill.json"
    skill_lege_body = "request_skill_legendary.json"
    pract_body = "request_practice.json"
    pract_lege_body = "request_practice_legendary.json"
    body_file = None
    if practice_type == "level":
        if practice_class == "skill":
            body_file = Path(skill_body)
        elif practice_class == "practice":
            body_file = Path(pract_body)
    elif practice_type == "legendary":
        if practice_class == "skill":
            body_file = Path(skill_lege_body)
        elif practice_class == "practice":
            body_file = Path(pract_lege_body)
    if body_file and body_file.exists():
        with body_file.open() as f:
            body_json = json.load(f)
            if practice_class == "skill" and practice_type == "legendary":
                body_json["skillId"] = skill_ids
            else:
                body_json["skillIds"] = skill_ids
        return body_json
    print("none body")


def request_practice(req_headers: dict, req_body, save_file: Path):
    session_url = "https://www.duolingo.com/2017-06-30/sessions"
    # print(req_body)
    # print(req_headers)
    response = requests.post(session_url, headers=req_headers, timeout=5, json=req_body)
    if response.status_code == 200:
        json_body = json.loads(response.text)
        with save_file.open("w", encoding="utf-8") as f:
            json.dump(json_body, f, indent=4)
        return True
    else:
        print(response.status_code)
        return None


def process_header_file(
    header_file_path: str, unit_index: int, level_index: int, practice_type: str
):
    base_url = "https://www.duolingo.com/lesson/unit"
    practice_types = ["level", "legendary"]
    # unit/31/level/"
    file = Path(header_file_path)
    if file.exists() and practice_type in practice_types:
        with file.open() as f:
            req_headers = f.readlines()
        headers = {}
        for header in req_headers:
            attr, value = [item.strip() for item in header.split(":", maxsplit=1)][:2]
            headers[attr] = value
        headers["Referer"] = f"{base_url}/{unit_index}/{practice_type}/{level_index}"
        return headers
    return None


def read_levels(unit_file_path: str):
    unit = Path(unit_file_path)
    if unit.exists():
        with unit.open() as f:
            unit_json = json.load(f)
        levels = unit_json["levels"]
        return levels
    else:
        print("unit file does not exist.")


def download_practice(
    unit_index: int, levels: list, header_file_path: str, save_path: str = "practice"
):
    index = 0
    target_level_type = ["skill", "practice"]
    save_to = Path(save_path)
    if not save_to.exists():
        save_to.mkdir()
    for level in levels:
        index += 1
        level_type = level["type"]
        level_name = level["debugName"].replace(" ", "-")
        if level_name == "Dining-Out":
            level_name = "DiningOut"

        if level_type == target_level_type[0]:
            request_body_level = process_req_body(
                "skill", "level", [level["pathLevelClientData"]["skillId"]]
            )
            request_body_legen = process_req_body(
                "skill", "legendary", level["pathLevelClientData"]["skillId"]
            )
        elif level_type == target_level_type[1]:
            request_body_level = process_req_body(
                "practice", "level", level["pathLevelClientData"]["skillIds"]
            )
            request_body_legen = process_req_body(
                "practice", "legendary", level["pathLevelClientData"]["skillIds"]
            )
        else:
            continue
        if level_type == target_level_type[0]:
            save_folder = check_save_path(save_to, unit_index, level_name)
        else:
            save_folder = check_save_path(save_to, unit_index, target_level_type[1])

        req_header_level = process_header_file(
            header_file_path, unit_index, index, "level"
        )
        req_header_legen = process_header_file(
            header_file_path, unit_index, index, "legendary"
        )
        practice_name_level = f"{index}-{level_name}.json"
        practice_name_legen = f"{index}-{level_name}-legendary.json"
        rcode_level = request_practice(
            req_header_level, request_body_level, Path(save_folder, practice_name_level)
        )
        rcode_legen = request_practice(
            req_header_legen, request_body_legen, Path(save_folder, practice_name_legen)
        )
        download_verbose(rcode_level, practice_name_level)
        download_verbose(rcode_legen, practice_name_legen)


def download_verbose(rcode, filename: str):
    if not rcode:
        print(f"{filename} failed")
        exit(-1)
    else:
        print(f"{filename}")


def check_save_path(folder: Path, unit_index: int, skill_name: str):
    unit_folder = Path(folder, str(unit_index))
    if not unit_folder.exists():
        unit_folder.mkdir()
    skill_folder = Path(unit_folder, skill_name)
    if not skill_folder.exists():
        skill_folder.mkdir()
    return skill_folder


def download_unit_practice(
    unit_index: int, unit_file_path: str, header_file_path: str, save_path
):
    levels = read_levels(unit_file_path)
    if levels:
        download_practice(unit_index, levels, header_file_path, save_path)


def download_batch(
    start: int, end: int, dir_of_path: Path, header: str, save_path: str = "practice"
):
    for index, unit_path in enumerate(dir_of_path.iterdir()):
        file_index = int(unit_path.name.split("-")[1])
        if file_index in range(start, end + 1):
            print(unit_path.name)
            download_unit_practice(file_index, unit_path, header, save_path)


if __name__ == "__main__":
    path_dir = "paths"
    header_file_path = "header"
    download_batch(33, 33, Path(path_dir), header_file_path)
    # unit_index = 31
    # unit_file_path = "levels.json"
    # download_unit_practice(unit_index,unit_file_path,header_file_path)
