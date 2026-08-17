class BaseSimulator:

    def __init__(self, name):
        self.name = name
        self.time = 0

    def tick(self):
        self.time += 1

    def get_state(self):
        return {}

    def reset(self):
        self.time = 0