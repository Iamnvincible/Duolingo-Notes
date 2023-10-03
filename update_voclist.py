from pathlib import Path
import json

def organize_words_by_pos(wordlist: list):
    '''
    将单词按词性组织
    '''
    word_catalog = {}
    other_key = "Other"
    for word in wordlist:
        pos = word['pos']
        if pos:
            if pos not in word_catalog.keys():
                word_catalog[pos] = []
            key = pos
        elif pos == None:
            if other_key not in word_catalog.keys():
                word_catalog[other_key] = []
            key = other_key
        word_catalog[key].append(word)
    for key in word_catalog.keys():
        word_catalog[key] = sorted(
            word_catalog[key], key=lambda x: x['word_string'])
    sorted_dict = dict(sorted(word_catalog.items(), key=lambda x: x[0]))
    return sorted_dict


def dump_wordlist_by_skill(skill_name: str, skill_word: dict, path: str):
    """
    将单词按照 skill 组织到一个文件中保存
    """
    import json
    skill_file = Path(path, f"{skill_name}.json")
    with skill_file.open("w") as file:
        json.dump(skill_word, file, indent=4)


def split_word_by_skill(vocab_overview: list):
    '''
    将单词按 skill 组织
    '''
    word_skills = {}
    for word in vocab_overview:
        skill = word['skill_url_title']
        if skill not in word_skills.keys():
            word_skills[skill] = []
        word_skills[skill].append(word)
    return word_skills


def get_unit_info(index: int, unit_path: Path, skill_path: Path, skill_voc_path: Path):
    '''
    获得每个 unit 的信息
    '''
    unit_file = Path(unit_path, f"unit_{index}.json")
    with unit_file.open('r') as f:
        unit = json.load(f)
    levels = unit['levels']
    skills = []
    for level in levels:
        skill_name = level['debugName'].replace(" ", "-")
        skill_file = Path(skill_path, f"{skill_name}.json")
        word_file = Path(skill_voc_path, f"{skill_name}.json")
        skill_info = {}
        if not skill_file.exists():
            print(f"{skill_file} not exist,in unit {index}")
            continue
        with skill_file.open('r') as f:
            skill = json.load(f)
            skill_info["info"] = skill
        if not word_file.exists():
            continue
        with word_file.open('r') as f:
            words = json.load(f)
            skill_info["words"] = words
        skills.append(skill_info)
    return {'unit': unit, 'skill': skills}


def show_unit(index: int):
    '''
    获得一个 unit 的单词表，返回 md 格式字符串列表
    '''
    genders = {"Masculine": "der", "Feminine": "die", "Neuter": "das"}
    units_dir = "units"
    skills_dir = "skills"
    skill_voc_dir = "skill_voc"
    udir = Path(units_dir)
    sdir = Path(skills_dir)
    vdir = Path(skill_voc_dir)
    string_lines = []
    u = get_unit_info(index, udir, sdir, vdir)
    # print("## %s"%(u['unit']['theme']))
    string_lines.append("## %s" % (u['unit']['theme']))
    for level in u['skill']:
        # print("### %s"%(level['info']['urlName']))
        string_lines.append("### %s" % (level['info']['urlName']))
        words = level['words']
        words_keys = sorted(words.keys())
        for key in words_keys:
            # print("#### {}".format(key))
            string_lines.append("#### {}".format(key))
            sorted_words = sorted(words[key], key=lambda x: x['word_string'])
            for word in sorted_words:
                word_str = word['word_string']
                if key == "Noun":
                    word_str = word_str.capitalize()
                    word_gender = word['gender']
                    if not word_gender:
                        print(
                            f"{word_str} without gender in {index},{u['unit']['theme']}")
                        word_str = str.format("{0}", word_str)
                    else:
                        word_str = str.format(
                            "{0}, {1}", word_str, word['gender'])
                # print("- {}".format(word_str))
                if key == "Verb":
                    word_str = word['word_string']
                    word_inf = word['infinitive']
                    if word_str != word_inf:
                        word_str = str.format("{0}, {1}", word_inf, word_str)
                string_lines.append("- {}".format(word_str))
    return string_lines


def write_unit_wordlist(path: Path, start: int, end: int):
    '''
    将一个范围内 unit 的单词表导出到 md 文件
    '''
    for i in range(start, end + 1):
        # print(i)
        lines = show_unit(i)
        file_name = Path(path, f"unit_{i}.md")
        with file_name.open("w") as file:
            file.writelines([line + '\n' for line in lines])


def write_tips_notes(notes:Path, skills:Path):
    '''
    将 skill 中有语法教学的部分导出到 md 文件
    '''
    import json
    for skill_file in skills.iterdir():
        with skill_file.open("r") as f:
            skillobj = json.load(f)
        if skillobj['tipsAndNotes']:
            mdfile = Path(notes, skill_file.name.replace('json','md'))
            with mdfile.open("w") as f:
                f.writelines(skillobj['tipsAndNotes'])


def dump_words_of_skills(req_headers: str, skillvoc_dir: Path, voc_file: str = None, update=False):
    vocab_overview = get_vocabulary(req_headers, voc_file, update)
    if not vocab_overview:
        print("vocab is empty")
        return
    skill_words = split_word_by_skill(vocab_overview)
    if not skillvoc_dir.exists():
        skillvoc_dir.mkdir()
    # 遍历 skill
    for skill in skill_words.keys():
        word_cata = organize_words_by_pos(skill_words[skill])
        one_skill_voc_file = Path(skillvoc_dir, skill)
        dump_wordlist_by_skill(skill, word_cata, skillvoc_dir)


if __name__ == "__main__":
    skillvoc_dir = Path("skill_voc")
    skills_dir = Path("skills")
    voc_list_dir = Path("vocabulary_list")
    notes_dir = Path("tips_and_notes")
    if not skillvoc_dir.exists() or not any(skillvoc_dir.iterdir()):
        dump_words_of_skills("headers", skillvoc_dir, "voc.json", True)
    write_unit_wordlist(voc_list_dir, 1, 33)
    if not notes_dir.exists() and skills_dir.exists():
        notes_dir.mkdir()
        write_tips_notes(notes_dir,skills_dir)
