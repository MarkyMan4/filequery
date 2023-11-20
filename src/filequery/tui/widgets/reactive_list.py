from typing import List

from textual.reactive import reactive
from textual.widget import Widget


# this is simply a list of items, where each item is displayed on its own line
# and it is reactive so the display updates as the list updates
class ReactiveList(Widget):
    items = reactive([])

    def render(self) -> str:
        return "\n".join(self.items)
