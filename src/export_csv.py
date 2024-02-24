import json
from pathlib import Path


def read_words(skill_voc: Path):
    if skill_voc.exists():
        with skill_voc.open("r", encoding="utf-8") as f:
            voc = json.load(f)
        return voc


def read_practice(practice: Path):
    if practice.exists():
        with practice.open("r", encoding="utf-8") as f:
            prac = json.load(f)
        return prac


def extract_words(sentence):
    import re

    words = re.findall(r"\b[\w-]+\b", sentence)
    return words


def combine(voc: dict, prac: list, db_file: str = "data.db"):
    """_summary_

    Args:
        voc (dict): 单词列表
        prac (list): 例句列表

    Returns:
        _type_: 每个单词对应例句，所有单词例句的列表
    """
    items = {}  # 单词对应例句字典
    lower = []  # 小写例句列表
    # 先将例句单词小写
    for sen in prac:
        pair = {}
        pair["prompt"] = sen["prompt"].lower()
        pair["translation"] = sen["translation"].lower()
        lower.append(pair)
    # 单词列表按照词性分组
    for key in voc.keys():
        gener = voc[key]
        # 遍历每种词性下的单词
        for word_dict in gener:
            loop = -1
            word = word_dict["word_string"]  # 单词原型
            for pair in lower:
                loop += 1
                if len(extract_words(word)) == 1:
                    if word not in extract_words(pair["prompt"]):
                        continue
                index = pair["prompt"].find(word)
                if index >= 0:
                    regular_word = prac[loop]["prompt"][index : index + len(word)]
                    if (
                        key not in ["Noun", "Proper noun"]
                        and len(extract_words(regular_word)) == 1
                    ):  # 非名词小写
                        regular_word = regular_word.lower()
                    # 单词第一次出现
                    if regular_word not in items.keys():
                        items[regular_word] = {}
                        items[regular_word]["example"] = []
                        variant = None
                        if key == "Noun":
                            variant = fulfill_noun(word_dict, db_file)
                        elif key == "Verb":
                            variant = fulfill_verb(word_dict, db_file)
                        if not variant:
                            variant = "Translation"
                        items[regular_word]["variant"] = variant
                    # print(regular_word)
                    items[regular_word]["example"].append(
                        prac[loop]
                    )  # 为这个单词添加例句
            # 单词没有找到例句

            lowercase_keys = [k.lower() for k in items.keys()]
            if word not in lowercase_keys:
                lost_word = word
                if key in ["Noun", "Proper noun"]:
                    lost_word = word.capitalize()
                items[lost_word] = {}
                items[lost_word]["example"] = []

    return items


# "word1";"translation1";"example1";"ex.translation1";"example2";"ex.translation2"
def format_item(items: list, unit_index: int, skill_name: str, csv_dir: str = "csv"):
    save_dir = Path(csv_dir)
    if not save_dir.exists():
        save_dir.mkdir()
    csv = Path(save_dir, f"{unit_index}-{skill_name}.csv")
    with csv.open("a", encoding="utf-8") as f:
        f.truncate(0)
        for item in items.keys():
            string = ""
            # print(f"{item}")
            string += f'"{item}";'
            if "variant" in items[item].keys():
                string += f'"{items[item]["variant"]}";'
            else:
                string += '"Translation";'
            for sentence in items[item]["example"]:
                string += f"\"{sentence['prompt']}\";\"{sentence['translation']}\";"
            # print(string)
            string = string[0:-1]
            f.write(string + "\n")


def fulfill_noun(word: dict, db_file: str = "data.db"):
    # from db_reader import get_word
    from dump_voc_db import get_word

    # print(word["word_string"])
    append_note = ""
    if word["gender"]:
        append_note = word["gender"]
    lexeme_ids = get_word(word["id"], db_file).related_lexemes
    for item in lexeme_ids:
        append_note += " " + item.word_string.capitalize()
    return append_note


def fulfill_verb(word: dict, db_file: str = "data.db"):
    from dump_voc_db import get_word

    append_note = ""
    lexeme_ids = get_word(word["id"], db_file).related_lexemes
    for item in lexeme_ids:
        append_note += item.word_string + " "
    return append_note.rstrip()


if __name__ == "__main__":
    unit_index_start = 33
    unit_index_end = 33
    voc_path_str = "skill_voc/"
    for unit in range(unit_index_start, unit_index_end + 1):
        unit_path = Path(str(unit))
        for skill in unit_path.iterdir():
            if "practice" in skill.name or skill.is_dir():
                continue
            skill_voc = Path(voc_path_str, skill.name)
            voc = read_words(skill_voc)
            prac = read_practice(skill)
            items = combine(voc, prac)
            format_item(items, unit, skill.name[:-5])
