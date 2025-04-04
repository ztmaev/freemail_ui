import datetime

from flask import Blueprint, jsonify, request, session

from config import freemail_free_limit, freemail_free_reset
from db import fetch_user, days_active, update_user, fetch_user_preferences, update_user_preferences, \
    fetch_user_email_log, \
    fetch_notifications, notif_mark_as_seen, clear_all_notifications, hash_password, check_password
from email_handler import send_account_deletion_email

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')


@profile_bp.route('/info', methods=['POST'])
def get_profile():
    uid = session['user_id']

    user_info = fetch_user(uid, 'uid')

    if user_info is None:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Extract user information from user_info
    account_created = user_info['created_at']

    user_preferences = fetch_user_preferences(uid)

    if user_preferences is not None:
        timezone = user_preferences['timezone']
        user_preference_list = {
            'email_notifications': True if int(user_preferences['email_notifications']) == 1 else False,
            'marketing_emails': True if int(user_preferences['marketing_emails']) == 1 else False,
            'security_alerts': True if int(user_preferences['security_alerts']) == 1 else False
        }


    else:
        user_preference_list = {
            'email_notifications': True,
            'marketing_emails': False,
            'security_alerts': True
        }
        timezone = 'est'

    user_days_active = days_active(account_created)

    if user_days_active is None or user_days_active < 0:
        user_days_active = 0

    # TODO
    plan = 'free'

    user_email_log = fetch_user_email_log(uid)

    if user_email_log is not None:
        emails_sent = len(user_email_log)
    else:
        emails_sent = '0'

    if user_info['has_2fa'] == 1:
        f2a_status = True
    else:
        f2a_status = False

    user_data = {
        'fullname': user_info['username'],
        'email': user_info['email'],
        'timezone': timezone,
        'f2a_status': f2a_status,
        'emails_sent': emails_sent,
        'days_active': user_days_active,
        'plan': plan,
        'notification_preferences': user_preference_list

    }

    return jsonify({
        'status': 'success',
        'message': 'Profile data retrieved successfully',
        'user': user_data
    }), 200


# Dashboard data endpoint
@profile_bp.route('/dashboard', methods=['POST'])
def dashboard_data():
    """Return dashboard data for the user dashboard using live database data"""
    uid = session['user_id']

    user_info = fetch_user(uid, 'uid')
    if user_info is None:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Fetch email logs for the last 30 days
    thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=freemail_free_reset)

    # Fetch all email logs (we'll filter and process in Python)
    email_logs = fetch_user_email_log(uid)

    if not email_logs:
        # If no logs, return default dashboard data
        return jsonify({
            'emailsSent': 0,
            'deliveryRate': 0,
            'emailsLimit': freemail_free_limit,
            'daysUntilReset': freemail_free_reset,
            'recentActivity': []
        }), 200

    # Filter logs for the last 30 days and process
    recent_activity = []
    emails_sent = 0
    failed_emails = 0

    for log in email_logs:
        # Convert created_at to datetime if it's a string
        created_at = log['created_at']
        if isinstance(created_at, str):
            created_at = datetime.datetime.fromisoformat(created_at)

        # Check if log is within the last 30 days
        if created_at >= thirty_days_ago:
            # Determine status based on is_sent and error fields
            if log['is_sent'] == 1:
                status = 'delivered'
                emails_sent += 1
            elif log['error']:
                status = 'failed'
                failed_emails += 1
            else:
                status = 'pending'

            # Prepare activity entry
            activity = {
                'id': log['id'],
                'type': 'email_sent',
                'recipient': log['receiver_email'],
                'subject': log['subject'],
                'status': status,
                'timestamp': created_at.isoformat()
            }
            recent_activity.append(activity)

    # Sort activities by timestamp (newest first)
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)

    # Calculate delivery rate
    total_processed_emails = emails_sent + failed_emails
    delivery_rate = (emails_sent / total_processed_emails * 100) if total_processed_emails > 0 else 0

    # Calculate days until reset (assuming reset is monthly)
    reset_date = datetime.datetime.now().replace(day=1) + datetime.timedelta(days=freemail_free_reset + 2)
    reset_date = reset_date.replace(day=1)
    days_until_reset = (reset_date - datetime.datetime.now()).days

    # Return the dashboard data
    return jsonify({
        'emailsSent': emails_sent,
        'deliveryRate': round(delivery_rate, 2),
        'emailsLimit': freemail_free_limit,  # Maximum 1000 emails per month
        'daysUntilReset': days_until_reset,
        'recentActivity': recent_activity[:4]  # Limit to 20 most recent activities
    }), 200


