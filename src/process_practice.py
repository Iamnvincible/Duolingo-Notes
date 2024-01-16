import json
from pathlib import Path


def read_practice(practice_file: Path):
    practice = []
    sub_practice = [
        "challenges",
        "adaptiveChallenges",
        "easierAdaptiveChallenges",
        "mistakesReplacementChallenges",
        "adaptiveInterleavedChallenges",
    ]
    with practice_file.open("r") as f:
        practice_json = json.load(f)
    for key in sub_practice:
        if key in practice_json:
            if key == "adaptiveInterleavedChallenges":
                practice.extend(practice_json[key]["challenges"])
                continue
            if practice_json[key]:
                practice.extend(practice_json[key])
    # print(len(practice))
    return practice


def read_type(practice: list):
    keep_practice = []
    for item in practice:
        if item["type"] not in ["assist", "match", "select"]:
            # if 'prompt' in item and item['type'] != 'assist':
            print(item["type"])
            exercise = {}
            # print(f"{item['type']}")
            # exercise['type']=item['type']
            meta = item["metadata"]
            # print(item['metadata']['text'])
            if "translation" in meta:
                # print(meta['translation'])
                trans = meta["translation"]
            elif "solution_translation" in meta:
                # print(meta['solution_translation'])
                trans = meta["solution_translation"]
            elif item["type"] == "completeReverseTranslation":
                trans = meta["challenge_construction_insights"]["best_solution"]
            else:
                print(f"No translation for {item['type']}")

            if item["type"] == "readComprehension":
                exercise["prompt"] = meta["passage"]
                exercise["translation"] = ""
            elif item["type"] in ["gapFill", "tapComplete"]:
                exercise["prompt"] = meta["text"]
                exercise["translation"] = meta["best_translation"]
            elif item["type"] == "dialogue":
                exercise["prompt"] = meta["choices"][meta["correct_index"]]
                exercise["translation"] = trans
            elif item["type"] == "definition":
                exercise["prompt"] = meta["text"]
                exercise["translation"] = meta["choices"][meta["correct_index"]]
            elif item["type"] == "listenComprehension":
                exercise["prompt"] = meta["prompt"]
                exercise["translation"] = ""
            elif item["type"] in ["listenIsolation"] or meta["source_language"] == "de":
                exercise["prompt"] = meta["text"]
                exercise["translation"] = trans
            elif meta["source_language"] == "en":
                exercise["prompt"] = trans
                exercise["translation"] = meta["text"]
            keep_practice.append(exercise)
    return keep_practice


def process_unit_practice(unit_practice_folder: Path):
    for skill in unit_practice_folder.iterdir():
        if skill.is_file():
            continue
        skill_name = skill.name + ".json"
        practices = []
        for file in skill.iterdir():
            print(file.name)
            practices.extend(read_type(read_practice(file)))
        total = Path(unit_practice_folder, skill_name)
        with total.open("w", encoding="utf-8") as f:
            json.dump(filter_uniq(practices), f, indent=4, ensure_ascii=False)


def filter_uniq(practices: list):
    hashes = []
    uniq_practices = []
    for item in practices:
        prompt_hash = hash(item["prompt"])
        transl_hash = hash(item["translation"])
        if prompt_hash not in hashes and transl_hash not in hashes:
            uniq_practices.append(item)
            hashes.extend([prompt_hash, transl_hash])
            continue
    return uniq_practices


if __name__ == "__main__":
    unit_index = 33
    process_unit_practice(Path(str(unit_index)))
