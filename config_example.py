import datetime

flask_secret_key = "later"
docker_data_dir = "data"
db_file_name = "freemail.db"
db_name = f'{docker_data_dir}/{db_file_name}'

port = 5000
debug = False
debug = True

current_year = datetime.datetime.now().year

url_hash_secret_key = ""

project_url = ""

email_api_url = f"{project_url}/send"
project_name = "freemail"
freemail_footer = f'<p style="font-size: 13px; text-align: center; color: #b1b3b1;"> &copy; {current_year} {project_name}. All rights reserved.</p>'

# emails
email_sender_name = 'freemail'

# SMTP configuration
email_host = ""
email_port = ""
email_username = ""
email_password = ""


freemail_free_limit = 300
freemail_free_reset = 30