@profile_bp.route('/update', methods=['POST'])
def update_profile():
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    username = data.get('fullname')
    timezone = data.get('timezone')

    uid = session['user_id']

    user_data = fetch_user(uid, 'uid')

    if user_data is None:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    user_prefferences = fetch_user_preferences(uid)
    # print(user_prefferences)
    user_timezone = user_prefferences['timezone']

    # check for changes
    if username == user_data['username'] and timezone == user_timezone:
        message = 'No changes made'
    elif username == user_data['username'] and timezone != user_timezone:
        message = 'Timezone updated'
    elif username != user_data['username'] and timezone == user_timezone:
        message = 'Username updated'
    else:
        message = 'Username and timezone updated'

    # Update the user's profile data
    update_user(uid, {'username': username})

    update_user_preferences(uid, {'timezone': timezone})

    data = {
        'fullname': username,
        'timezone': timezone
    }

    return jsonify({
        'status': 'success',
        'message': message,
        'data': data
    }), 200


@profile_bp.route('/update-password', methods=['POST'])
def update_password():
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    # Validate that we have the required fields
    if 'currentPassword' not in data or 'newPassword' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    current_password = data['currentPassword']
    new_password = data['newPassword']

    uid = session['user_id']

    user_data = fetch_user(uid, 'uid')

    if user_data is None:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    db_password = user_data['password']

    # Verify the current password
    if check_password(current_password, db_password) is False:
        return jsonify({'status': 'error', 'message': 'Incorrect password'}), 400

    # update the password
    update_user(uid, {'password': hash_password(data['newPassword'])})

    return jsonify({
        'status': 'success',
        'message': 'Password updated'
    }), 200


@profile_bp.route('/update-notification', methods=['POST'])
def update_notification():
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    # Validate that we have the required fields
    if 'setting' not in data or 'enabled' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    uid = session['user_id']

    user_data = fetch_user(uid, 'uid')
    if user_data is None:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    setting_name = data['setting']
    is_enabled = data['enabled']

    settings_map = {
        'email_notification': 'email_notifications',
        'marketing_notification': 'marketing_emails',
        'security_notification': 'security_alerts'
    }

    if setting_name not in settings_map:
        return jsonify({'status': 'error', 'message': 'Invalid setting'}), 400

    setting_name = settings_map[setting_name]

    update_user_preferences(uid, {setting_name: is_enabled})

    return jsonify({
        'status': 'success',
        'message': f'{setting_name} have been {"enabled" if is_enabled else "disabled"}',
        'data': data
    }), 200


@profile_bp.route('/update-2fa', methods=['POST'])
def update_2fa():
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    # Validate that we have the required fields
    if 'enabled' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    # update user
    uid = session['user_id']
    user_data = fetch_user(uid, 'uid')
    if user_data is None:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    if user_data['has_2fa'] == 1:
        is_enabled = True
    else:
        is_enabled = False

    if data['enabled'] == is_enabled:
        if is_enabled:
            return jsonify({'status': 'error', 'message': '2FA is already enabled'}), 400
        else:
            return jsonify({'status': 'error', 'message': '2FA is already disabled'}), 400

    # update user
    if is_enabled:
        update_user(uid, {'has_2fa': 0})
        message = '2FA has been disabled'
    else:
        update_user(uid, {'has_2fa': 1})
        message = '2FA has been enabled'

    return jsonify({
        'status': 'success',
        'message': message
    }), 200


