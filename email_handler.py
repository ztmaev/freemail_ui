import datetime
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import email_host, email_password, email_username, email_port, freemail_footer, email_sender_name, \
    project_name, project_url, freemail_free_limit, freemail_free_reset
from db import verify_api_key, save_email_log, encode_url, fetch_uid, add_log, fetch_user_email_log
# Import email templates
from email_templates import (
    login_email_template, register_email_template, reset_email_template,
    change_email_template, account_recovery_template,
    email_change_template, account_deletion_template, info_template
)


def handle_email_send(data_json):
    # Verify API key
    active_api_key = verify_api_key(data_json['api_key'])
    if not active_api_key[0]:
        # print("error", active_api_key[1])
        return json.dumps({'status': 'error', 'message': active_api_key[1]})

    # Get user ID from API key
    api_key = data_json['api_key']
    uid = fetch_uid(api_key)

    # Rate limit 300 emails per 30 days
    thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=freemail_free_reset)
    # Fetch all email logs for this user
    email_logs = fetch_user_email_log(uid)

    # Count emails sent in the last 30 days
    recent_emails_count = 0
    if email_logs:  # Check if there are any email logs
        for log in email_logs:
            # Check if the email was sent within the last 30 days
            # Email logs have a 'created_at' field with timestamp
            if 'created_at' in log:
                # Convert string timestamp to datetime object for comparison
                log_date = datetime.datetime.strptime(log['created_at'], "%Y-%m-%d %H:%M:%S")
                if log_date >= thirty_days_ago:
                    recent_emails_count += 1

    # Check if user has reached the rate limit
    if recent_emails_count >= freemail_free_limit:
        return json.dumps({
            'status': 'error',
            'message': f'Rate limit exceeded. You can send a maximum of {freemail_free_limit} emails in a {freemail_free_reset}-day period.'
        })

    # Extract data from JSON
    api_key = data_json['api_key']
    sender_name = data_json['sender_name']
    email_subject = data_json['email_subject']
    message_content = data_json['message_content']
    message_type = data_json['message_type']
    footer = data_json['footer']
    receiver_email = data_json['receiver_email']
    # Send email
    try:
        send_email_main(receiver_email, sender_name, email_subject, message_content, message_type, footer)

        uid = fetch_uid(api_key)

        add_log(uid, {'title': 'Email Sent', 'message': f"Email sent to {data_json['receiver_email']} via API"})

        save_email_log(receiver_email, sender_name, email_subject, message_content, message_type, api_key,
                       is_template=False, template_id=None, is_sent=1, error=None, footer=footer)

        return json.dumps({'status': 'success', 'message': 'Email sent successfully'})
    except Exception as e:
        print(e)
        return json.dumps({'status': 'error', 'message': str(e)})


def handle_internal_email_send(data_json):
    sender_name = data_json['sender_name']
    email_subject = data_json['email_subject']
    message_content = data_json['message_content']
    message_type = data_json['message_type']
    footer = data_json['footer']
    receiver_email = data_json['receiver_email']
    try:
        send_email_main(receiver_email, sender_name, email_subject, message_content, message_type, footer)
        return json.dumps({'status': 'success', 'message': 'Email sent successfully'})
    except Exception as e:
        return json.dumps({'status': 'error', 'message': str(e)})


def send_2fa_email(code, user_email, email_type):
    if email_type == 'login':
        template = login_email_template(code)
        subject = "Login verification"
    elif email_type == 'register':
        template = register_email_template(code)
        subject = "Registration verification"
    elif email_type == 'forgot':
        template = reset_email_template(code)
        subject = "Password reset verification"
    elif email_type == 'change_email':
        template = change_email_template(code)
        subject = "Email change verification"

    data_json = {
        'sender_name': email_sender_name,
        'email_subject': subject,
        'message_content': template,
        'message_type': 'html',
        'footer': '',
        'receiver_email': user_email
    }

    try:
        result = handle_internal_email_send(data_json)
        response_data = json.loads(result)
        return response_data.get('status') == 'success'
    except Exception as e:
        return False


