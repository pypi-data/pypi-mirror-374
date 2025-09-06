import enum
import logging
import time
from enum import Enum

import aiohttp

logger = logging.getLogger(__name__)


class Switch:
    switch_type: str
    cache_duration = 2
    _last_cache_time: int = 0
    _cached_switch_state = None

    def __init__(self, address):
        logger.debug(f"Created switch at {address}")
        self.cgi_bin_url = f"http://{address}/cgi-bin/"
        self.auth = aiohttp.BasicAuth("RPM", "RPM")
    
    async def get_info(self):
        status, constants = await self._make_get_request(["status?outputType=application/json", "constants?outputType=application/json"])

        status.update(constants)

        return status

    async def get_switch_state(self):
        return await self._make_get_request([f"avswitch?action=showAll{self.switch_type}PortsInJson"])

    async def set_property(self, port, property, value):
        await self._make_post_request("/cgi-bin/scweb", {f"output{port}.{property}": value, "cfunc": "changeavswitch", "stop": True})

    async def set_input(self, port, input_port=""):
        await self.set_property(port, "inputsrc", input_port)

    async def reboot(self):
        await self._make_post_request("/cgi-bin/status", {"action": "reboot"})

    def _make_session(self):
        return aiohttp.ClientSession(self.cgi_bin_url, auth=self.auth)

    async def _make_post_request(self, url, data):
        async with self._make_session() as session:
            res = await session.post(url, data=data)
    
    async def _make_get_request(self, urls):
        ret = []
        async with self._make_session() as session:
            for url in urls:
                res = await session.get(url)
                data = await res.json()
                ret.append(data)
        if len(ret) == 1:
            return ret[0]
        return ret

class AudioSwitch(Switch):
    switch_type = "Audio"

    async def mute(self, port, mute):
        mute = "muted" if mute else "not-muted"
        await self._make_post_request("/cgi-bin/avswitch?action=setAudio", {f"output{port}.mute": mute})

class VideoSwitch(Switch):
    switch_type = "Video"
