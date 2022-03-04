from __future__ import annotations

import os
import asyncio
from time import time
from ..components import TextInput
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types.components import Modal as ModalPayload
    from ..interactions import Interaction

__all__ = ('Modal',)

class Modal:
    """Represents a UI modal box.

    Parameters
    ----------
    title: :class:`str`
        The title of the modal.
    fields: Optional[List[:class:`.TextInput`]]
        The fields that the user will be asked to fill.
        Defaults to an empty list.
        There can be a maximum of 5 fields.
    custom_id: Optional[:class:`str`]
        The custom ID of the modal.
    """
    def __init__(
        self,
        *,
        title: str,
        fields: Optional[List[TextInput]] = None,
        custom_id: Optional[str] = None,
    ):
        self.title: str = title
        self.custom_id: str = custom_id or os.urandom(16).hex()
        self._fields: dict[str, TextInput] = {f.custom_id: f for f in (fields or [])}
        if len(self.fields) > 5:
            raise ValueError('Modal can only have up to 5 fields')

    @property
    def fields(self) -> list[TextInput]:
        """List[:class:`.TextInput`]: A list of the fields in the modal"""
        return list(self._fields.values())

    async def callback(self, interaction: Interaction):
        """The function that is called when the modal is submitted."""
        pass

    def add_field(self, **kwargs) -> TextInput:
        """Add a field to the modal.
        Takes the same kwargs as :class:`.TextInput`."""
        if len(self._fields) >= 5:
            raise ValueError("Cannot add any more fields to this modal")
        field = TextInput(**kwargs)
        self._fields[field.custom_id] = field
        return field

    def remove_field_at(self, index: int) -> None:
        """Remove a field from the modal.
        
        Parameters
        ----------
        index: :class:`int`
            The index of the field to remove."""
        del self._fields[list(self._fields.keys())[index]]

    async def _handle(self, interaction: Interaction):
        start_time = time()
        await self.callback(interaction)
        if not interaction.response.is_done() and time() - start_time < 3:
            try:
                await interaction.response.defer()
            except:
                pass

    def _dispatch(self, interaction: Interaction):
        for row in interaction.data['components']:
            component = row['components'][0]
            field = self._fields.get(component['custom_id'])
            if field:
                field.value = component['value']
        loop = asyncio.get_running_loop()
        loop.create_task(self._handle(interaction))

    def to_dict(self) -> ModalPayload:
        return {
            'title': self.title,
            'components': [
                {'type': 1, 'components': [f.to_dict()]} for f in self._fields.values()
            ],
            'custom_id': self.custom_id,
        }
