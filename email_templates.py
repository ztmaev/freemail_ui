from config import project_url, project_name


def master_template(header, message, extra_content=""):
    return f"""
            <div style="width: 100%; padding: 40px 0; padding-bottom: 30px; background: #192a1a; border-top-left-radius: 8px; border-top-right-radius: 8px; border-top: 2px solid #0d9023; border-bottom: 1px solid #b9f2b9;">
                <p style="font-size: 30px; text-align: center; font-weight: bold; padding: 0; margin: 0; color: #eee;">
                Freemail API</p>
            </div>
            <div  style="width: 100%; min-height: 100px; background: #192a1a;  border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
                <div style="padding: 20px;">
                    <div style="margin: 0; margin-bottom: 10px; padding: 0 ; color: #eee; font-size: 14px;">{message}</div>
                    <div style="margin: 0; padding: 0; color: #eee; font-size: 14px;">{extra_content}</div>
                </div>
            </div>
            <div  style="width: 100%; margin-top: 20px; font-size: 12px; color: #b1b3b1;">
                <p style="text-align: center;">You received this email because of recent activity on your {project_name} account. </p>
            </div>
            """


def verification_email_template(header, message, code):
    code_first_half = code[:len(code) // 2]
    code_second_half = code[len(code) // 2:]

    extra_content = f"""
        <div style="background: #191918; border-radius: 12px;">
            <p style="color: #b9f2b9; font-size: 30px; font-weight: bold; padding: 20px; margin: 0; border-radius: 12px; text-align: center;">{code_first_half}<span style="width: 15px;"> </span>{code_second_half}</p>
        </div>
        <p style="color: #ccc; font-size: 12px;">This code will expire in 10 minutes. Please use it promptly.</p>
        <p style="color: #ccc; font-size: 12px;">If you didn't request this code, please disregard this email.</p>
    """
    return master_template(header, message, extra_content)


def login_email_template(code):
    return verification_email_template("Login Verification", "Use the following code to verify your login", code)


def register_email_template(code):
    return verification_email_template("Registration Verification",
                                       "Use the following code to verify your registration", code)


def reset_email_template(code):
    return verification_email_template("Password Reset Verification",
                                       "Use the following code to complete your password reset", code)


def change_email_template(code):
    return verification_email_template("Email Change Verification",
                                       "Use the following code to verify your email change", code)


def account_recovery_template(username, code, link):
    code_first_half = code[:len(code) // 2]
    code_second_half = code[len(code) // 2:]

    extra_content = f"""
        <p style="color: #eee;">Use the code or click the button below to recover your <a href="{project_url}" style="color: dodgerblue;">{project_name}</a> account.</p>
        <div style="background: #191918; border-radius: 12px;">
            <p style="color: #b9f2b9; font-size: 30px; font-weight: bold; padding: 20px; margin: 0; border-radius: 12px; text-align: center;">{code_first_half}<span style="width: 15px;"> </span>{code_second_half}</p>
        </div>
        <div style="padding: 20px; margin: 0 auto;">
        <p style="text-align: center;">
            <a href="{link}" style="color: #eee; text-decoration: none; font-size: 20px; border: 1px solid #1bac8f; background: #0d9023; border-radius: 5px; padding: 10px 20px;">Recover</a>
        </p>
        </div>
        <p style="color: #eee;">If the button above does not work, open the link below.</p>
        <p style="color: dodgerblue;">{link}</p>
        <p style="color: #eee; font-size: 12px">If you didn't request to recover your account, please disregard this email.</p>
    """
    return master_template("Account Recovery", f"Hello {username.capitalize()},", extra_content)


def email_change_template(email, username):
    message = f"Hello {username.capitalize()},<br> your account email for <a href=\"{project_url}\" style=\"color: dodgerblue;\">{project_name}</a> has been changed to {email}."
    return master_template("Email Changed", message)


def account_deletion_template(username):
    message = f"Hello {username.capitalize()},<br> your <a href=\"{project_url}\" style=\"color: dodgerblue;\">{project_name}</a> account has been queued for deletion and will be deleted in 30 days. Log in before then to recover it."
    return master_template("Account Deletion", message)


def info_template(heading, message):
    return master_template(heading, message)
