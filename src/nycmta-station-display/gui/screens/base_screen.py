class BaseScreen:
    def __init__(self, screen):
        self.screen = screen
        self.next_screen = None

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def render(self):
        pass
