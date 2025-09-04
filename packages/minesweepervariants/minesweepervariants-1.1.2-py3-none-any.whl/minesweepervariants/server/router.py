from flask import Flask, redirect
from flask_cors import CORS

from .session import SessionManager

from .config import CORS_resources, github_web
from .model import Model

__all__ = ["create_app"]

def create_app(sm: SessionManager, model: type[Model]) -> Flask:
    app = Flask('Minesweeper Variants')
    CORS(app, resources=CORS_resources, supports_credentials=True)

    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Referrer-Policy'] = 'unsafe-url'
        if 'Access-Control-Allow-Credentials' in response.headers:
            try:
                del response.headers['Access-Control-Allow-Credentials']
            except Exception:
                pass
        return response

    @app.route('/')
    def root():
        return redirect(github_web)

    app.add_url_rule('/api/new', 'generate_board', sm.gen_wrapper(lambda _: True, lambda x,*_:x.game.create_schedule()[0])(model.generate_board), methods=['GET', 'POST'])
    app.add_url_rule('/api/metadata', 'metadata', sm.gen_wrapper()(model.metadata), methods=['GET', 'POST'])
    app.add_url_rule('/api/click', 'click', sm.gen_wrapper()(model.click), methods=['GET', 'POST'])
    app.add_url_rule('/api/hint', 'hint_post', sm.gen_wrapper(lambda m: m.game.last_hint[0] != m.game.board)(model.hint_post), methods=['GET', 'POST'])
    app.add_url_rule('/api/rules', 'get_rule_list', sm.gen_wrapper()(model.get_rule_list), methods=['GET', 'POST'])
    app.add_url_rule('/api/reset', 'reset', sm.gen_wrapper()(model.reset), methods=['GET', 'POST'])
    app.add_url_rule('/api/new_token', 'gen_token_route', sm.gen_token_route(), methods=['GET', 'POST'])
    app.add_url_rule('/api/check', 'gen_check', sm.gen_check(), methods=['GET', 'POST'])
    app.add_url_rule('/api/host_dual', 'gen_host_dual', sm.gen_host_dual(), methods=['GET', 'POST'])
    app.add_url_rule('/api/dual_register', 'dual_register', sm.dual_register, methods=['GET', 'POST'])
    app.add_url_rule('/api/dual_connect', 'dual_connect', sm.dual_connect, methods=['GET', 'POST'])

    return app