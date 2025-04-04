document.addEventListener("DOMContentLoaded", function () {
  // Get all form links and forms
  const formLinks = document.querySelectorAll(".auth-link");
  const authForms = document.querySelectorAll(".auth-form");

  //buttons
  const loginButton = document.querySelector("#login-form button");
  const registerButton = document.querySelector("#register-form button");
  const forgotButton = document.querySelector("#forgot-form button");
  
  // Setup password toggle functionality
  const passwordToggles = document.querySelectorAll(".password-toggle");
  const passwordFields = document.querySelectorAll("input[type='password']");
  
  // Add input event listeners to password fields to show toggle buttons
  passwordFields.forEach(field => {
    field.addEventListener("input", function() {
      // Show the toggle button when user starts typing
      if (this.value.length > 0) {
        const toggleButton = this.nextElementSibling;
        toggleButton.style.display = "block";
      } else {
        // Hide the toggle button when field is empty
        const toggleButton = this.nextElementSibling;
        toggleButton.style.display = "none";
      }
    });
    
    // Check if password field already has a value (e.g., from autofill)
    // and only show toggle if user interacts with the field
    field.addEventListener("focus", function() {
      if (this.value.length > 0) {
        const toggleButton = this.nextElementSibling;
        toggleButton.style.display = "block";
      }
    });
  });
  
  // Setup click functionality for password toggles
  passwordToggles.forEach(toggle => {
    toggle.addEventListener("click", function() {
      const passwordField = this.previousElementSibling;
      if (passwordField.type === "password") {
        passwordField.type = "text";
        this.classList.remove("bx-hide");
        this.classList.add("bx-show");
      } else {
        passwordField.type = "password";
        this.classList.remove("bx-show");
        this.classList.add("bx-hide");
      }
    });
  });

  //url parse and show the correct page
  current_url = window.location.href;
  if (current_url.includes("register")) {
    //show register form
    authForms.forEach((form) => {
      form.classList.remove("active");
    });

    const targetForm = document.getElementById("register-form");
    targetForm.classList.add("active");
  } else if (current_url.includes("forgot")) {
    //show forgot password form
    authForms.forEach((form) => {
      form.classList.remove("active");
    });

    const targetForm = document.getElementById("forgot-form");
    targetForm.classList.add("active");
  }

  // Add click event listener to each form link
  formLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();

      // Get the form ID from the data-form attribute
      const formId = this.getAttribute("data-form");

      // Remove active class from all forms
      authForms.forEach((form) => {
        form.classList.remove("active");
        // Add fade-out animation
        form.classList.add("fade-out");

        // Remove fade-out class after animation completes
        setTimeout(() => {
          form.classList.remove("fade-out");
        }, 300);
      });

      // Add active class to the corresponding form with fade-in animation
      const targetForm = document.getElementById(`${formId}-form`);
      targetForm.classList.add("active", "fade-in");

      // update url
      // check if current url contains /auth
      if (current_url.includes("/auth")) {
        history.pushState(null, null, `/auth/${formId}`);
      }
      // Remove fade-in class after animation completes
      setTimeout(() => {
        targetForm.classList.remove("fade-in");
      }, 300);
    });
  });

  // Handle login form submission
  const loginForm = document.getElementById("login-form");
  loginForm.addEventListener("submit", function (e) {
    e.preventDefault();

    loginButton.classList.add("loading");
    loginButton.innerText = "Logging in...";

    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    // Validate form data
    if (!email || !password) {
      showGlobalNotif("error", "Please fill in all required fields");
      return;
    }

    // Send login request to server
    fetch("/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        password: password,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        loginButton.classList.remove("loading");
        loginButton.innerText = "Login";

        if (data.status === "success") {
          showGlobalNotif("success", data.message);
          // Redirect to dashboard after successful login
          setTimeout(() => {
            window.location.href = "/dashboard";
          }, 1000);
        } else if (data.status === "info") {
          // Show 2FA verification form
          if (data.action === "2fa") {
            saveCookie("session_token", data.session_token, 5);
            // Show 2FA verification form
            showTwoFactorAuthForm("login");
          } else if (data.action === "2fa_recover") {
            saveCookie("session_token", data.session_token, 5);
            // Show 2FA verification form
            showTwoFactorAuthForm("recover");
          }

          showGlobalNotif("info", data.message);
        } else {
          if (data.action === "register") {
            //show register form
            document.querySelector('.auth-link[data-form="register"]').click();
            //fill in email/username
            if (email.includes("@")) {
              document.getElementById("register-email").value = email;
            } else {
              document.getElementById("register-username").value = email;
            }

            showGlobalNotif("info", data.message);
          }
          showGlobalNotif("error", data.message);
        }
      })
      .catch((error) => {
        loginButton.classList.remove("loading");
        loginButton.innerText = "Login";
        console.error("Error:", error);
        showGlobalNotif("error", "An error occurred. Please try again.");
      });
  });

  // Handle register form submission
  const registerForm = document.getElementById("register-form");
  registerForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const email = document.getElementById("register-email").value;
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById(
      "register-confirm-password"
    ).value;

    // Validate form data
    if (!email || !username || !password || !confirmPassword) {
      showGlobalNotif("error", "Please fill in all required fields");
      return;
    }

    if (password !== confirmPassword) {
      showGlobalNotif("error", "Passwords do not match");
      return;
    }

    registerButton.classList.add("loading");
    registerButton.innerText = "Signing Up...";

    // Send register request to server
    fetch("/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        username: username,
        password: password,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        registerButton.classList.remove("loading");
        registerButton.innerText = "Register";
        if (data.status === "success") {
          showGlobalNotif("success", data.message);
          // Switch to login form after successful registration
          setTimeout(() => {
            document.querySelector('.auth-link[data-form="login"]').click();
          }, 1000);
        } else if (data.status === "info") {
          saveCookie("session_token", data.session_token, 5);
          // Show 2FA verification form
          showTwoFactorAuthForm("register");
          showGlobalNotif("info", data.message);
        } else {
          showGlobalNotif("error", data.message);
        }
      })
      .catch((error) => {
        registerButton.classList.remove("loading");
        registerButton.innerText = "Register";
        console.error("Error:", error);
        showGlobalNotif("error", "An error occurred. Please try again.");
      });
  });

  // Handle forgot password form submission
  const forgotForm = document.getElementById("forgot-form");
  forgotForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const email = document.getElementById("forgot-email").value;

    // Validate form data
    if (!email) {
      showGlobalNotif("error", "Please enter your email address");
      return;
    }

    forgotButton.classList.add("loading");
    forgotButton.innerText = "Requesting code ...";

    // Send forgot password request to server
    fetch("/auth/forgot-password", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        forgotButton.classList.remove("loading");
        forgotButton.innerText = "Reset Password";
        if (data.status === "success") {
          showGlobalNotif("success", data.message);
          // Switch to login form after password reset email is sent
          setTimeout(() => {
            document.querySelector('.auth-link[data-form="login"]').click();
          }, 1000);
        } else if (data.status === "info") {
          if (data.action === "2fa") {
            saveCookie("session_token", data.session_token, 5);
            // Show 2FA verification form
            showTwoFactorAuthForm("forgot");
          }

          showGlobalNotif("info", data.message);
        } else {
          showGlobalNotif("error", data.message);
        }
      })
      .catch((error) => {
        forgotButton.classList.remove("loading");
        forgotButton.innerText = "Reset Password";
        console.error("Error:", error);
        showGlobalNotif("error", "An error occurred. Please try again.");
      });
  });
});

