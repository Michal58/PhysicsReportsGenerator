import abc


class CreatorListener:
    def __init__(self):
        pass

    @abc.abstractmethod
    def notify_about_result_of_main_function(self, result: bool):
        pass
