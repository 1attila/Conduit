class UI:
    """
    UI Components container.

    Inherit from this class for every UI that you want to make.

    Make sure to add the components to the instance:
    ```

    class MyUI(ui.UI):

        def __init__(self):

            self.label_1 = ui.Label() # Rigth
            label_2 = ui.Label() # Wrong
    ```
    """