function saveCookie(name, value, minutes) {
  var date = new Date();
  date.setTime(date.getTime() + minutes * 60 * 1000);
  document.cookie =
    name + "=" + value + "; expires=" + date.toUTCString() + "; path=/";
}

function getCookie(name) {
  var name = name + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(";");
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function deleteCookie(name) {
  document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

// Function to show 2FA verification form
function showTwoFactorAuthForm(form_type) {
  // console.log("form_type: " + form_type);

  // Hide all existing forms
  const authForms = document.querySelectorAll(".auth-form");
  authForms.forEach((form) => {
    form.classList.remove("active");
    form.classList.add("fade-out");
  });

  // Check if 2FA form already exists
  let twoFactorForm = document.getElementById("two-factor-form");

  if (!twoFactorForm) {
    // Create 2FA form if it doesn't exist
    twoFactorForm = document.createElement("form");
    twoFactorForm.id = "two-factor-form";
    twoFactorForm.className = "auth-form";

    twoFactorForm.innerHTML = `
            <div class="form-group">
                <label for="verification-code">Verification Code</label>
                <div class="verification-code-container">
                    <i class="bx bx-lock-alt"></i>
                    <div class="verification-inputs">
                        <input type="text" class="verification-digit" maxlength="1" autocomplete="off" data-index="0">
                        <input type="text" class="verification-digit" maxlength="1" autocomplete="off" data-index="1">
                        <input type="text" class="verification-digit" maxlength="1" autocomplete="off" data-index="2">
                        <span class="verification-separator"></span>
                        <input type="text" class="verification-digit" maxlength="1" autocomplete="off" data-index="3">
                        <input type="text" class="verification-digit" maxlength="1" autocomplete="off" data-index="4">
                        <input type="text" class="verification-digit" maxlength="1" autocomplete="off" data-index="5">
                    </div>
                    <input type="hidden" id="verification-code" name="verification-code" required>
                </div>
            </div>
            <p class="form-info">Enter the verification code sent to your email.</p>
            <button type="submit" class="auth-button">Verify</button>
            <div class="form-links">
                <a href="#" class="auth-link" data-form="login">Back to login</a>
            </div>
        `;
        
        // Add event listeners for the verification code inputs
        const digitInputs = twoFactorForm.querySelectorAll('.verification-digit');
        const hiddenInput = twoFactorForm.querySelector('#verification-code');
        
        // Function to update the hidden input with the combined value
        const updateVerificationCode = () => {
            let code = '';
            digitInputs.forEach(input => {
                code += input.value;
            });
            hiddenInput.value = code;
        };
        
        // Add event listeners to each digit input
        digitInputs.forEach((input, index) => {
            // Convert input to uppercase and handle navigation
            input.addEventListener('input', (e) => {
                // Convert to uppercase
                if (e.target.value) {
                    e.target.value = e.target.value.toUpperCase();
                }
                
                // Move to next input if a character was entered
                if (e.target.value && index < digitInputs.length - 1) {
                    digitInputs[index + 1].focus();
                }
                
                updateVerificationCode();
            });
            
            // Handle backspace to go to previous input
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Backspace' && !e.target.value && index > 0) {
                    digitInputs[index - 1].focus();
                }
            });
            
            // Handle paste event for the entire code
            input.addEventListener('paste', (e) => {
                e.preventDefault();
                const pasteData = (e.clipboardData || window.clipboardData).getData('text').toUpperCase();
                
                if (pasteData) {
                    // Fill in the inputs with the pasted data
                    for (let i = 0; i < digitInputs.length && i < pasteData.length; i++) {
                        digitInputs[i].value = pasteData[i];
                    }
                    
                    // Focus the next empty input or the last one
                    const nextEmptyIndex = Array.from(digitInputs).findIndex(input => !input.value);
                    if (nextEmptyIndex !== -1) {
                        digitInputs[nextEmptyIndex].focus();
                    } else {
                        digitInputs[digitInputs.length - 1].focus();
                    }
                    
                    updateVerificationCode();
                }
            });
        });
        
        // Focus the first input when the form is shown
        setTimeout(() => {
            digitInputs[0].focus();
        }, 350);

    // Add the form to the container
    document.querySelector(".auth-form-container").appendChild(twoFactorForm);

    // Add event listener for the back to login link
    twoFactorForm
      .querySelector(".auth-link")
      .addEventListener("click", function (e) {
        e.preventDefault();
        const formId = this.getAttribute("data-form");
        const targetForm = document.getElementById(`${formId}-form`);

        // Hide 2FA form
        twoFactorForm.classList.remove("active");
        twoFactorForm.classList.add("fade-out");

        // Show login form
        targetForm.classList.add("active", "fade-in");
        setTimeout(() => {
          targetForm.classList.remove("fade-in");
        }, 300);
      });

    // Add event listener for form submission
    twoFactorForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const verificationCode =
        document.getElementById("verification-code").value;

      // Validate form data
      if (!verificationCode) {
        showGlobalNotif("error", "Please enter the verification code");
        return;
      }

      // get the session token from the cookie
      const session_token = getCookie("session_token");

      if (!session_token) {
        showGlobalNotif("error", "Session token not found");
        return;
      }

      const f2aButton = document.querySelector("#two-factor-form button");

      f2aButton.classList.add("loading");
      f2aButton.innerText = "Verifying...";

      // Send verification code to server
      fetch("/auth/verify-2fa", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code: verificationCode,
          form_type: form_type,
          session_token: session_token,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          f2aButton.classList.remove("loading");
          f2aButton.innerText = "Verify";
          if (data.status === "success") {
            showGlobalNotif("success", data.message);
            //delete session token
            saveCookie("session_token", "", -1);

            // Redirect to dashboard after successful verification
            setTimeout(() => {
              window.location.href = "/dashboard";
            }, 1000);
          } else if (data.status === "info") {
            if (data.action === "new_password") {
              showNewPasswordForm();
            }

            showGlobalNotif("info", data.message);
          } else {
            showGlobalNotif("error", data.message);
          }
        })
        .catch((error) => {
          f2aButton.classList.remove("loading");
          f2aButton.innerText = "Verify";
          console.error("Error:", error);
          showGlobalNotif("error", "An error occurred. Please try again.");
        });
    });
  }

  // Show 2FA form with fade-in animation
  twoFactorForm.classList.add("active", "fade-in");
  setTimeout(() => {
    twoFactorForm.classList.remove("fade-in");
  }, 300);

  // Focus on the verification code input
  setTimeout(() => {
    document.getElementById("verification-code").focus();
  }, 350);
}

