from pathlib import Path

from update_study_process import (
    update_user_info,
    update_vocabulary,
)
from parse_course import (
    get_units,
    get_skills,
    dump_course_path,
    dump_current_skills,
    unit_path,
)
from parse_vocabulary import dump_words_of_skills, write_unit_wordlist
from condense_skill_voc import read_skill_voc, split_voc
from dump_voc_db import dump_to_db
from download_practice import download_batch
from process_practice import process_unit_practice
from export_csv import read_words, read_practice, combine, format_item

res_dir = "../res/"
userinfo_file = res_dir + "user_info.json"
header_file = res_dir + "headers"
header_prac_file = res_dir + "header_practice"
userinfo_file = res_dir + "user_info.json"
cached_voc_file = res_dir + "voc.json"
path_file = res_dir + "path.json"
path_of_units = res_dir + "unit_path"
skills_file = res_dir + "skills.json"
skills_dir = res_dir + "skills"
units_dir = res_dir + "units"
skills_voc_dir = res_dir + "skill_voc"
units_voc_dir = res_dir + "vocabulary_list"
voc_of_pos_dir = res_dir + "vocabulary_by_pos"
voc_database_file = res_dir + "data.db"
practice_dir = res_dir + "practice"
reword_csv = res_dir + "reword_csv"
user_info = Path(userinfo_file)


def update_info():
    # First, download user info
    update_user_info(header_file, userinfo_file, True)
    # Second, download vocabulary
    update_vocabulary(header_file, cached_voc_file, True)


def extract_path_skill_unit():
    if user_info.exists():
        dump_course_path(userinfo_file, path_file)
        dump_current_skills(userinfo_file, skills_file)
        get_units(path_file, units_dir)
        get_skills(skills_file, skills_dir)
        unit_path(path_file, path_of_units)
    else:
        print("user_info.json doesn't exist")


def extract_words_of_skill(unit_word_list: bool, start: int, end: int):
    skill_voc = Path(skills_voc_dir)
    # skills_dir_path = Path(skills_dir)
    voc_list_dir = Path(units_voc_dir)
    # notes_dir = Path("tips_and_notes")
    # if not skillvoc_dir.exists() or not any(skillvoc_dir.iterdir()):
    dump_words_of_skills(header_file, skill_voc, cached_voc_file, False)
    if unit_word_list and start <= end and start >= 1:
        write_unit_wordlist(
            voc_list_dir, units_dir, skills_dir, skills_voc_dir, start, end
        )

def condense_voc_by_pos():
    skill_voc = Path(skills_voc_dir)
    for skill in skill_voc.iterdir():
        words = read_skill_voc(skill)
        split_voc(words, voc_of_pos_dir)


def download_practice(start: int = 1, end: int = 1):
    download_batch(start, end, Path(path_of_units), header_file,practice_dir)
    for unit_index in range(start, end + 1):
        process_unit_practice(Path(practice_dir, str(unit_index)))


def export_csv(start: int = 1, end: int = 1):
    unit_index_start = start
    unit_index_end = end
    voc_path_str = skills_voc_dir
    for unit in range(unit_index_start, unit_index_end + 1):
        unit_path = Path(practice_dir, str(unit))
        for skill in unit_path.iterdir():
            if "practice" in skill.name or skill.is_dir():
                continue
            skill_voc = Path(voc_path_str, skill.name)
            voc = read_words(skill_voc)
            prac = read_practice(skill)
            items = combine(voc, prac, voc_database_file)
            format_item(items, unit, skill.name[:-5], reword_csv)


if __name__ == "__main__":
    start_index = 1
    end_index = 1
    # 1. download infomation from Duolingo
    update_info()
    # 2. extract courses structure from downloaded infomation
    extract_path_skill_unit()
    # 3. split vocabulary into skills
    extract_words_of_skill(True, start_index, end_index)
    # 4. optional, remove personal learning progres from vocabulary
    condense_voc_by_pos()
    # 5. dump all words to db
    dump_to_db(cached_voc_file, voc_database_file)
    # 6. download practice of target unit range
    download_practice(start_index, end_index)
    # 7. export practice to reword app csv
    export_csv(start_index, end_index)
