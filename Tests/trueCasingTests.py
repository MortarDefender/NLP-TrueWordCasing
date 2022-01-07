import sys
import json

sys.path.append('../')

from src.trueCasing import true_case

if __name__ == '__main__':
    with open('config.json', 'r') as json_file:
        config = json.load(json_file)

    true_case(config['input_filename'], config['output_filename'], config['corpus'])