function showNewPasswordForm() {
  // Hide all existing forms
  const authForms = document.querySelectorAll(".auth-form");
  authForms.forEach((form) => {
    form.classList.remove("active");
    form.classList.add("fade-out");

    // Check if new password form already exists
    let newPasswordForm = document.getElementById("new-password-form");

    if (!newPasswordForm) {
      // Create new password form if it doesn't exist
      newPasswordForm = document.createElement("form");
      newPasswordForm.id = "new-password-form";
      newPasswordForm.className = "auth-form";

      newPasswordForm.innerHTML = `
        <div class="form-group">
            <label for="new-password">New Password</label>
            <div class="input-group">
                <i class="bx bx-lock-alt"></i>
                <input type="password" id="new-password" name="new-password" required>
            </div>
        </div>
        <div class="form-group">
            <label for="confirm-new-password">Confirm New Password</label>
            <div class="input-group">
                <i class="bx bx-lock-alt"></i>
                <input type="password" id="confirm-new-password" name="confirm-new-password" required>
            </div>
        </div>
        <button type="submit" class="auth-button">Change Password</button>
        <div class="form-links">
            <a href="#" class="auth-link" data-form="login">Back to login</a>
        </div>
    `;

      // Add the form to the container
      document
        .querySelector(".auth-form-container")
        .appendChild(newPasswordForm);

      // Add event listener for the back to login link
      newPasswordForm
        .querySelector(".auth-link")
        .addEventListener("click", function (e) {
          e.preventDefault();
          const formId = this.getAttribute("data-form");
          const targetForm = document.getElementById(`${formId}-form`);

          // Hide new password form
          newPasswordForm.classList.remove("active");
          newPasswordForm.classList.add("fade-out");

          // Show login form
          targetForm.classList.add("active", "fade-in");
          setTimeout(() => {
            targetForm.classList.remove("fade-in");
          }, 300);
        });

      // Add event listener for form submission
      newPasswordForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const newPassword = document.getElementById("new-password").value;
        const confirmNewPassword = document.getElementById(
          "confirm-new-password"
        ).value;
        const sessionToken = getCookie("session_token");

        // Validate form data
        if (!newPassword || !confirmNewPassword) {
          showGlobalNotif("error", "Please fill in all required fields");
          return;
        }

        if (newPassword !== confirmNewPassword) {
          showGlobalNotif("error", "Passwords do not match");
          return;
        }

        if (!sessionToken) {
          showGlobalNotif("error", "Session token not found");
          return;
        }

        const passwordChangeButton = document.querySelector("#new-password-form button");
        passwordChangeButton.classList.add("loading");
        passwordChangeButton.innerText = "Updating password...";

        // Send new password to server
        fetch("/auth/reset-password", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            password: newPassword,
            confirmPassword: confirmNewPassword,
          }),
        })
          .then((response) => response.json())
          .then((data) => {
            passwordChangeButton.classList.remove("loading");
            passwordChangeButton.innerText = "Change Password";
            if (data.status === "success") {
              showGlobalNotif("success", data.message);
              deleteCookie("session_token");

              // Redirect to dashboard
              setTimeout(() => {
                window.location.href = "/dashboard";
              }, 1000);
            } else {
              showGlobalNotif("error", data.message);
            }
          })
          .catch((error) => {
            passwordChangeButton.classList.remove("loading");
            passwordChangeButton.innerText = "Change Password";
            console.error("Error:", error);
            showGlobalNotif("error", "An error occurred. Please try again.");
          });
      });
    }

    // Show new password form with fade-in animation
    newPasswordForm.classList.add("active", "fade-in");
    setTimeout(() => {
      newPasswordForm.classList.remove("fade-in");
    }, 300);

    // Focus on the new password input
    setTimeout(() => {
      document.getElementById("new-password").focus();
    }, 350);
  });
}
