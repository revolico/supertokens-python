import json

from _pytest.fixtures import fixture
from flask import Flask, jsonify, make_response, request

from supertokens_python.exceptions import SuperTokensError
from supertokens_python.framework.flask.flask_middleware import Middleware, error_handler
from supertokens_python import init, session
from supertokens_python.session.sync import create_new_session, refresh_session, get_session, revoke_session
from tests.Flask.utils import extract_all_cookies


def setup_function(f):
    reset()
    clean_st()
    setup_st()


def teardown_function(f):
    reset()
    clean_st()


# @fixture(scope='function')
# def app():
#     app = Flask(__name__)
#     supertokens = Supertokens(app)
#     init({
#         'supertokens': {
#             'connection_uri': "http://localhost:3567",
#         },
#         'framework' : 'Flask',
#         'app_info': {
#             'app_name': "SuperTokens Demo",
#             'api_domain': "api.supertokens.io",
#             'website_domain': "supertokens.io",
#             'api_base_path': "/auth"
#         },
#         'recipe_list': [session.init(
#             {
#                 'anti_csrf': 'VIA_TOKEN',
#                 'cookie_domain': 'supertokens.io'
#             }
#         )],
#     })
#
#     def ff(e):
#         return jsonify({'error_msg': 'try refresh token'}), 401
#
#     supertokens.set_try_refresh_token_error_handler(ff)
#
#     @app.route('/login')
#     def login():
#         user_id = 'userId'
#         response = make_response(jsonify({'userId': user_id}), 200)
#         create_new_session(response, user_id, {}, {})
#         return response
#
#     @app.route('/refresh', methods=['POST'])
#     def refresh():
#         response = make_response(jsonify({}))
#         refresh_session(response)
#         return response
#
#     @app.route('/info', methods=['GET', 'OPTIONS'])
#     def info():
#         if request.method == 'OPTIONS':
#             return jsonify({'method': 'option'})
#         response = make_response(jsonify({}))
#         get_session(response, True)
#         return response
#
#     @app.route('/handle', methods=['GET', 'OPTIONS'])
#     def handle_api():
#         if request.method == 'OPTIONS':
#             return jsonify({'method': 'option'})
#         session = get_session(None, False)
#         return jsonify({'s': session.get_handle()})
#
#     @app.route('/logout', methods=['POST'])
#     def logout():
#         response = make_response(jsonify({}))
#         supertokens_session = get_session(response, True)
#         supertokens_session.revoke_session()
#         return response
#
#     return app
from tests.utils import set_key_value_in_config, TEST_COOKIE_SAME_SITE_CONFIG_KEY, TEST_ACCESS_TOKEN_MAX_AGE_CONFIG_KEY, \
    TEST_ACCESS_TOKEN_MAX_AGE_VALUE, TEST_ACCESS_TOKEN_PATH_CONFIG_KEY, TEST_ACCESS_TOKEN_PATH_VALUE, \
    TEST_COOKIE_DOMAIN_CONFIG_KEY, TEST_COOKIE_DOMAIN_VALUE, TEST_REFRESH_TOKEN_MAX_AGE_CONFIG_KEY, \
    TEST_REFRESH_TOKEN_MAX_AGE_VALUE, TEST_REFRESH_TOKEN_PATH_CONFIG_KEY, TEST_REFRESH_TOKEN_PATH_KEY_VALUE, \
    TEST_COOKIE_SECURE_CONFIG_KEY, TEST_DRIVER_CONFIG_COOKIE_DOMAIN, \
    TEST_DRIVER_CONFIG_ACCESS_TOKEN_PATH, TEST_DRIVER_CONFIG_REFRESH_TOKEN_PATH, TEST_DRIVER_CONFIG_COOKIE_SAME_SITE, \
    start_st, reset, clean_st, setup_st


@fixture(scope='function')
def driver_config_app():
    app = Flask(__name__)
    app.app_context().push()
    app.wsgi_app = Middleware(app.wsgi_app)

    app.register_error_handler(SuperTokensError, error_handler)

    app.testing = True
    init({
        'supertokens': {
            'connection_uri': "http://localhost:3567",
        },
        'framework': 'Flask',
        'app_info': {
            'app_name': "SuperTokens Demo",
            'api_domain': "api.supertokens.io",
            'website_domain': "supertokens.io",
            'api_base_path': "/auth"
        },
        'recipe_list': [session.init(
            {
                'anti_csrf': 'VIA_TOKEN',
                'cookie_domain': 'supertokens.io'
            }
        )],
    })

    @app.route('/test')
    def t():
        print(request)
        return jsonify({})

    @app.route('/login')
    def login():
        user_id = 'userId'
        print(request)

        session = create_new_session(request, user_id, {}, {})
        response = make_response(jsonify({'userId': user_id, 'session': 'ssss'}), 200)

        return response

    @app.route('/refresh', methods=['POST'])
    def custom_refresh():
        response = make_response(jsonify({}))
        refresh_session(request)
        return response

    @app.route('/custom/info', methods=['GET', 'OPTIONS'])
    def custom_info():
        if request.method == 'OPTIONS':
            return jsonify({'method': 'option'})
        response = make_response(jsonify({}))
        get_session(response, True)
        return response

    @app.route('/custom/handle', methods=['GET', 'OPTIONS'])
    def custom_handle_api():
        if request.method == 'OPTIONS':
            return jsonify({'method': 'option'})
        session = get_session(None, False)
        return jsonify({'s': session.get_handle()})

    @app.route('/logout', methods=['POST'])
    def custom_logout():
        response = make_response(jsonify({}))
        supertokens_session = get_session(request, True)
        revoke_session(supertokens_session['user_id'])
        return response

    return app


