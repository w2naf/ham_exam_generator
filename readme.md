# Ham Exam Generator

This repository contains a Python-based tool for generating amateur radio license practice exams. It uses a question pool in JSON format to create randomized exams and answer keys for the Technician class license.

## Features

- Generates randomized practice exams and answer keys.
- Outputs exams and keys in both text and PDF formats.
- Supports accessibility with customizable font size and style for PDFs.
- Includes a comprehensive question pool for the Technician class license.

## Repository Structure

```
.
├── generate_exam.py       # Main script for generating exams
├── pool/
│   └── technician.json    # Question pool for Technician class license
└── exams/                 # Directory where generated exams and keys are saved
```

## Requirements

- Python 3.7 or higher
- Required Python packages:
  - `fpdf`
  - `pathlib`

Install the required packages using pip:

```sh
pip install fpdf
```

## Usage

1. Clone the repository:

```sh
git clone https://github.com/w2naf/ham_exam_generator.git
cd ham_exam_generator
```

2. Run the script to generate an exam:

```sh
python generate_exam.py
```

3. The generated exam and answer key will be saved in the `exams/` directory with timestamped filenames.

## Question Pool Format

The question pool is stored in `pool/technician.json` and follows this structure:

```json
{
  "id": "T1A02",
  "correct": 2,
  "refs": "[97.1]",
  "question": "Which agency regulates and enforces the rules for the Amateur Radio Service in the United States?",
  "answers": [
    "FEMA",
    "Homeland Security",
    "The FCC",
    "All these choices are correct"
  ]
}
```

- `id`: Unique identifier for the question.
- `correct`: Index of the correct answer (0-based).
- `refs`: References to FCC rules or other materials.
- `question`: The question text.
- `answers`: List of possible answers.

Many thanks to Russ Olsen for making the U.S. amateur radio question pool available in JSON format from https://github.com/russolsen/ham_radio_question_pool.

## Customization

- To modify the question pool, edit `pool/technician.json`.
- To change the license class, update the `LICENSE_CLASS` variable in `generate_exam.py`.

## Contributing

Contributions are welcome! If you have additional question pools or feature ideas, feel free to submit a pull request or open an issue.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE.txt](LICENSE.txt) file for details.