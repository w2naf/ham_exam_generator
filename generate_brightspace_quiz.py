import json
from pathlib import Path
import shutil
import glob
import os
import pandas as pd

# Files relative to this script
BASE_DIR = Path(__file__).parent
LICENSE_CLASS = "technician"
POOL_FILE = BASE_DIR / "pool" / f"{LICENSE_CLASS}.json"
QUIZ_DIR  = BASE_DIR / "quiz"

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

    # Copy over figure files and keep track of them in a dictionary.
    figure_files = glob.glob(str(BASE_DIR / "pool" / "*.jpg"))
    figs_dct = {}
    for figure_file in figure_files:
        shutil.copy(figure_file, QUIZ_DIR)
        print(f"Copied figure file: {figure_file} to {QUIZ_DIR}")

        bname    = os.path.basename(figure_file)
        if "T1" in bname:
            fig_name = "figure T-1"
        elif "T2" in bname:
            fig_name = "figure T-2"
        elif "T3" in bname:
            fig_name = "figure T-3"

        figs_dct[fig_name] = bname

    # Initialze Subelement Dictionary
    sub_els = {}
    for inx in range(10):
        sub_el  = f'T{inx}'
        sub_csv = QUIZ_DIR / f'{sub_el}.csv'
        sub_els[sub_el] = {'csv':sub_csv,'count':0}

    # Initialize the ARRL Module Dictionary
    mod_df = pd.read_csv(BASE_DIR / "pool" / "arrl_modules.csv", encoding='utf-8')
    mod_nrs = mod_df['Module'].unique()
    mods   = {}
    for mod_nr in mod_nrs:
        mod_name   = f'ARRL Module {mod_nr}'
        mod_csv    = QUIZ_DIR / f'arrl_mod_{mod_nr}.csv'
        mods[mod_nr] = {'csv':mod_csv, 'name':mod_name, 'count':0}

    fig_qIDs = []
    missing_qIDs = [] # Keep track of questions that are not found in arrl_modules.csv
    for qq in pool:      
        qID      = qq.get("id")
        sub_el   = qID[0:2]
        
        question = f'[{qID}] ' + qq.get('question')
        question = question.replace('"', '""')  # Escape double quotes for CSV

        answers   = qq.get("answers")
        correct  = [0]*len(answers)
        correct[qq.get("correct")] = 100  # Set the correct answer to 100 points

        tt = []
        tta = tt.append

        tta(f"ID,{qID},,,")
        tta("NewQuestion,MC,,,")
        tta(f"Title,{qID},,,")
        tta(f'QuestionText,"{question}",,,')
        tta("Points,1,,,")
        tta("Difficulty,1,,,")
        for corr, ans in zip(correct, answers):
            ans = ans.replace('"', '""')  # Escape double quotes for CSV
            tta(f'Option,{corr},"{ans}",,,')

        has_fig = False
        for fig_name,fig in figs_dct.items():
            if fig_name in question:
                tta(f"Image,images/{fig},,,")
                has_fig = True
                fig_qIDs.append(qID)
                break
        
        tta("Hint,,,,")
        tta("Feedback,,,,")
        tta("")

        # Write to sub-element quiz file
        with open(sub_els[sub_el]['csv'], 'a', encoding='utf-8') as f:
            f.write("\n".join(tt))
            f.write("\n")
        sub_els[sub_el]['count'] += 1

        # Write to ARRL module quiz file
        inxs = mod_df.index[mod_df['qID'] == qID].tolist()

        if len(inxs) > 1:
            print(f"NOTICE: Question ID {qID} found multiple times in arrl_modules.csv")
        if len(inxs) >= 1:
            for mod_nr_inx in inxs:
                mod_nr = mod_df.at[mod_nr_inx, 'Module']
                with open(mods[mod_nr]['csv'], 'a', encoding='utf-8') as f:
                    f.write("\n".join(tt))
                    f.write("\n")
                mods[mod_nr]['count'] += 1
        else:
            missing_qIDs.append(qID)
            print(f"WARNING: Question ID {qID} not found in arrl_modules.csv")

    print()
    print("########################################")
    print("All quiz files generated in:", QUIZ_DIR)
    print()
    print("Total questions generated:", len(pool))

    print()
    print("FCC Subelements:")
    for sub_el, data in sub_els.items():
        print(f"  - {sub_el}: {data['count']} questions")

    print()
    print("ARRL Modules:")
    for mod_nr, data in mods.items():
        print(f"  - {data['name']}: {data['count']} questions")

    print()
    if len(missing_qIDs) > 0:
        print(f"WARNING: The following {len(missing_qIDs)} questions were not found in arrl_modules.csv:")
        for qID in missing_qIDs:
            print(f"  - {qID}")
    print()
    if len(fig_qIDs) > 0:
        print(f"WARNING: The following {len(fig_qIDs)} questions contain figures.")
        print("Be sure to upload the *.jpgs to the images/ directory of your BrightSpace Class.")
        for qID in fig_qIDs:
            print(f"  - {qID}")

if __name__ == "__main__":
    main()
