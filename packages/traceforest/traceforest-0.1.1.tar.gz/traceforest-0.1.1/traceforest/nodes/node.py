class CallNode:
    def __init__(self, name):
        self.name = name
        self.time = 0.0
        self.children = {}
        self.start_time = None

    def get_child(self, name):
        if name not in self.children:
            self.children[name] = CallNode(name)
        return self.children[name]
