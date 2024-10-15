import sys
import time
from threading import Thread
from contextlib import ContextDecorator

from flask import Flask, request
from werkzeug.serving import make_server


class WebhookReaper(ContextDecorator):

    stop_log = (
        "Process stopped after receiving request from `{addr}` address."
    )

    def __init__(
        self, exit_callback, port=5342,
        logger=sys.stdout.write,
    ):
        self.exit_callback = exit_callback
        self.host, self.port = '127.0.0.1', port
        self.logger = logger
        self._stop_thread = None

        self.init_flask()

    def init_flask(self):
        self._app = Flask(__name__)
        self._app.add_url_rule(
            "/", endpoint=self.exit_callback.__name__,
            view_func=lambda: self._stop_process_endpoint(
                log=self.stop_log.format(addr=request.remote_addr)
            ),
        )
        self._server = make_server(self.host, self.port, self._app)
        self._app_ctx = self._app.app_context()
        self._app_ctx.push()

    def __enter__(self, *args, **kwargs):
        self.start_app()

    def __exit__(self, *args, **kwargs):
        if self._stop_thread:
            self._stop_thread.join()
        self.stop_app()

    def start_app(self):
        self._app_thread = Thread(
            target=self._server.serve_forever
        )
        self._app_thread.start()

        time.sleep(1)
        self.logger(
            f"\nRun `curl {self.host}:{self.port}` to stop the process.\n",
        )

    def stop_app(self):
        self._server.shutdown()
        self._app_thread.join()

    def _stop_process_endpoint(self, log=None):
        self._stop_thread = Thread(
            target=self.stop_process, args=(log, )
        )
        self._stop_thread.start()
        return {'message': log}

    def stop_process(self, log=None):
        self.stop_app()

        self.exit_callback()
        if self.logger:
            self.logger(f"\n{log}\n")
