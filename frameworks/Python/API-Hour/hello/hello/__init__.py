import logging
import asyncio
import os

import aiopg
import psycopg2.extras
import aiohttp.web

import api_hour

from . import endpoints


LOG = logging.getLogger(__name__)


class Container(api_hour.Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Servers
        self.servers['http'] = aiohttp.web.Application(loop=kwargs['loop'])
        self.servers['http'].ah_container = self # keep a reference to Container
        # routes
        self.servers['http'].router.add_route('GET', '/json', endpoints.world.json)
        self.servers['http'].router.add_route('GET', '/db', endpoints.world.db)
        self.servers['http'].router.add_route('GET', '/queries', endpoints.world.queries)

    def make_servers(self):
        return [self.servers['http'].make_handler()]

    @asyncio.coroutine
    def start(self):
        yield from super().start()
        LOG.info('Starting engines...')
        self.engines['pg'] = self.loop.create_task(aiopg.create_pool(host=os.environ.get('DBHOST', '127.0.0.1'),
                                                                     sslmode='disable',
                                                                     port=int(self.config['engines']['pg']['port']),
                                                                     dbname=self.config['engines']['pg']['dbname'],
                                                                     user=self.config['engines']['pg']['user'],
                                                                     password=self.config['engines']['pg']['password'],
                                                                     cursor_factory=psycopg2.extras.RealDictCursor,
                                                                     minsize=int(self.config['engines']['pg']['minsize']),
                                                                     maxsize=int(self.config['engines']['pg']['maxsize'])))
        yield from asyncio.wait([self.engines['pg']], return_when=asyncio.ALL_COMPLETED)

        LOG.info('All engines ready !')


    @asyncio.coroutine
    def stop(self):
        LOG.info('Stopping engines...')
        if 'pg' in self.engines:
            if self.engines['pg'].done():
                self.engines['pg'].result().terminate()
                yield from self.engines['pg'].result().wait_closed()
            else:
                yield from self.engines['pg'].cancel()
        LOG.info('All engines stopped !')
        yield from super().stop()