import json
from typing import Dict, Any, List

from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

from .custom_field import Field
from .tipo_dado import TipoDado


class Card:
    def __init__(self, raw: Dict[str, Any]):
        self.tipo_dado = TipoDado.CARTAO
        self.image = TipoDado.get_icon(self.tipo_dado)

        if isinstance(raw, str):
            raw = json.loads(raw)

        data = raw.get("data", {})
        self.code = data.get("code")
        self.notes = raw.get("notes")
        self.number = data.get("number")
        self.exp_year = data.get("exp_year")
        self.exp_month = data.get("exp_month")
        self.name = data.get("cardholder_name")

        self.fields: List[Field] = [
            Field(self.tipo_dado, f)
            for f in raw.get("fields", [])
            if f.get("type") == "text"
        ]

    def get_itens(self) -> List[ExtensionResultItem]:
        items: List[ExtensionResultItem] = []

        # Nome impresso
        if self.name:
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"NOME IMPRESSO:   {self.name}",
                on_enter=CopyToClipboardAction(self.name)
            ))

        # Número do cartão
        if self.number:
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"NÚMERO CARTÃO:   {self.number}",
                on_enter=CopyToClipboardAction(self.number)
            ))

        # Data de expiração (MM/YY)
        month = self.exp_month.zfill(2) if self.exp_month else None
        year = self.exp_year.zfill(2) if self.exp_year else None

        if month and year:
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"MM/YY:   {month}/{year}",
                on_enter=CopyToClipboardAction(f"{month}/{year}")
            ))

        elif month:
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"MÊS:   {month}",
                on_enter=CopyToClipboardAction(month)
            ))

        elif year:
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"ANO:   {year}",
                on_enter=CopyToClipboardAction(year)
            ))

        # CVV
        if self.code:
            masked_cvv = "*" * len(self.code.zfill(3))
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"CVV:   {masked_cvv}",
                on_enter=CopyToClipboardAction(self.code.zfill(3))
            ))

        # Notas
        if self.notes:
            display_notes = self.notes[:30] + " [...]" if len(self.notes) > 30 else self.notes
            items.append(ExtensionResultItem(
                icon=self.image,
                name=f"NOTA:   {display_notes}",
                on_enter=CopyToClipboardAction(self.notes)
            ))

        # Campos personalizados
        for field in self.fields:
            item = field.get_item()
            if item:
                items.append(item)

        return items
