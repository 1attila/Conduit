from typing import Iterable
from prompt_toolkit.completion import WordCompleter, Completion, CompleteEvent
from prompt_toolkit.document import Document


class NonRepeatingWordCompleter(WordCompleter):

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        
        for completion in super().get_completions(document, complete_event):

            if completion.text not in document.text:
                yield completion