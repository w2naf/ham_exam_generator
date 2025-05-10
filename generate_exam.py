import json
import random
import string
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# Files relative to this script
BASE_DIR = Path(__file__).parent
LICENSE_CLASS = "technician"
POOL_FILE = BASE_DIR / "pool" / f"{LICENSE_CLASS}.json"
EXAMS_DIR = BASE_DIR / "exams"

# Create timestamp-based filenames
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
EXAM_FILE = EXAMS_DIR / f"{TIMESTAMP}_{LICENSE_CLASS}_exam.txt"
KEY_FILE = EXAMS_DIR / f"{TIMESTAMP}_{LICENSE_CLASS}_answer_key.txt"

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

def generate_exam_by_subelement(question_pool):
    """
    Generate a practice exam by selecting one random question from each subelement.

    Args:
        question_pool (list): The full list of question dictionaries.

    Returns:
        list: A shuffled list of selected exam questions.
    """
    groups = defaultdict(list)
    for q in question_pool:
        groups[q['id'][:3]].append(q)
    exam = [random.choice(bucket) for bucket in groups.values()]
    random.shuffle(exam)
    return exam

def write_exam_and_key(exam, exam_path, key_path):
    """
    Write the practice exam and corresponding answer key to text files.

    Args:
        exam (list): The list of selected exam questions.
        exam_path (Path): Path to write the exam file.
        key_path (Path): Path to write the answer key file.
    """
    letters = list(string.ascii_uppercase)
    EXAMS_DIR.mkdir(parents=True, exist_ok=True)

    with open(exam_path, 'w', encoding='utf-8') as ex_f, \
         open(key_path,  'w', encoding='utf-8') as key_f:
        # Write headers
        ex_f.write(f"Amateur Radio {LICENSE_CLASS.capitalize()} License Practice Exam\n")
        ex_f.write(f"Filename: {exam_path.name}\n")
        ex_f.write("=" * 60 + "\n\n")

        key_f.write(f"Answer Key for {LICENSE_CLASS.capitalize()} Practice Exam\n")
        key_f.write(f"Filename: {key_path.name}\n")
        key_f.write("=" * 60 + "\n\n")

        for idx, q in enumerate(exam, start=1):
            # Shuffle answers and track the correct one
            answer_options = list(enumerate(q['answers']))
            random.shuffle(answer_options)
            correct_index = next(i for i, (orig_idx, _) in enumerate(answer_options) if orig_idx == q['correct'])

            # Question block
            ex_f.write(f"Question {idx}: ({q['id']}) {q['question']}\n")
            for i, (_, ans_text) in enumerate(answer_options):
                ex_f.write(f"  {letters[i]}. {ans_text}\n")
            ex_f.write("\n")

            # Answer key line
            key_f.write(f"Question {idx} ({q['id']}): {letters[correct_index]}\n")

def main():
    """
    Main execution function that loads the pool, generates an exam,
    and writes the output files.
    """
    if not POOL_FILE.exists():
        print(f"ERROR: Cannot find question pool at {POOL_FILE}")
        return

    pool = load_question_pool(POOL_FILE)
    exam = generate_exam_by_subelement(pool)
    write_exam_and_key(exam, EXAM_FILE, KEY_FILE)
    print(f"Exam written to {EXAM_FILE}")
    print(f"Answer key written to {KEY_FILE}")

if __name__ == "__main__":
    main()