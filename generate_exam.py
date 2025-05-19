import json
import random
import string
import argparse
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from fpdf import FPDF

# Files relative to this script
BASE_DIR = Path(__file__).parent
LICENSE_CLASS = "technician"
POOL_FILE = BASE_DIR / "pool" / f"{LICENSE_CLASS}.json"
EXAMS_DIR = BASE_DIR / "exams"

# Create timestamp-based filenames
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
EXAM_FILE = EXAMS_DIR / f"{TIMESTAMP}_{LICENSE_CLASS}_exam.txt"
KEY_FILE = EXAMS_DIR / f"{TIMESTAMP}_{LICENSE_CLASS}_answer_key.txt"
EXAM_PDF = EXAMS_DIR / f"{TIMESTAMP}_{LICENSE_CLASS}_exam.pdf"
KEY_PDF = EXAMS_DIR / f"{TIMESTAMP}_{LICENSE_CLASS}_answer_key.pdf"

# PDF formatting defaults for accessibility
PDF_FONT = "Arial"
PDF_FONT_SIZE = 18  # Increased size for better visibility
PDF_FONT_STYLE = "B"  # Bold font
PDF_LINE_HEIGHT = 12
PDF_MARGIN = 20


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


def write_exam_and_key(exam, exam_path, key_path, exam_pdf_path, key_pdf_path):
    """
    Write the practice exam and corresponding answer key to text and PDF files.

    Args:
        exam (list): The list of selected exam questions.
        exam_path (Path): Path to write the exam text file.
        key_path (Path): Path to write the answer key text file.
        exam_pdf_path (Path): Path to write the exam PDF file.
        key_pdf_path (Path): Path to write the answer key PDF file.
    """
    letters = list(string.ascii_uppercase)
    EXAMS_DIR.mkdir(parents=True, exist_ok=True)

    exam_text = []
    key_text = []

    # Headers
    exam_text.append(f"Amateur Radio {LICENSE_CLASS.capitalize()} License Practice Exam")
    exam_text.append(f"Filename: {exam_path.name}\n" + "=" * 5 + "\n")

    key_text.append(f"Answer Key for {LICENSE_CLASS.capitalize()} Practice Exam")
    key_text.append(f"Filename: {key_path.name}\n" + "=" * 5 + "\n")

    for idx, q in enumerate(exam, start=1):
        answer_options = list(enumerate(q['answers']))
        random.shuffle(answer_options)
        correct_index = next(i for i, (orig_idx, _) in enumerate(answer_options) if orig_idx == q['correct'])

        # Question block
        exam_text.append(f"{idx}: ({q['id']})")
        exam_text.append(f"{q['question']}")
        for i, (_, ans_text) in enumerate(answer_options):
            exam_text.append(f"  {letters[i]}. {ans_text}")
        exam_text.append("")

        key_text.append(f"{idx} ({q['id']}): {letters[correct_index]}")

    # Write to text files
    with open(exam_path, 'w', encoding='utf-8') as ex_f:
        ex_f.write("\n".join(exam_text))

    with open(key_path, 'w', encoding='utf-8') as key_f:
        key_f.write("\n".join(key_text))

    # Write to PDF files with font size and weight for low vision
    def write_pdf(content_lines, pdf_path, title):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=PDF_MARGIN)
        pdf.add_page()
        pdf.set_font(PDF_FONT, style=PDF_FONT_STYLE, size=PDF_FONT_SIZE)
        pdf.set_title(title)
        for line in content_lines:
            clean_line = line.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, PDF_LINE_HEIGHT + 4, clean_line)
        pdf.output(str(pdf_path))

    write_pdf(exam_text, exam_pdf_path, f"{LICENSE_CLASS.capitalize()} Exam")
    write_pdf(key_text, key_pdf_path, f"{LICENSE_CLASS.capitalize()} Answer Key")


def filter_no_figures(pool):
    """
    Filter out questions that have figures/images or reference figures.
    """
    def has_figure(q):
        # Adjust this logic if your JSON uses a different key or pattern
        if 'figure' in q or 'image' in q:
            return True
        if 'figure' in q.get('question', '').lower():
            return True
        return False
    return [q for q in pool if not has_figure(q)]


def main():
    """
    Main execution function that loads the pool, generates an exam,
    and writes the output files.
    """
    parser = argparse.ArgumentParser(description="Generate a ham radio practice exam.")
    parser.add_argument('--include-figures', action='store_true', help="Include questions with figures (default is to exclude for accessibility).")
    args = parser.parse_args()

    if not POOL_FILE.exists():
        print(f"ERROR: Cannot find question pool at {POOL_FILE}")
        return

    pool = load_question_pool(POOL_FILE)
    if not args.include_figures:
        pool = filter_no_figures(pool)
    exam = generate_exam_by_subelement(pool)
    write_exam_and_key(exam, EXAM_FILE, KEY_FILE, EXAM_PDF, KEY_PDF)
    print(f"Exam written to {EXAM_FILE} and {EXAM_PDF}")
    print(f"Answer key written to {KEY_FILE} and {KEY_PDF}")


if __name__ == "__main__":
    main()
