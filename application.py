import os

import requests
from flask import Flask, request, abort, redirect, jsonify
from requests.exceptions import RequestException

import quicklatex

application = Flask(__name__)

slack_client_id = os.environ['SLACK_CLIENT_ID']
slack_client_secret = os.environ['SLACK_CLIENT_SECRET']
slack_verification_token = os.environ['SLACK_VERIFICATION_TOKEN']


@application.route('/ping')
def ping():
    """Return a short message so it's easy to check whether the bot is up and running"""
    return 'pong'


@application.route('/slack/oauth', methods=['GET'])
def oauth():
    """Auth a Slack team"""
    try:
        r = requests.post('https://slack.com/api/oauth.access', data={
            'client_id': slack_client_id,
            'client_secret': slack_client_secret,
            'code': request.args['code'],
        })

        if r.status_code != 200:
            abort(400)  # Bad Request
    except RequestException:
        abort(500)  # Internal Server Error

    return redirect('https://github.com/jamy015/slack-latex-bot/blob/master/SUCCESS_PAGE.md', 303)


@application.route('/slack/latex', methods=['POST'])
def slash_latex():
    """Handle an incoming LaTeX slash command from Slack"""

    if request.form.get('ssl_check') == '1':  # Slack SSL ping
        return ''  # Empty 200 OK

    if request.form['token'] != slack_verification_token:
        abort(401)  # Unauthorized

    if request.form['text'] == 'help':
        return ('Give me a LaTeX formula and I\'ll show it to the channel!\r\n\r\n'
                'Not quite ready for prime time? Just use me in the conversation with yourself!')

    try:
        image = quicklatex.quicklatex(request.form['text'], show_errors=True)
        err_attachment = None
    except ValueError as err:
        image = quicklatex.quicklatex(request.form['text'], show_errors=False)
        err_attachment = {
            'fallback': str(err),
            'color': 'warning',
            'text': str(err),
        }
    except quicklatex.HTTPError as err:
        return jsonify({
            'response_type': 'in_channel',
            'text': 'QuickLaTeX seems to be having some trouble (HTTP {}). Please try again later.'.format(err)
        })

    return jsonify({
        'response_type': 'in_channel',
        'attachments': [
            err_attachment,
            {
                'fallback': 'LaTeX',
                'text': 'LaTeX',
                'image_url': image,
            },
        ],
    })


if __name__ == "__main__":
    application.run()
