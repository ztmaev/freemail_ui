from flask import Blueprint, request

from email_handler import handle_email_send

email_api_bp = Blueprint('email_api', __name__)


@email_api_bp.route('/send', methods=['POST'])
def send_email_api():
    data = request.get_json()
    # print(data)

    data_json = {
        'sender_name': data.get('sender_name'),
        'email_subject': data.get('subject'),
        'message_content': data.get('message'),
        'message_type': data.get('message_type'),
        'footer': data.get('footer'),
        'receiver_email': data.get('receiver_email'),
        'api_key': data.get('api_key'),
    }

    return handle_email_send(data_json)
