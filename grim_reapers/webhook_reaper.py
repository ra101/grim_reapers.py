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
        tunning=None, subdomain=None,
        logger=sys.stdout.write,
    ):
        self.exit_callback = exit_callback
        self.host, self.port = '127.0.0.1', port
        self.tunning, self.subdomain = tunning, subdomain
        self.logger = logger
        self._stop_thread = None

        self.init_flask()

        if tunning is None:
            self.logger(
                "\nTo create publicly accessible url using `localtunnel.me`. "
                "Install `py-localtunnel` package and pass `tunning=True` "
                "argument during initialization of Webhook Reaper. "
                "Pass `tunning=False` to remove this message.\n"
            )
        elif tunning:
            self.init_tunnel()

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

    def init_tunnel(self):
        from py_localtunnel.tunnel import Tunnel


        self._tunnel = Tunnel()
        self.url = self._tunnel.get_url(self.subdomain)

    def __enter__(self, *args, **kwargs):
        self.start_app_and_tunnel()

    def __exit__(self, *args, **kwargs):
        if self._stop_thread:
            self._stop_thread.join()
        self.stop_app_and_tunnel()

    def start_app_and_tunnel(self):
        self._app_thread = Thread(
            target=self._server.serve_forever
        )
        self._app_thread.start()

        time.sleep(1)
        self.logger(
            f"\nRun `curl {self.host}:{self.port}` to stop the process.\n",
        )

        if not self.tunning:
            return

        self._tunnel_thread = Thread(
            target=self._tunnel.create_tunnel,
            args=(self.port, self.host)
        )
        self._tunnel_thread.start()
        time.sleep(1)
        self.logger(
            f'\nUse `curl -L {self.url} -H "user-agent:webhook-reaper"`'
            ' to stop the process.\n',
        )

    def stop_app_and_tunnel(self):
        self._server.shutdown()
        self._app_thread.join()

        if self.tunning:
            self._tunnel.stop_tunnel()
            self._tunnel_thread.join()

    def _stop_process_endpoint(self, log=None):
        self._stop_thread = Thread(
            target=self.stop_process, args=(log, )
        )
        self._stop_thread.start()
        return {'message': log}

    def stop_process(self, log=None):
        self.stop_app_and_tunnel()

        self.exit_callback()
        if self.logger:
            self.logger(f"\n{log}\n")
