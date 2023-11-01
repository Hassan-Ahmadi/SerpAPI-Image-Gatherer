# test_image_download.py

import asyncio
import aiohttp
import pytest
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_dir)

from main import download_image

@pytest.mark.asyncio
async def test_download_image_success():
    # a valid image url
    url = "https://i.guim.co.uk/img/media/43352be36da0eb156e8551d775a57fadba8ae6d7/0_0_1440_864/master/1440.jpg?width=620&dpr=1&s=none"
    async with aiohttp.ClientSession() as session:
        image_data = await download_image(session, url)
        assert image_data is not None

@pytest.mark.asyncio
async def test_download_image_failure():
    url = "https://nonexistent-url.com/nonexistent.jpg"
    async with aiohttp.ClientSession() as session:
        image_data = await download_image(session, url)
        assert image_data is None