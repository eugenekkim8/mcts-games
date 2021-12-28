from abc import ABC, abstractmethod

class State(ABC):
    
    @abstractmethod
    def get_valid_actions(self):
        pass

    @abstractmethod
    def act(self, action):
        pass

    @abstractmethod
    def is_terminal(self):
        pass

    @abstractmethod
    def get_score(self):
        pass

    @abstractmethod
    def get_current_player(self):
        pass
