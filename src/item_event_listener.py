from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()

        if not data:
            return HideWindowAction()

        action = data.get("action")
        handler = extension.keyword_query_event_listener

        match action:
            case "unlock_vault":
                handler.desbloquear_rbw()
            case "sync_vault":
                handler.sync_rbw()
            case "lock_vault":
                handler.bloquear_rbw()
            case "show_item":
                item_id = data.get("item_id")
                return handler.get_info(item_id)
            case "list_folder":
                folder = data.get("folder")
                handler.show_notification(f"Listar registros da pasta: {folder}", "Info")

        return HideWindowAction()
