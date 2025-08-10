import gi

gi.require_version("Notify", "0.7")

# Imports padrão do Ulauncher
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent

# Imports da aplicação
from src.item_event_listener import ItemEnterEventListener
from src.keyword_query_event_listener import KeywordQueryEventListener


class RbwUlauncherE(Extension):
    def __init__(self):
        super().__init__()

        # Instancia e registra os listeners da extensão
        keyword_listener = KeywordQueryEventListener(self)
        item_listener = ItemEnterEventListener()

        self.keyword_query_event_listener = keyword_listener

        self.subscribe(KeywordQueryEvent, keyword_listener)
        self.subscribe(ItemEnterEvent, item_listener)


if __name__ == '__main__':
    RbwUlauncherE().run()
