from Model.Creators.Creator import Creator
from Model.Creators.CreatorListener import CreatorListener


class AddTexCreator(Creator):
    TITLE: str = 'Add .tex file'

    def __init__(self, settings: dict[str, str], creator_listener: CreatorListener):
        super().__init__()
        self.settings = settings
        self.creator_listener = creator_listener

    def get_title(self) -> str:
        return AddTexCreator.TITLE
