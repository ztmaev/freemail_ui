from flask import Blueprint, jsonify, request, session

from db import fetch_api_key, verify_api_key, delete_api_key, \
    generate_api_key, add_api_key, add_log, add_notification
from email_handler import handle_email_send

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/status')
def status():
    return jsonify({'status': 'ok'})


@api_bp.route('/test_console', methods=['POST'])
def test_console():
    # Get form data from request
    data = request.get_json()

    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided!'}), 400

    # 'senderName', 'subject', 'message', 'receiverEmail'
    if data['senderName'] is None or data['subject'] is None or data['message'] is None or data[
        'receiverEmail'] is None:
        return jsonify({'status': 'error', 'message': 'Missing data!'}), 400

    uid = session['user_id']
    if uid is None:
        return jsonify({'status': 'error', 'message': 'user not found'}), 400

    # get api key
    api_key = fetch_api_key(uid)
    if api_key is None:
        return jsonify({'status': 'error', 'message': 'You don\'t have an api key, generate one'}), 400

    # verify api key
    active_api_key = verify_api_key(api_key)

    if active_api_key is None:
        return jsonify({'status': 'error', 'message': 'Your api key is not active'}), 400

    # send email
    email_data = {
        'sender_name': data['senderName'],
        'email_subject': data['subject'],
        'message_type': data['messageType'],
        'message_content': data['message'],
        'receiver_email': data['receiverEmail'],
        'footer': data['footer'],
        'api_key': api_key
    }

    handle_email_send(email_data)

    add_log(uid, {'title': 'Email Sent', 'message': 'Sent email via web console'})
    return jsonify({'status': 'success', 'message': 'Email sent successfully'}), 200


@api_bp.route('/get_api_key', methods=['POST'])
def getapikey():
    uid = session['user_id']
    if uid is None:
        return jsonify({'status': 'error', 'message': 'user not found'}), 400

    api_key = fetch_api_key(uid)
    if api_key is None:
        return jsonify(
            {'status': 'success', 'message': "You don't have an api key, generate one", 'api_key': 'None'}), 400

    add_log(uid, {'title': 'API Key', 'message': 'API key fetched'})
    return jsonify({'status': 'success', 'message': 'API key fetched successfully', 'api_key': api_key}), 200


@api_bp.route('/generate_api_key', methods=['POST'])
def generate_api_key_endpoint():
    uid = session['user_id']
    if uid is None:
        return jsonify({'status': 'error', 'message': 'user not found'}), 400

    # check if user has an api key
    api_key = fetch_api_key(uid)

    if api_key is not None:
        return jsonify({'status': 'error', 'message': 'You already have an api key, regenerate it'}), 400

    # Generate api key
    api_key = generate_api_key()

    # add api key to database
    add_api_key(uid, api_key)

    # Return the API key in the format expected by the client
    add_log(uid, {'title': 'API Key', 'message': 'Generated API key'})
    add_notification(uid, 'system', 'API Key Ready!',
                     'Your new API key has been successfully generated and is ready to use. Visit the api tab for more info.')
    return jsonify({'status': 'success', 'message': 'API key regenerated successfully', 'api_key': api_key}), 200


@api_bp.route('/regenerate_api_key', methods=['POST'])
def regenerate_api_key():
    uid = session['user_id']
    if uid is None:
        return jsonify({'status': 'error', 'message': 'user not found'}), 400

    # check if user has an api key
    api_key = fetch_api_key(uid)
    if api_key is None:
        return jsonify({'status': 'error', 'message': 'You don\'t have an api key, generate one'}), 400

    # remove api key from database
    delete_api_key(uid, api_key)

    # Generate api key
    api_key = generate_api_key()

    # add api key to database
    add_api_key(uid, api_key)
    add_log(uid, {'title': 'API Key', 'message': 'Regenerated API key'})
    add_notification(uid, 'system', 'API Key Updated',
                     'Your API key has been successfully regenerated. For security, any applications using your previous key will need to be updated with this new key.')
    return jsonify({'status': 'success', 'message': 'API key regenerated successfully', 'api_key': api_key}), 200
