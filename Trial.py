from psychopy.event import waitKeys
from psychopy.visual import Window, TextStim, ImageStim
from psychopy import visual, core, event
from psychopy.core import Clock

class Trial:
    def __init__(self, window):
        self.window = window
        self.response = None
        self.response_key = None
        self.is_correct = False
        self.clock = Clock()
        self.response_time = None

    def wait_keys(self):
        return event.waitKeys(keyList=['f', 'j'])

    def draw_and_flip(self, stims):
        for stim in stims:
            stim.draw()
        self.window.flip()
        self.clock.reset()
        self.response = self.wait_keys()
        self.response_key = self.response[0] if self.response else None
        self.clock.getTime()
        self.response_time = self.clock.getTime()
        print(self.response_time)


####### FLANKER ARROW LIST #######
arrow_file = 'flanker_arrow.png'
arrow_size = (0.2, 0.2)

positions_left = [(-0.5, 0), (-0.25, 0), (0, 0), (0.25, 0), (0.5, 0)]
positions_right = [(0.5, 0), (0.25, 0), (0, 0), (-0.25, 0), (-0.5, 0)]

####### SETUP FOR EACH TRIAL #######
class FlankerTrial(Trial):
    def __init__(self, window, correct=None, trial_type=None):
        super().__init__(window)
        self.correct = correct
        self.trial_type = trial_type
        self.data_dict = {}

        if self.correct == 'left' and self.trial_type == 'congruent':
            self.arrows = [visual.ImageStim(self.window, image=arrow_file, size=arrow_size, pos=pos, ori=180) for pos in positions_left]
        elif self.correct == 'right' and self.trial_type == 'congruent':
            self.arrows = [visual.ImageStim(self.window, image=arrow_file, size=arrow_size, pos=pos) for pos in positions_right]
        elif self.correct == 'left' and self.trial_type == 'incongruent':
            self.arrows = [visual.ImageStim(self.window, image=arrow_file, size=arrow_size, pos=pos) for pos in positions_right]
            self.arrows[2] = visual.ImageStim(self.window, image=arrow_file, size=arrow_size, pos=positions_left[2], ori=180)
        elif self.correct == 'right' and self.trial_type == 'incongruent':
            self.arrows = [visual.ImageStim(self.window, image=arrow_file, size=arrow_size, pos=pos, ori=180) for pos in positions_left]
            self.arrows[2] = visual.ImageStim(self.window, image=arrow_file, size=arrow_size, pos=positions_right[2], ori=360)
        elif self.correct == 'right':
            self.arrows = [ImageStim(self.window, image='flanker_arrow.png', size=arrow_size)]
        else:
            self.arrows = [ImageStim(self.window, image='flanker_arrow.png', size=arrow_size, ori=180)]

    def run(self):
        self.draw_and_flip(self.arrows)
        self.validate_response()

    def validate_response(self):
        self.response_list = []
        if len(self.response) > 1:
            self.is_correct = False
            self.response_list.append("invalid")
        elif (self.correct == 'left' and self.response[0] == 'f') or (
                self.correct == 'right' and self.response[0] == 'j'):
            self.is_correct = True
            self.response_list.append("correct")
        else:
            self.is_correct = False
            self.response_list.append("incorrect")

        return self.response_list

    def get_data_dict(self):
        self.data_dict = {
            #'type': 'FlankerTrial',
            'response': self.response_key,
            'correct': self.response[0],
            'flanker_direction': self.correct,
            'flanker_type': self.trial_type,
            'stroop_word': '-',
            'stroop_color': '-',
            'response_list': self.response_list,
            'response_time': self.response_time
        }
        return self.data_dict

class StroopTrial(Trial):
    def __init__(self, window, word, color):
        super().__init__(window)
        self.word = word
        self.color = color
        self.correct_key = None
        self.data_dict = {}

    def run(self):
        stim = visual.TextStim(self.window, text=self.word, color=self.color, height=0.5)
        self.draw_and_flip([stim])

    def wait_keys(self):
        return event.waitKeys(keyList=['b', 'r', 'y', 'g'])

    def validate_response(self):
        self.response_list = []
        color_to_key = {'blue': 'b', 'red': 'r', 'yellow': 'y', 'green': 'g'}
        self.correct_key = color_to_key.get(self.color)
        if len(self.response) > 1:
            self.is_correct = False
            self.response_list.append("invalid")
        elif self.response[0] == self.correct_key:
            self.is_correct = True
            self.response_list.append("correct")
        else:
            self.is_correct = False
            self.response_list.append("incorrect")

        return self.response_list

    def get_data_dict(self):
        self.validate_response()

        self.data_dict = {
            'response': self.response_key,
            'correct': self.correct_key,
            'stroop_word': self.word,
            'stroop_color': self.color,
            'flanker_direction': '-',
            'flanker_type': '-',
            'response_list': self.response_list,
            'response_time': self.response_time
        }
        return self.data_dict


class InstructionTrial:
    def __init__(self, window, text):
        self.window = window
        self.text = text

    def run(self):
        stim = visual.TextStim(self.window, text=self.text, color = "black")
        stim.draw()
        self.window.flip()
        event.waitKeys()

if __name__ == "__main__":
    win = visual.Window(size=(800, 600), color='white', units='norm')
    flanker_trial = FlankerTrial(win, correct='left', trial_type='congruent')
    flanker_trial.run()
    print(flanker_trial.get_data_dict())
