document.addEventListener("DOMContentLoaded", function () {
    // Load user profile data from server
    function loadUserProfile() {
        fetch("/api/profile/info", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "success") {
                    // Update profile information
                    const profileName = document.querySelector(".profile-name");
                    const profileEmail = document.querySelector(".profile-email");
                    const emailsSent = document.querySelector(
                        ".stat-item:nth-child(1) .stat-value"
                    );
                    const daysActive = document.querySelector(
                        ".stat-item:nth-child(2) .stat-value"
                    );
                    const currentPlan = document.querySelector(
                        ".stat-item:nth-child(3) .stat-value"
                    );

                    if (profileName) profileName.textContent = data.user.fullname;
                    if (profileEmail) profileEmail.textContent = data.user.email;
                    if (emailsSent) emailsSent.textContent = data.user.emails_sent;
                    if (daysActive) daysActive.textContent = data.user.days_active;
                    if (currentPlan) currentPlan.textContent = data.user.plan;

                    // Update form fields
                    const fullnameInput = document.getElementById("fullname");
                    const emailInput = document.getElementById("email");
                    const timezoneSelect = document.getElementById("timezone");

                    if (fullnameInput) fullnameInput.value = data.user.fullname;
                    if (emailInput) emailInput.value = data.user.email;
                    if (timezoneSelect) timezoneSelect.value = data.user.timezone;

                    // Update notification preferences
                    const toggles = document.querySelectorAll(
                        '.toggle-switch input[type="checkbox"]'
                    );
                    if (toggles.length > 0 && data.user.notification_preferences) {
                        const prefs = data.user.notification_preferences;
                        if (toggles[0]) toggles[0].checked = prefs.email_notifications;
                        if (toggles[1]) toggles[1].checked = prefs.marketing_emails;
                        if (toggles[2]) toggles[2].checked = prefs.security_alerts;
                    }
                } else {
                    showNotification("Failed to load profile data", "error");
                }

                // 2fa
                const f2a_status = data.user.f2a_status;
                const f2a_status_toggle = document.querySelector('.f2a-status .toggle-switch input[type="checkbox"]')
                if (f2a_status_toggle) {
                    f2a_status_toggle.checked = f2a_status;
                }

            })
            .catch((error) => {
                console.error("Error:", error);
                showNotification("Failed to load profile data", "error");
            });
    }

    // Load user profile when page loads
    loadUserProfile();
    // Profile form submission
    const profileForm = document.getElementById("profile-form");
    if (profileForm) {
        profileForm.addEventListener("submit", function (e) {
            e.preventDefault();
            // Get form data
            const formData = new FormData(profileForm);
            const userData = {
                fullname: formData.get("fullname"),
                timezone: formData.get("timezone"),
            };

            // Get the submit button and add loading class
            const submitBtn = profileForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.classList.add('loading');

            // Send data to the backend
            fetch("/api/profile/update", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(userData),
            })
                .then((response) => response.json())
                .then((data) => {
                    // Remove loading class
                    submitBtn.classList.remove('loading');
                    submitBtn.innerHTML = originalBtnText;
                    
                    if (data.status === "success") {
                        showNotification(data.message, "success");
                    } else {
                        showNotification(data.message || "An error occurred", "error");
                    }
                })
                .catch((error) => {
                    // Remove loading class
                    submitBtn.classList.remove('loading');
                    submitBtn.innerHTML = originalBtnText;
                    
                    console.error("Error:", error);
                    showNotification("Failed to update profile", "error");
                });
        });
    }

    // Security form submission
    const securityForm = document.getElementById("security-form");
    if (securityForm) {
        securityForm.addEventListener("submit", function (e) {
            e.preventDefault();
            // Get form data
            const formData = new FormData(securityForm);
            const currentPassword = formData.get("current-password");
            const newPassword = formData.get("new-password");
            const confirmPassword = formData.get("confirm-password");

            // Validate passwords
            if (!currentPassword) {
                showNotification("Please enter your current password", "error");
                return;
            }

            if (!newPassword) {
                showNotification("Please enter a new password", "error");
                return;
            }

            if (newPassword !== confirmPassword) {
                showNotification("New passwords do not match", "error");
                return;
            }

            // Get the submit button and add loading class
            const submitBtn = securityForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.classList.add('loading');

            // Send data to the backend
            fetch("/api/profile/update-password", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    currentPassword: currentPassword,
                    newPassword: newPassword,
                }),
            })
                .then((response) => response.json())
                .then((data) => {
                    // Remove loading class
                    submitBtn.classList.remove('loading');
                    submitBtn.innerHTML = originalBtnText;
                    
                    if (data.status === "success") {
                        showNotification(data.message, "success");
                        securityForm.reset();
                    } else {
                        showNotification(data.message || "An error occurred", "error");
                    }
                })
                .catch((error) => {
                    // Remove loading class
                    submitBtn.classList.remove('loading');
                    submitBtn.innerHTML = originalBtnText;
                    
                    console.error("Error:", error);
                    showNotification("Failed to update password", "error");
                });
        });
    }

    // Toggle switches
    const toggleSwitches = document.querySelectorAll(
        '.toggle-switch input[type="checkbox"]'
    );
    toggleSwitches.forEach((toggle) => {
        toggle.addEventListener("change", function () {
            const settingName = this.closest(".notification-option").getAttribute(
                "data-type"
            );
            const isEnabled = this.checked;

            // Send preference to the backend
            fetch("/api/profile/update-notification", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    setting: settingName,
                    enabled: isEnabled,
                }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === "success") {
                        showNotification(
                            data.message ||
                            `${settingName} ${isEnabled ? "enabled" : "disabled"}`,
                            "success"
                        );
                    } else {
                        showNotification(data.message || "An error occurred", "error");
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    showNotification(
                        `Failed to update ${settingName} preference`,
                        "error"
                    );
                });
        });
    });

    // 2fa toggle
    const f2a_status_toggle = document.querySelector('.f2a-status .toggle-switch input[type="checkbox"]');
    const f2a_status_toggle_btn = document.querySelector('.f2a-status .toggle-switch .toggle-slider');
    if (f2a_status_toggle_btn) {
        f2a_status_toggle_btn.addEventListener("click", function () {
            const isEnabled = f2a_status_toggle.checked;
            //toggle switch
            f2a_status_toggle.checked = !isEnabled;
            // Send preference to the backend
            fetch("/api/profile/update-2fa", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    enabled: !isEnabled,
                }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === "success") {
                        showNotification(
                            data.message ||
                            `${isEnabled ? "enabled" : "disabled"}`,
                            "success"
                        );
                    } else {
                        showNotification(data.message || "An error occurred", "error");
                        //revert toggle
                        f2a_status_toggle.checked = isEnabled;
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    showNotification(
                        `Failed to update 2fa preference`,
                        "error"
                    );
                    //revert toggle
                    f2a_status_toggle.checked = isEnabled;
                })

        })
    }

    // Delete account overlay functionality
    const deleteAccountBtn = document.getElementById("delete-account-btn");
    const deleteAccountOverlay = document.getElementById(
        "delete-account-overlay"
    );
    const cancelDeleteBtn = document.getElementById("cancel-delete-btn");
    const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
    const confirmPasswordInput = document.getElementById(
        "delete-confirm-password"
    );
    const sidebarContent = document.querySelector(".sidebar-content");

    if (deleteAccountBtn && deleteAccountOverlay) {
        // Open overlay when delete button is clicked
        deleteAccountBtn.addEventListener("click", function () {
            deleteAccountOverlay.classList.add("active");

            // disable scroll
            sidebarContent.classList.add("no-scroll");

            // Focus on email input
            if (confirmPasswordInput) {
                confirmPasswordInput.focus();
            }
        });

        // Close overlay when cancel button is clicked
        if (cancelDeleteBtn) {
            cancelDeleteBtn.addEventListener("click", function () {
                deleteAccountOverlay.classList.remove("active");
                // enable scroll
                sidebarContent.classList.remove("no-scroll");
            });
        }

        // Add event listener for Enter key on password input
        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener("keydown", function(event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    // Trigger the delete button click
                    confirmDeleteBtn.click();
                }
            });
        }

        // Handle confirm delete action
        if (confirmDeleteBtn && confirmPasswordInput) {
            confirmDeleteBtn.addEventListener("click", function () {
                const password = document.getElementById(
                    "delete-confirm-password"
                ).value;

                if (!password) {
                    showNotification(
                        "Please enter your password to confirm account deletion",
                        "error"
                    );
                    return;
                }

                confirmDeleteBtn.textContent = "Deleting...";
                confirmDeleteBtn.classList.add('loading')

                // Send delete request to the backend
                fetch("/api/profile/delete-account", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        password: password,
                    }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        // Reset button text
                        confirmDeleteBtn.textContent = "Delete account";
                        confirmDeleteBtn.classList.remove('loading')

                        if (data.status === "success") {
                            showNotification(
                                data.message || "Account deletion request submitted",
                                "warning"
                            );
                            // Clear the email input
                            if (confirmPasswordInput) {
                                confirmPasswordInput.value = "";
                            }

                            deleteAccountOverlay.classList.remove("active");
                            // Redirect to logout after a short delay
                            setTimeout(() => {
                                window.location.href = "/auth/logout";
                            }, 2000);
                        } else {
                            showNotification(data.message || "An error occurred", "error");
                        }
                    })
                    .catch((error) => {
                        confirmDeleteBtn.textContent = "Delete account";
                        confirmDeleteBtn.classList.remove('loading')

                        if (data.action === "retry") {
                            showNotification(data.message || "An error occurred", "error");
                        } else {
                            // console.error('Error:', error);
                            deleteAccountOverlay.classList.remove("active");
                            showNotification(
                                "Failed to process account deletion request",
                                "error"
                            );
                        }
                    });
                // enable scroll
                sidebarContent.classList.remove("no-scroll");
            });
        }

        // Close overlay when clicking outside the dialog
        deleteAccountOverlay.addEventListener("click", function (e) {
            if (e.target === deleteAccountOverlay) {
                deleteAccountOverlay.classList.remove("active");
                // enable scroll
                sidebarContent.classList.remove("no-scroll");

                // Clear the email input
                if (confirmPasswordInput) {
                    confirmPasswordInput.value = "";
                }
            }
        });
    }

    // Logout functionality
    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function () {
            // Redirect to logout page
            window.location.href = "/auth/logout";
        });
    }

    // Helper function to show notifications
    function showNotification(message, type = "info") {
        showGlobalNotif(type, message);
    }
    
    // Password toggle functionality
    const passwordToggles = document.querySelectorAll('.password-toggle');
    const passwordFields = document.querySelectorAll('input[type="password"]');
    
    // Add input event listeners to password fields to show/hide toggle buttons
    passwordFields.forEach(field => {
        // Get the associated toggle button (next element sibling)
        const toggle = field.nextElementSibling;
        if (toggle && toggle.classList.contains('password-toggle')) {
            // Show toggle only when input has value
            field.addEventListener('input', function() {
                if (this.value.length > 0) {
                    toggle.style.display = 'flex';
                } else {
                    toggle.style.display = 'none';
                }
            });
            
            // Initial check in case of autofill
            if (field.value.length > 0) {
                toggle.style.display = 'flex';
            }
        }
    });
    
    // Add click event listeners to toggle buttons
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const passwordField = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            // Toggle password visibility
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                passwordField.classList.add('password-field');
                icon.classList.remove('bx-hide');
                icon.classList.add('bx-show');
            } else {
                passwordField.type = 'password';
                passwordField.classList.remove('password-field');
                icon.classList.remove('bx-show');
                icon.classList.add('bx-hide');
            }
        });
    });
});
