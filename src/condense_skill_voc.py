from pathlib import Path
import json
from enum import Enum

unmatched_keys = set()


class Pos(Enum):
    Noun = 1
    Verb = 2
    Adjective = 3
    Adverb = 4
    Pronoun = 5
    Conjunction = 6
    Determiner = 7
    Preposition = 8
    Interjection = 9
    Numeral = 10
    Proper_noun = 11
    Other = 12


def string_to_enum(enum_class, enum_string):
    for member in enum_class.__members__.values():
        if member.name.replace("_", " ") == enum_string:
            return member
    raise ValueError(f"No matching enum member found for '{enum_string}'")


def read_skill_voc(skill_voc: Path):
    """
    读取 skill_voc 文件中的单词列表
    """
    if skill_voc.is_file():
        with skill_voc.open("r", encoding="utf-8") as file:
            words = json.load(file)
        return words
    return None


def split_voc(words: dict, split_dir: str = "word_collection"):
    if words is None:
        return None

    for key in words:
        value = words[key]
        match key:
            case Pos.Noun.name:
                split_noun(value, split_dir)
            case Pos.Verb.name:
                split_verb(value, split_dir)
            case Pos.Adjective.name:
                split_adj(value, split_dir)
            case Pos.Adverb.name:
                split_adv(value, split_dir)
            case _:
                split_common(value, key, split_dir)
                # unmatched_keys.add(key)
                # if key not in unmatched_keys:
                #     print(f"unmatched key {key}")
                #     unmatched_keys.add(key)
    # print(unmatched_keys)
    # {'Numeral', 'Preposition', 'Determiner',
    # 'Interjection', 'Conjunction', 'Pronoun',
    #  'Adjective', 'Proper noun', 'Verb',
    # 'Adverb', 'Other'}


def split_noun(words: list, split_dir: str = "word_collection"):
    condensed = []
    for single in words:
        temp = {}
        temp["word"] = single["word_string"].capitalize()
        temp["gender"] = single["gender"]
        temp["skill"] = single["skill_url_title"]
        temp["id"] = single["lexeme_id"]
        temp["related_words"] = single["related_lexemes"]
        condensed.append(temp)
    update_category(Pos.Noun, condensed, split_dir)


def split_verb(words: list, split_dir: str = "word_collection"):
    condensed = []
    verb_fields = [
        "word_string",
        "infinitive",
        "skill_url_title",
        "lexeme_id",
        "related_lexemes",
    ]
    for single in words:
        temp = filter_fields(single, verb_fields)
        # temp["word"] = single["word_string"]
        # temp["infinitive"] = single["infinitive"]
        # temp["skill"] = single["skill_url_title"]
        # temp["id"] = single["lexeme_id"]
        # temp["related_words"] = single["related_lexemes"]
        condensed.append(temp)
    update_category(Pos.Verb, condensed, split_dir)


def split_adj(words: list, split_dir: str = "word_collection"):
    condensed = []
    adj_fields = [
        "word_string",
        "skill_url_title",
        "lexeme_id",
        "related_lexemes",
    ]
    for single in words:
        temp = filter_fields(single, adj_fields)
        # temp["word"] = single["word_string"]
        # temp["skill"] = single["skill_url_title"]
        # temp["id"] = single["lexeme_id"]
        # temp["related_words"] = single["related_lexemes"]
        condensed.append(temp)
    update_category(Pos.Adjective, condensed, split_dir)


def split_adv(words: list, split_dir: str = "word_collection"):
    condensed = []
    adv_fields = [
        "word_string",
        "skill_url_title",
        "lexeme_id",
        "related_lexemes",
    ]
    for single in words:
        temp = filter_fields(single, adv_fields)
        # temp["word"] = single["word_string"]
        # temp["skill"] = single["skill_url_title"]
        # temp["id"] = single["lexeme_id"]
        # temp["related_words"] = single["related_lexemes"]
        condensed.append(temp)
    update_category(Pos.Adverb, condensed, split_dir)


def split_common(words: list, pos_str: str, split_dir: str = "word_collection"):
    condensed = []
    common_fields = [
        "word_string",
        "skill_url_title",
        "lexeme_id",
        "related_lexemes",
    ]
    for single in words:
        temp = filter_fields(single, common_fields)
        condensed.append(temp)
    pos = string_to_enum(Pos, pos_str)
    update_category(pos, condensed, split_dir)


def filter_fields(word: dict, keys: list):
    temp = {}
    keymap = {
        "word_string": "word",
        "skill_url_title": "skill",
        "lexeme_id": "id",
        "related_lexemes": "related_words",
        "infinitive": "infinitive",
        "gender": "gender",
    }
    for key in keys:
        temp[keymap[key]] = word[key]
    return temp


def update_category(pos_name: Pos, word_list: list, collection_path="word_collection"):
    save_dir = Path(collection_path)
    if not save_dir.exists():
        save_dir.mkdir()
    pos_file = Path(collection_path, pos_name.name + ".json")
    previous = []
    if len(word_list) == 0:
        return
    if not pos_file.exists():
        pos_file.touch()
    with pos_file.open("r", encoding="utf-8") as f:
        if pos_file.stat().st_size > 0:
            previous = json.load(f)
    current = previous + uniq_merge(previous, word_list)
    with pos_file.open("w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=4)


def uniq_merge(previous: list, pending: list):
    uniq = []
    for new in pending:
        dup = False
        for word in previous:
            if word["id"] == new["id"]:
                dup = True
                break
        if not dup:
            uniq.append(new)
    return uniq


if __name__ == "__main__":
    skill_voc_path = "skill_voc/"
    skill_voc = Path(skill_voc_path)
    for skill in skill_voc.iterdir():
        # print(skill.name)
        words = read_skill_voc(skill)
        split_voc(words)
        # exit()
