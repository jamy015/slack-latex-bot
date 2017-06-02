import latex
import os
from flask import Flask, request, abort, jsonify

app = Flask(__name__)

slack_verification_token = os.environ["SLACK_VERIFICATION_TOKEN"]


@app.route('/slack/latex', methods=['POST'])
def slash_latex():
    """Handle an incoming LaTeX slash command from Slack"""

    if request.form['token'] != slack_verification_token:
        abort(401)  # Unauthorized

    try:
        image = latex.to_image_url(request.form['text'])
    except ValueError as err:
        return jsonify({
            'response_type': 'in_channel',
            'attachments': [{
                'fallback': '*LaTeX Error:* {}'.format(err),
                'color': 'danger',
                'fields': [{
                    'title': 'LaTeX Error',
                    'value': str(err),
                }],
            }],
        })

    return jsonify({
        'response_type': 'in_channel',
        'attachments': [{
            'fallback': 'LaTeX',
            'text': 'LaTeX',
            'image_url': image,
        }],
    })


if __name__ == "__main__":
    app.run()
