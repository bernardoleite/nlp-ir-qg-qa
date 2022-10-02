# -*- coding: utf-8 -*-

from questiongen import request_questions, question_list_to_json
from answer import main
from utils.handle_files import read_file
import sys, os

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

file = 'live_demo'

with HiddenPrints():
    all_answers, score = main(file = file)

# Clear Screen
os.system('cls' if os.name == 'nt' else 'clear')

print("-" * 80)
for q in all_answers:
    lines = read_file(q['n_file'])
    print('|- Original text: ' + lines[q['n_line']])
    print('|- Question: ' + q['question'] + '\n|- Predicted answer: ' + q['y_pred'] + '\tCorrect Answer: ' + q['y_test'])
    print("-" * 80)
print("Eval: ", score)