def send_password_change_email(email, username):
    subject = "Password changed"
    message = f"Hello {username},\n\nYour password has been changed."
    template = info_template("Password Changed", message)
    data_json = {
        'sender_name': email_sender_name,
        'email_subject': subject,
        'message_content': template,
        'message_type': 'html',
        'footer': '',
        'receiver_email': email
    }

    try:
        result = handle_internal_email_send(data_json)
        response_data = json.loads(result)
        return response_data.get('status') == 'success'
    except Exception as e:
        return False


def send_account_deletion_cancel_email(email, username):
    subject = "Account recovery"
    message = f'Hello {username}, <br> Your <a href="{project_url}" style="color: dodgerblue;">{project_name}</a> account has been recovered successfully.'
    template = info_template("Account Recovery", message)
    data_json = {
        'sender_name': email_sender_name,
        'email_subject': subject,
        'message_content': template,
        'message_type': 'html',
        'footer': '',
        'receiver_email': email
    }

    try:
        result = handle_internal_email_send(data_json)
        response_data = json.loads(result)
        return response_data.get('status') == 'success'
    except Exception as e:
        return False


def send_email_change(email, username):
    subject = "Email changed"
    template = email_change_template(email, username)

    data_json = {
        'sender_name': email_sender_name,
        'email_subject': subject,
        'message_content': template,
        'message_type': 'html',
        'footer': '',
        'receiver_email': email
    }

    try:
        result = handle_internal_email_send(data_json)
        response_data = json.loads(result)
        return response_data.get('status') == 'success'
    except Exception as e:
        return False


# web emails
def send_demo_email(receiver_email, email_type):
    # send email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Test message from Freemail API'
    msg['From'] = f'Freemail API <{email_username}>'
    msg['To'] = receiver_email

    if email_type == 'html':
        html = f'<html><body><h1>This is a test message from Freemail API</h1><p>Have a nice day</p></body></html>'
        part = MIMEText(html, 'html')
    else:
        part = MIMEText(f'This is a test message from Freemail API', 'plain')

    msg.attach(part)

    try:
        with smtplib.SMTP_SSL(email_host, email_port) as server:
            server.login(email_username, email_password)
            server.sendmail(email_username, receiver_email, msg.as_string())
        return True, None
    except Exception as e:
        # Log email sending failure
        print(e)
        return False, str(e)


def send_email_main(receiver_email, sender_name, email_subject, message_content, email_type, footer=None):
    # send email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = email_subject
    msg['From'] = f'{sender_name} <{email_username}>'
    msg['To'] = receiver_email

    if footer is None or footer == '':
        footer = None
    else:
        footer = f'<p style="font-size: 13px; text-align: center; color: #b1b3b1;">{footer}</p>'

    if email_type == 'html':
        if footer:
            html = f'<html><body>{message_content}<br>{footer}{freemail_footer}</body></html>'
        else:
            html = f'<html><body>{message_content}{freemail_footer}</body></html>'
        part = MIMEText(html, 'html')
    else:
        if footer:
            part = MIMEText(f'{message_content}<br>{footer}{freemail_footer}', 'html')
        else:
            part = MIMEText(f'{message_content}{freemail_footer}', 'html')

    msg.attach(part)

    try:
        with smtplib.SMTP_SSL(email_host, email_port) as server:
            server.login(email_username, email_password)
            server.sendmail(email_username, receiver_email, msg.as_string())
        return True, None
    except Exception as e:
        # Log email sending failure
        print(e)
        return False, e


def send_account_deletion_email(email, username):
    email_content = account_deletion_template(username)

    data_json = {
        'sender_name': email_sender_name,
        'email_subject': "Account deletion",
        'message_content': email_content,
        'message_type': 'html',
        'footer': '',
        'receiver_email': email
    }

    try:
        result = handle_internal_email_send(data_json)
        response_data = json.loads(result)
        return response_data.get('status') == 'success'
    except Exception as e:
        return False


def send_account_cancel_deletion_email(code, uid, email, username):
    raw_url = f"{uid}/{code}"
    recovery_link = f"{project_url}/auth/recover/{encode_url(raw_url)}"
    email_content = account_recovery_template(username, code, recovery_link)

    data_json = {
        'sender_name': email_sender_name,
        'email_subject': "Account recovery",
        'message_content': email_content,
        'message_type': 'html',
        'footer': '',
        'receiver_email': email
    }

    try:
        result = handle_internal_email_send(data_json)
        response_data = json.loads(result)
        return response_data.get('status') == 'success'
    except Exception as e:
        return False