@profile_bp.route('/delete-account', methods=['POST'])
def delete_account():
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    # Validate that we have the required fields
    if 'password' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    uid = session['user_id']

    user_data = fetch_user(uid, 'uid')

    if user_data is None:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Verify the password
    if check_password(data['password'], user_data['password']) is False:
        return jsonify({'status': 'error', 'message': 'Incorrect password'}), 400

    update_user(uid, {'is_await_delete': True})

    send_account_deletion_email(user_data['email'], user_data['username'])

    session.clear()

    return jsonify({
        'status': 'success',
        'action': 'retry',
        'message': 'Your account has been scheduled for deletion. You will be logged out shortly.'
    }), 200


# Notifications
@profile_bp.route('/notifications', methods=['POST'])
def get_notifications():
    uid = session['user_id']

    notifications = fetch_notifications(uid)

    unseen_notifications = [notif for notif in notifications if not notif['is_seen']]

    return jsonify({
        'status': 'success',
        'message': 'Notifications retrieved successfully',
        'notifications': unseen_notifications
    }), 200


@profile_bp.route('/mark-notification-seen', methods=['POST'])
def mark_notification_seen():
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    # Validate that we have the required fields
    if 'notification_id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    uid = session['user_id']
    notification_id = data['notification_id']

    notif_mark_as_seen(uid, notification_id)

    return jsonify({
        'status': 'success',
        'message': 'Notification marked as seen'
    }), 200


@profile_bp.route('/clear-notifications', methods=['POST'])
def clear_notifications():
    uid = session['user_id']

    result = clear_all_notifications(uid)

    if result:
        return jsonify({
            'status': 'success',
            'message': 'All notifications cleared'
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to clear notifications'
        }), 500


# Email history endpoint
@profile_bp.route('/email-history', methods=['POST'])
def email_history():
    """Return email history with search and pagination"""
    uid = session['user_id']
    data = request.get_json()

    # Get pagination parameters
    page = data.get('page', 1)
    items_per_page = data.get('items_per_page', 10)

    # Get search parameters
    search_query = data.get('search', None)
    status_filter = data.get('status', None)
    date_from = data.get('date_from', None)
    date_to = data.get('date_to', None)

    # Fetch email logs with search parameters
    email_logs = fetch_user_email_log(
        uid,
        number_of_items=items_per_page,
        page=page,
        search_query=search_query,
        status=status_filter,
        date_from=date_from,
        date_to=date_to
    )

    if not email_logs:
        return jsonify({
            'status': 'success',
            'message': 'No email logs found',
            'emails': [],
            'total_pages': 0,
            'current_page': page
        }), 200

    # Process email logs to add status
    processed_logs = []
    for log in email_logs:
        # Determine status based on is_sent and error fields
        if log['is_sent'] == 1:
            status = 'delivered'
        elif log['error']:
            status = 'failed'
        else:
            status = 'pending'

        # Format created_at if it's a string
        created_at = log['created_at']
        if isinstance(created_at, str):
            try:
                # Try to parse as ISO format
                created_at = datetime.datetime.fromisoformat(created_at).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                # If that fails, keep as is
                pass

        # Create processed log entry
        processed_log = {
            'id': log['id'],
            'recipient': log['receiver_email'],
            'sender': log['sender_name'],
            'subject': log['subject'],
            'content': log['content'],
            'status': status,
            'error': log['error'],
            'timestamp': created_at,
            'email_type': log['email_type'],
            'email_footer': log['footer']
        }
        processed_logs.append(processed_log)

    # Get total count for pagination
    # This is a simplified approach - for a real app, you'd want to do a COUNT query
    # For now, we'll estimate based on the current page and items per page
    total_pages = max(1, page)  # At least the current page exists

    return jsonify({
        'status': 'success',
        'message': 'Email logs retrieved successfully',
        'emails': processed_logs,
        'total_pages': total_pages,
        'current_page': page
    }), 200
