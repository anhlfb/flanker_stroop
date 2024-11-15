from psychopy.visual import Window, TextStim, ImageStim
from psychopy import core, event
from psychopy.event import waitKeys
import csv
import random
import psychopy.gui as psygui
from Trial import FlankerTrial, StroopTrial, InstructionTrial

window = Window(fullscr=False, units='norm', color="white")

class Block:
    def __init__(self, window, csv_file, participant_id, participant_type, instruction_text=None):
        self.window = window
        self.trials_specification = []
        self.trials = []
        self.csv_file = csv_file
        self.participant_id = participant_id
        self.participant_type = participant_type
        self.instruction = InstructionTrial(window, instruction_text) if instruction_text else None
        self.process_csv()
        self.block_type = None

    def process_csv(self):
        with open(self.csv_file) as f:
            reader = csv.reader(f, delimiter=',')
            next(reader)  # Skip header
            for row in reader:
                self.trials_specification.append(row)

    def process_stroop_task(self):
        for word, color in self.trials_specification:
            self.trials.append(StroopTrial(self.window, word=word, color=color))

    def process_flanker_task(self):
        for correct, trial_type in self.trials_specification:
            self.trials.append(FlankerTrial(self.window, correct=correct, trial_type=trial_type))

    def run(self):
        if self.instruction:
            self.instruction.run()
            self.wait(0.5)

        if self.csv_file.startswith("ft"):
            self.block_type = "flanker"
            self.process_flanker_task()
        elif self.csv_file.startswith("st"):
            self.block_type = "stroop"
            self.process_stroop_task()
        else:
            print("Unknown file type.")

        for trial in self.trials:
            trial.run()
            self.wait(0.5)

    def wait(self, time):
        self.window.flip(clearBuffer=True)
        core.wait(time)

    def get_data_dict(self):
        data_dict = {
            'csv file': self.csv_file,
            'block type': self.block_type,
            'participant id': self.participant_id,
            'participant type': self.participant_type,
            'trials': [trial.get_data_dict() for trial in self.trials]
        }
        return data_dict

###### LOAD 2 BLOCKS OF FLANKER AND STROOP ######
def load_blocks(window, stroop_filenames=None, flanker_filenames=None, stroop_first=True):
    gui = psygui.Dlg(title="Stroop / Flanker study")
    gui.addField('Participant ID:')
    gui.addField('Participant Type:', choices=['main', 'pilot'])

    ok_pressed = gui.show()

    if not ok_pressed:
        return None, None

    participant_id = gui.data['Participant ID:']
    participant_type = gui.data['Participant Type:']

    flanker_instruction_text = "This is flanker test. Please press key 'f' for left and 'j' for right direction."
    stroop_instruction_text = "This is stroop test. Please press 'g', 'y', 'r', 'b' key for corresponding color."

    flanker_blocks = [Block(window, filename, participant_id=participant_id, participant_type=participant_type, instruction_text=flanker_instruction_text) for filename in flanker_filenames]
    stroop_blocks = [Block(window, filename, participant_id=participant_id, participant_type=participant_type, instruction_text=stroop_instruction_text) for filename in stroop_filenames]
    for block in flanker_blocks:
        block.process_flanker_task()  
        random.shuffle(block.trials)  

    for block in stroop_blocks:
        block.process_stroop_task()  
        random.shuffle(block.trials)  

    def roundrobin(*iterables):
        iterators = [iter(it) for it in iterables]
        while iterators:
            for it in iterators:
                try:
                    yield next(it)
                except StopIteration:
                    iterators.remove(it)

    if stroop_first:
        blocks = list(roundrobin(stroop_blocks, flanker_blocks))
    else:
        blocks = list(roundrobin(flanker_blocks, stroop_blocks))

    return blocks

def write_data_to_csv(blocks, output_filename):
    with open(output_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['index', 'block_type', 'block_csv', 'correct', 'is_correct', 'response', 'flanker_type', 'flanker_correct_direction', 'stroop_text', 'stroop_color', 'response time', 'participant id', 'participant type'])  # Header row

        index = 0
        for block in blocks:
            block.run()
            for trial_data in block.get_data_dict()['trials']:
                writer.writerow([
                    index,
                    block.block_type,
                    block.csv_file,
                    trial_data.get('correct', ''),
                    ', '.join(trial_data.get('response_list', [])),
                    trial_data.get('response', ''),
                    trial_data.get('flanker_type', ''),
                    trial_data.get('flanker_direction', ''),
                    trial_data.get('stroop_word', ''),
                    trial_data.get('stroop_color', ''),
                    trial_data.get('response_time', ''),
                    block.participant_id,
                    block.participant_type
                ])
                index += 1

    print(f'Data written to {output_filename}')

#### EXECUTE TASKS #####
stroop_files = ['st_b1.csv', 'st_b2.csv', 'st_b3.csv']
flanker_files = ['ft_b1.csv', 'ft_b2.csv', 'ft_b3.csv']
file_name = 'output.csv'

####### ORDER OF TESTS ########
blocks = load_blocks(window, stroop_files, flanker_files, stroop_first=True)

####### OUTPUT DATA ########
write_data_to_csv(blocks, file_name)

window.close()
