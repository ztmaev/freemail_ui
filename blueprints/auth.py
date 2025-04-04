from flask import Blueprint, redirect, url_for, request, session, jsonify

from db import generate_2fa_code, save_user, save_auth_code, generate_uid, fetch_user, fetch_auth_code, update_user, \
    delete_auth_code, add_log, add_notification, current_time, compare_timestamps, hash_password, check_password, \
    decode_url
from email_handler import send_2fa_email, send_password_change_email, send_account_deletion_cancel_email, \
    send_account_cancel_deletion_email

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    email_username = data.get('email')
    password = data.get('password')
    remember_me = data.get('remember_me', False)

    if not email_username or not password:
        return jsonify({'status': 'error', 'message': 'Email/username and password are required'}), 400

    # Determine if input is email or username
    login_type = 'email' if '@' in email_username else 'username'

    # Fetch user from database
    user_info = fetch_user(email_username, login_type)

    if not user_info:
        return jsonify({'status': 'error', 'message': 'Invalid email/username or password'}), 401

    # Verify password
    if check_password(password, user_info['password']) is False:
        return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

    # Check if user is active
    if not user_info['is_active']:
        return jsonify({'status': 'error', 'action': 'register',
                        'message': 'Account creation was not completed, please register again'}), 403

    if user_info['is_await_delete']:
        code = generate_2fa_code()
        save_auth_code(user_info['uid'], code, 'recover', user_info['uid'])

        email_sent = send_account_cancel_deletion_email(code, user_info['uid'], user_info['email'],
                                                        user_info['username'])

        return jsonify({
            'status': 'info',
            'action': '2fa_recover',
            'session_token': user_info['uid'],
            'message': 'Your account is awaiting deletion, please enter the code sent to your email to recover your account'
        })

    # Check if user has 2FA enabled
    if user_info['has_2fa']:
        # Generate and save 2FA code
        auth_code = generate_2fa_code()
        save_auth_code(user_info['uid'], auth_code, 'login', user_info['uid'])

        # Send 2FA code via email
        email_sent = send_2fa_email(auth_code, user_info['email'], 'login')

        return jsonify({
            'status': 'info',
            'action': '2fa',
            'session_token': user_info['uid'],
            'message': 'Enter the code sent to your email'
        })
    else:
        # Set session data
        session['user_id'] = user_info['uid']
        session['username'] = user_info['username']
        session['email'] = user_info['email']
        session['role'] = user_info['role']

        # Add log entry
        add_log(user_info['uid'], {'title': 'Login', 'message': 'Logged in'})

        return jsonify({
            'status': 'success',
            'message': 'Logged in successfully'
        })


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    # Dummy validation logic
    if not data.get('email') or not data.get('username') or not data.get('password'):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields'
        }), 400

    # print(data)
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    # verify if email already exists
    if fetch_user(email, 'email'):
        if fetch_user(email, 'email')['is_active']:
            return jsonify({
                'status': 'error',
                'message': 'Account using this email already exists'
            }), 400

    # verify if username already exists
    if fetch_user(username, 'username'):
        if fetch_user(username, 'username')['is_active']:
            return jsonify({
                'status': 'error',
                'message': 'Username already taken'
            }), 400

    uid = generate_uid()
    auth_code = generate_2fa_code()

    user_info = {
        'email': email,
        'username': username,
        'password': password,
        'uid': uid,
        'role': 'user',
        'is_active': False,
        'has_2fa': False,
        'is_await_delete': False,
        'is_deleted': False,
        'deleted_at': None,
        'avatar_url': None,
    }

    try:
        save_user(user_info)
        save_auth_code(uid, auth_code, 'register', uid)

        # Send verification email
        email_sent = send_2fa_email(auth_code, email, 'register')

        return jsonify({
            'status': 'info',
            'session_token': uid,
            'message': 'Check your email for a verification code'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@auth_bp.route('/logout')
def logout():
    uid = session.get('user_id')
    if uid:
        user_info = fetch_user(uid, 'uid')
        if user_info:
            add_log(user_info['uid'], {'title': 'Logout', 'message': 'Logged out'})

    # clear session data
    session.clear()
    return redirect(url_for('home'))


@auth_bp.route('/recover/<path:encode>', methods=['GET'])
def recover_account(encode):
    decoded = decode_url(encode)
    parts = decoded.split('/')
    uid, code = parts

    # Fetch the auth code from database
    auth_code_info = fetch_auth_code(uid, 'recover')

    if not auth_code_info:
        return jsonify({'status': 'error', 'message': 'Invalid recovery link'}), 400

    # Verify the code
    if auth_code_info['code'] != code:
        return jsonify({'status': 'error', 'message': 'Invalid recovery link'}), 400

    user_info = fetch_user(uid, 'uid')

    if not user_info:
        return jsonify({'status': 'error', 'message': 'Invalid recovery link'}), 400

    # Update user to not await deletion
    update_user(user_info['uid'], {'is_await_delete': False})

    # Delete the auth code after successful recovery
    delete_auth_code(user_info['uid'], 'recover')

    # Add log entry
    add_log(user_info['uid'], {'title': 'Account Recovery', 'message': 'Account recovered from deletion'})

    # Add notification
    add_notification(user_info['uid'], 'system', 'Account Restored!',
                     'Welcome back! Your account has been successfully restored and is now fully accessible again.')

    # Send email notification about account recovery
    send_account_deletion_cancel_email(user_info['email'], user_info['username'])

    # Set session data
    session['user_id'] = user_info['uid']
    session['username'] = user_info['username']
    session['email'] = user_info['email']
    session['role'] = user_info['role']

    return redirect(url_for('dashboard', page='dashboard'))


@auth_bp.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    form_type = data.get('form_type')
    code = data.get('code')
    session_token = data.get('session_token')

    if not form_type or not code or not session_token:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    if form_type not in ['login', 'register', 'forgot', 'recover']:
        return jsonify({'status': 'error', 'message': 'Invalid form type'}), 400

    # uppercase and no spaces
    code = code.upper()
    code = code.replace(' ', '')

    # check if code exists
    auth_code_info = fetch_auth_code(session_token, form_type)

    # print("auth code info", auth_code_info)

    if not auth_code_info:
        return jsonify({'status': 'error', 'message': 'Invalid verification code'}), 400

    # check expiration
    current_time_now = current_time()

    # print("current time", current_time_now)
    # print("created at", auth_code_info['created_at'])

    time_difference = compare_timestamps(current_time_now, auth_code_info['created_at'])
    if time_difference > 300:
        return jsonify({'status': 'error', 'message': 'Verification code expired'}), 400

    # check validity
    if auth_code_info['code'] != code:
        return jsonify({'status': 'error', 'message': 'Invalid verification code'}), 400

    # Fetch user from session token
    user_info = fetch_user(session_token, 'uid')

    if not user_info:
        return jsonify({'status': 'error', 'message': 'Invalid session'}), 401

    username = user_info['username']

    # Handle different form types
    if form_type == 'login':
        # Set session data
        session['user_id'] = user_info['uid']
        session['username'] = user_info['username']
        session['email'] = user_info['email']
        session['role'] = user_info['role']

        # Add log entry
        add_log(user_info['uid'], {'title': 'Login', 'message': 'User logged in with 2FA'})

    elif form_type == 'register':
        # Activate user account
        update_user(user_info['uid'], {'is_active': True})

        # Set session data
        session['user_id'] = user_info['uid']
        session['username'] = user_info['username']
        session['email'] = user_info['email']
        session['role'] = user_info['role']

        # Add log entry
        add_log(user_info['uid'], {'title': 'Registration', 'message': 'User account activated'})

        # Add welcome notification
        add_notification(user_info['uid'], 'system', 'Welcome to Freemail!',
                         f"Hello {user_info['username']}, welcome to Freemail!")

    elif form_type == 'forgot':
        session['user_id'] = user_info['uid']
        session['username'] = user_info['username']
        session['email'] = user_info['email']
        session['role'] = user_info['role']

        return jsonify({
            'status': 'info',
            'action': 'new_password',
            'message': 'Enter your new password'
        })

    elif form_type == 'recover':
        update_user(user_info['uid'], {'is_await_delete': False})
        # Add log entry
        add_log(user_info['uid'], {'title': 'Account Recovery', 'message': 'Account recovered from deletion'})

        # Add notification
        add_notification(user_info['uid'], 'system', 'Account Restored!',
                         'Welcome back! Your account has been successfully restored and is now fully accessible again.')

        # Send email notification about account recovery
        send_account_deletion_cancel_email(user_info['email'], user_info['username'])

        # Set session data
        session['user_id'] = user_info['uid']
        session['username'] = user_info['username']
        session['email'] = user_info['email']
        session['role'] = user_info['role']

        return jsonify({
            'status': 'success',
            'message': f'Welcome back {username}. Account recovered successfully'
        })

    # Delete the auth code after successful verification
    delete_auth_code(user_info['uid'], form_type)

    return jsonify({
        'status': 'success',
        'message': 'Verification successful'
    })


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    email = data.get('email')

    if not email:
        return jsonify({'status': 'error', 'message': 'Email is required'}), 400

    # Check if user exists
    user_info = fetch_user(email, 'email')

    if not user_info:
        # For security reasons, don't reveal that the email doesn't exist
        # Just pretend we sent an email
        return jsonify({
            'status': 'info',
            'action': '2fa',
            'message': 'Password reset link sent to your email'
        })

    # Generate reset code
    reset_code = generate_2fa_code()

    # Save reset code to database
    save_auth_code(user_info['uid'], reset_code, 'forgot', user_info['uid'])

    # Send password reset code via email
    email_sent = send_2fa_email(reset_code, user_info['email'], 'forgot')

    # Add log entry
    add_log(user_info['uid'], {'title': 'Password Reset', 'message': 'Password reset requested'})

    return jsonify({
        'status': 'info',
        'action': '2fa',
        'session_token': user_info['uid'],
        'message': 'Password reset link sent to your email'
    })


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    new_password = data.get('password')
    confirm_password = data.get('confirmPassword')

    if not new_password or not confirm_password:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    if new_password != confirm_password:
        return jsonify({'status': 'error', 'message': 'Passwords do not match'}), 400

    uid = session.get('user_id')
    user_info = fetch_user(uid, 'uid')

    # Update the user's password
    update_user(uid, {'password': hash_password(new_password)})

    # Add log entry
    add_log(user_info['uid'], {'title': 'Password Reset', 'message': 'Password reset completed'})

    # Add notification
    add_notification(user_info['uid'], 'system', 'Password Updated',
                     'Your password has been successfully reset. Your account is now secure with your new credentials.')

    # Send email notification about password change
    send_password_change_email(user_info['email'], user_info['username'])

    return jsonify({
        'status': 'success',
        'message': 'Password reset successful'
    })
