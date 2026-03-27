


class UiRenderer:
    """
    Main class responsible to render all the UI components and text click events too
    """


    def __init__(
        self,
        server: None
        ) -> "UiRenderer":
        
        self.server = server


    def create_component_base_id(self, component: object):
        return f"mconduit-{type(component).__name__.lower()}-"

    
    def edit_data(self, name: str, value: str):
        
        self.server.execute(f"data entity modify {name}")