def test_cookie_login_and_refresh(driver_config_app):
    start_st()

    set_key_value_in_config(
        TEST_COOKIE_SAME_SITE_CONFIG_KEY,
        'None')
    set_key_value_in_config(
        TEST_ACCESS_TOKEN_MAX_AGE_CONFIG_KEY,
        TEST_ACCESS_TOKEN_MAX_AGE_VALUE)
    set_key_value_in_config(
        TEST_ACCESS_TOKEN_PATH_CONFIG_KEY,
        TEST_ACCESS_TOKEN_PATH_VALUE)
    set_key_value_in_config(
        TEST_COOKIE_DOMAIN_CONFIG_KEY,
        TEST_COOKIE_DOMAIN_VALUE)
    set_key_value_in_config(
        TEST_REFRESH_TOKEN_MAX_AGE_CONFIG_KEY,
        TEST_REFRESH_TOKEN_MAX_AGE_VALUE)
    set_key_value_in_config(
        TEST_REFRESH_TOKEN_PATH_CONFIG_KEY,
        TEST_REFRESH_TOKEN_PATH_KEY_VALUE)
    set_key_value_in_config(
        TEST_COOKIE_SECURE_CONFIG_KEY,
        False)

    response_1 = driver_config_app.test_client().get('/login')
    cookies_1 = extract_all_cookies(response_1)

    assert response_1.headers.get('anti-csrf') is not None
    assert cookies_1['sAccessToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_1['sRefreshToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_1['sIdRefreshToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_1['sAccessToken']['path'] == TEST_DRIVER_CONFIG_ACCESS_TOKEN_PATH
    assert cookies_1['sRefreshToken']['path'] == TEST_DRIVER_CONFIG_REFRESH_TOKEN_PATH
    assert cookies_1['sIdRefreshToken']['path'] == TEST_DRIVER_CONFIG_ACCESS_TOKEN_PATH
    assert cookies_1['sAccessToken']['httponly']
    assert cookies_1['sRefreshToken']['httponly']
    assert cookies_1['sIdRefreshToken']['httponly']
    assert cookies_1['sAccessToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE
    assert cookies_1['sRefreshToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE
    assert cookies_1['sIdRefreshToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE

    request_2 = driver_config_app.test_client()
    request_2.set_cookie(
        'localhost',
        'sRefreshToken',
        cookies_1['sRefreshToken']['value'])
    response_2 = request_2.post('/refresh', headers={
        'anti-csrf': response_1.headers.get('anti-csrf')})
    cookies_2 = extract_all_cookies(response_2)
    assert cookies_1['sAccessToken']['value'] != cookies_2['sAccessToken']['value']
    assert cookies_1['sRefreshToken']['value'] != cookies_2['sRefreshToken']['value']
    assert cookies_1['sIdRefreshToken']['value'] != cookies_2['sIdRefreshToken']['value']
    assert response_2.headers.get('anti-csrf') is not None
    assert cookies_2['sAccessToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_2['sRefreshToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_2['sIdRefreshToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_2['sAccessToken']['path'] == TEST_DRIVER_CONFIG_ACCESS_TOKEN_PATH
    assert cookies_2['sRefreshToken']['path'] == TEST_DRIVER_CONFIG_REFRESH_TOKEN_PATH
    assert cookies_2['sIdRefreshToken']['path'] == TEST_DRIVER_CONFIG_ACCESS_TOKEN_PATH
    assert cookies_2['sAccessToken']['httponly']
    assert cookies_2['sRefreshToken']['httponly']
    assert cookies_2['sIdRefreshToken']['httponly']
    assert cookies_2['sAccessToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE
    assert cookies_2['sRefreshToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE
    assert cookies_2['sIdRefreshToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE


def test_login_refresh_no_csrf(driver_config_app):
    start_st()

    set_key_value_in_config(
        TEST_COOKIE_SAME_SITE_CONFIG_KEY,
        'None')
    set_key_value_in_config(
        TEST_ACCESS_TOKEN_MAX_AGE_CONFIG_KEY,
        TEST_ACCESS_TOKEN_MAX_AGE_VALUE)
    set_key_value_in_config(
        TEST_ACCESS_TOKEN_PATH_CONFIG_KEY,
        TEST_ACCESS_TOKEN_PATH_VALUE)
    set_key_value_in_config(
        TEST_COOKIE_DOMAIN_CONFIG_KEY,
        TEST_COOKIE_DOMAIN_VALUE)
    set_key_value_in_config(
        TEST_REFRESH_TOKEN_MAX_AGE_CONFIG_KEY,
        TEST_REFRESH_TOKEN_MAX_AGE_VALUE)
    set_key_value_in_config(
        TEST_REFRESH_TOKEN_PATH_CONFIG_KEY,
        TEST_REFRESH_TOKEN_PATH_KEY_VALUE)
    set_key_value_in_config(
        TEST_COOKIE_SECURE_CONFIG_KEY,
        False)

    response_1 = driver_config_app.test_client().get('/login')
    cookies_1 = extract_all_cookies(response_1)

    assert response_1.headers.get('anti-csrf') is not None
    assert cookies_1['sAccessToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_1['sRefreshToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_1['sIdRefreshToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_1['sAccessToken']['path'] == TEST_DRIVER_CONFIG_ACCESS_TOKEN_PATH
    assert cookies_1['sRefreshToken']['path'] == TEST_DRIVER_CONFIG_REFRESH_TOKEN_PATH
    assert cookies_1['sIdRefreshToken']['path'] == TEST_DRIVER_CONFIG_ACCESS_TOKEN_PATH
    assert cookies_1['sAccessToken']['httponly']
    assert cookies_1['sRefreshToken']['httponly']
    assert cookies_1['sIdRefreshToken']['httponly']
    assert cookies_1['sAccessToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE
    assert cookies_1['sRefreshToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE
    assert cookies_1['sIdRefreshToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE

    test_client = driver_config_app.test_client()
    test_client.set_cookie('localhost', 'sRefreshToken', cookies_1['sRefreshToken']['value'])
    test_client.set_cookie('localhost', 'sIdRefreshToken', cookies_1['sIdRefreshToken']['value'])

    # post with csrf token -> no error
    result = test_client.post('/refresh', headers={
        'anti-csrf': response_1.headers.get('anti-csrf')})
    assert result.status_code == 200

    # post with csrf token -> should be error with status code 401
    result = test_client.post('/refresh')
    assert result.status_code == 401


def test_login_logout(driver_config_app):
    start_st()

    set_key_value_in_config(
        TEST_COOKIE_SAME_SITE_CONFIG_KEY,
        'None')
    set_key_value_in_config(
        TEST_ACCESS_TOKEN_MAX_AGE_CONFIG_KEY,
        TEST_ACCESS_TOKEN_MAX_AGE_VALUE)
    set_key_value_in_config(
        TEST_ACCESS_TOKEN_PATH_CONFIG_KEY,
        TEST_ACCESS_TOKEN_PATH_VALUE)
    set_key_value_in_config(
        TEST_COOKIE_DOMAIN_CONFIG_KEY,
        TEST_COOKIE_DOMAIN_VALUE)
    set_key_value_in_config(
        TEST_REFRESH_TOKEN_MAX_AGE_CONFIG_KEY,
        TEST_REFRESH_TOKEN_MAX_AGE_VALUE)
    set_key_value_in_config(
        TEST_REFRESH_TOKEN_PATH_CONFIG_KEY,
        TEST_REFRESH_TOKEN_PATH_KEY_VALUE)
    set_key_value_in_config(
        TEST_COOKIE_SECURE_CONFIG_KEY,
        False)

    response_1 = driver_config_app.test_client().get('/login')
    cookies_1 = extract_all_cookies(response_1)

    assert response_1.headers.get('anti-csrf') is not None
    assert cookies_1['sAccessToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_1['sRefreshToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_1['sIdRefreshToken']['domain'] == TEST_DRIVER_CONFIG_COOKIE_DOMAIN
    assert cookies_1['sAccessToken']['path'] == TEST_DRIVER_CONFIG_ACCESS_TOKEN_PATH
    assert cookies_1['sRefreshToken']['path'] == TEST_DRIVER_CONFIG_REFRESH_TOKEN_PATH
    assert cookies_1['sIdRefreshToken']['path'] == TEST_DRIVER_CONFIG_ACCESS_TOKEN_PATH
    assert cookies_1['sAccessToken']['httponly']
    assert cookies_1['sRefreshToken']['httponly']
    assert cookies_1['sIdRefreshToken']['httponly']
    assert cookies_1['sAccessToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE
    assert cookies_1['sRefreshToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE
    assert cookies_1['sIdRefreshToken']['samesite'] == TEST_DRIVER_CONFIG_COOKIE_SAME_SITE

    test_client = driver_config_app.test_client()
    test_client.set_cookie('localhost', 'sAccessToken', cookies_1['sAccessToken']['value'])
    test_client.set_cookie('localhost', 'sIdRefreshToken', cookies_1['sIdRefreshToken']['value'])

    response_2 = test_client.post('/logout',
                                  headers={
                                      'anti-csrf': response_1.headers.get('anti-csrf')
                                  }
                                  )

    cookies_2 = extract_all_cookies(response_2)
    assert cookies_2 == {}

    response_3 = test_client.post('/logout',
                                  headers={
                                      'anti-csrf': response_1.headers.get('anti-csrf')
                                  }
                                  )

    assert response_3.status_code == 200

