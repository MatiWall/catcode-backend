import logging

from catdocs.core.events import EventType
from catdocs.core.events.handlers import on_component_created_or_changed
from messaging_tools import Message, EventBus

from catdocs.utils import create_name

logger = logging.getLogger(__name__)

from catdocs.read_componnets import read_components
async def on_startup():

    components = await read_components()
    for component in components:

        event = Message(
            type=EventType.COMPONENT_UPDATED,
            body=component
        )
        await on_component_created_or_changed(event)

    logger.info('Finished start up processes')


