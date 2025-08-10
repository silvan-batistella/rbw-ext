from typing import Dict, Any, Optional

from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

from .tipo_dado import TipoDado


class Field:
    def __init__(self, tipo_dado: TipoDado, field_data: Dict[str, Any]):
        self.tipo_dado = tipo_dado
        self.name: str = field_data.get("name", "Campo")
        self.value: str = field_data.get("value", "")

    def get_item(self) -> Optional[ExtensionResultItem]:
        # Apenas retorna se houver valor
        if not self.value:
            return None

        display_value = self.value[:30] + " [...]" if len(self.value) > 30 else self.value

        return ExtensionResultItem(
            icon=TipoDado.get_icon(self.tipo_dado),
            name=f"{self.name.upper()}:   {display_value}",
            on_enter=CopyToClipboardAction(self.value)
        )
