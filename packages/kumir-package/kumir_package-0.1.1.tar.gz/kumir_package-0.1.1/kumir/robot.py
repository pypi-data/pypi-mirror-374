
actions = {
    "up": "вверх",
    "down": "вниз",
    "left": "влево",
    "right": "вправо",
    "paint": "закрасить",
    "repeat": "нц",
    "end_repeat": "кц"
}

class Robot:
    def __init__(self):
        self.result = []
    
    def up(self):
        self.result.append({"action": "up"})
    
    def down(self):
        self.result.append({"action": "down"})
    
    def left(self):
        self.result.append({"action": "left"})
    
    def right(self):
        self.result.append({"action": "right"})
    
    def paint(self):
        self.result.append({"action": "paint"})
    
    def start_repeat(self, n):
        self.result.append({"action": "repeat", "count": n})
    
    def end_repeat(self):
        self.result.append({"action": "end_repeat"})
    
    def get_result(self):
        print(self.result)
        for action in self.result:
            action_name = action["action"]
            if action_name in actions:
                action["action"] = actions[action_name]
            if action_name == "repeat":
                action["action"] = f"{actions['repeat']} {action['count']} раз"
            if action_name == "end_repeat":
                action["action"] = actions["end_repeat"]
        # Преобразуем результат в строку
        self.result = "\n".join([f"{action['action']}" for action in self.result])
        # Возвращаем результат
        return self.result