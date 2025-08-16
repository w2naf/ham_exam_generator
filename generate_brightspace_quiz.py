import json
import random
import string
import argparse
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import shutil

# Files relative to this script
BASE_DIR = Path(__file__).parent
LICENSE_CLASS = "technician"
POOL_FILE = BASE_DIR / "pool" / f"{LICENSE_CLASS}.json"
QUIZ_DIR  = BASE_DIR / "quiz"

# # Create timestamp-based filenames
# TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
# EXAM_FILE = EXAMS_DIR / f"{TIMESTAMP}_{LICENSE_CLASS}_exam.txt"


def load_question_pool(filename):
    """
    Load the question pool from a JSON file using UTF-8 encoding.

    Args:
        filename (Path): Path to the JSON file containing the question pool.

    Returns:
        list: A list of question dictionaries.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """
    Main execution function that loads the pool, generates an exam,
    and writes the output files.
    """
    # parser = argparse.ArgumentParser(description="Generate a ham radio practice exam.")
    # parser.add_argument('--include-figures', action='store_true', help="Include questions with figures (default is to exclude for accessibility).")
    # args = parser.parse_args()

    if not POOL_FILE.exists():
        print(f"ERROR: Cannot find question pool at {POOL_FILE}")
        return

    pool = load_question_pool(POOL_FILE)
    # if not args.include_figures:
    #     pool = filter_no_figures(pool)

    # Delete and create the quiz directory
    if QUIZ_DIR.exists():
        shutil.rmtree(QUIZ_DIR)
        print(f"Deleted existing quiz directory: {QUIZ_DIR}")
    
    QUIZ_DIR.mkdir(parents=True, exist_ok=True)

    # Initialze Subelement Quiz Files
    sub_els = {}
    for inx in range(10):
        sub_el  = f'T{inx}'
        sub_csv = QUIZ_DIR / f'{sub_el}.csv'

        sub_els[sub_el] = {'csv':sub_csv}

        # with open(sub_csv, 'w', encoding='utf-8') as f:
        #     f.write("")
        print(sub_csv)

    for qq in pool:
        print(qq)
        
        qID      = qq.get("id")
        sub_el   = qID[0:2]
        question = f"[{qID}] " + qq.get("question")

        answers   = qq.get("answers")
        correct  = [0]*len(answers)
        correct[qq.get("correct")] = 100  # Set the correct answer to 100 points

        tt = []
        tta = tt.append

        tta(f"ID,{qID},,,")
        tta("NewQuestion,MC,,,")
        tta(f"Title,{qID},,,")
        tta(f"QuestionText,{question},,,")
        tta("Points,1,,,")
        tta("Difficulty,1,,,")
        # tta("Image,images/MC1.jpg,,,")
        # tta("Image,,,,")
        for corr, ans in zip(correct, answers):
            tta(f"Option,{corr},{ans},,,")
        tta("Hint,,,,")
        tta("Feedback,,,,")
        tta("")

        for ll in tt:
            print(ll)

        with open(sub_els[sub_el]['csv'], 'a', encoding='utf-8') as f:
            f.write("\n".join(tt))
            f.write("\n")

        print("Added question to subelement:", sub_el)

if __name__ == "__main__":
    main()
