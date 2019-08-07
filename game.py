class GameSession():

    def __init__(self):
        self.apply_amnt = 0

    def apply(self, client_data):
        self.apply_amnt += 1

        return '{} {}'.format(client_data, str(self.apply_amnt))
