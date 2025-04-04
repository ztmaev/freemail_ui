document.addEventListener("DOMContentLoaded", function () {
    // Initialize dashboard data
    initDashboard();

    // Add event listeners
    setupEventListeners();
});

/**
 * Initialize dashboard with data
 */
function initDashboard() {
    refreshDashboard();
}

/**
 * Refresh dashboard with latest data from server
 * This function can be called whenever the dashboard needs to be updated
 */
function refreshDashboard() {
    // Show loading indicator (optional)
    const refreshButton = document.getElementById("refresh-dashboard");
    if (refreshButton) {
        refreshButton.classList.add("loading");
    }

    // Fetch dashboard data from API
    fetchDashboardData()
        .then((data) => {
            updateDashboardStats(data);
            updateActivityList(data.recentActivity);
            updateUsageProgress(data.emailsSent, data.emailsLimit);

            // Hide loading indicator (optional)
            if (refreshButton) {
                refreshButton.classList.remove("loading");
            }
        })
        .catch((error) => {
            console.error("Error fetching dashboard data:", error);
            // Use placeholder data for demonstration
            usePlaceholderData();

            // Hide loading indicator (optional)
            if (refreshButton) {
                refreshButton.classList.remove("loading");
            }
        });
}

/**
 * Fetch dashboard data from API
 */
async function fetchDashboardData() {
    try {
        // Make a real API call to fetch dashboard data
        const response = await fetch("/api/profile/dashboard", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("Error fetching dashboard data:", error);
        throw error;
    }
}

/**
 * Use placeholder data when API fails
 */
function usePlaceholderData() {
    // Update stats with placeholder data
    document.getElementById("emails-sent").textContent = "0";
    document.getElementById("delivery-rate").textContent = "0%";
    document.getElementById("emails-remaining").textContent = "100";
    document.getElementById("reset-days").textContent = "30";

    // Show empty activity state
    const activityList = document.getElementById("activity-list");
    activityList.innerHTML = `
        <div class="activity-empty">
            <i class='bx bx-inbox'></i>
            <p>No activity yet</p>
        </div>
    `;

    // Update usage progress
    updateUsageProgress(0, 100);
}

/**
 * Update dashboard statistics
 */
function updateDashboardStats(data) {
    document.getElementById("emails-sent").textContent = data.emailsSent;
    document.getElementById(
        "delivery-rate"
    ).textContent = `${data.deliveryRate}%`;
    document.getElementById("emails-remaining").textContent =
        data.emailsLimit - data.emailsSent;
    document.getElementById("reset-days").textContent = data.daysUntilReset;
}

/**
 * Update activity list with recent activities
 */
function updateActivityList(activities) {
    const activityList = document.getElementById("activity-list");
    const cardFooter = document.querySelector(".activity-card .card-footer");

    if (!activities || activities.length === 0) {
        activityList.innerHTML = `
            <div class="activity-empty">
                <i class='bx bx-inbox'></i>
                <p>No activity yet</p>
            </div>
        `;
        // Hide the card footer when there's no activity
        if (cardFooter) {
            cardFooter.style.display = "none";
        }
        return;
    }

    // Show the card footer when there are activities
    if (cardFooter) {
        cardFooter.style.display = "flex";
    }

    // Clear existing content
    activityList.innerHTML = "";

    // Add activity items
    activities.forEach((activity) => {
        const activityItem = document.createElement("div");
        activityItem.className = "activity-item";

        // Format timestamp
        const timestamp = new Date(activity.timestamp);
        const formattedDate = timestamp.toLocaleDateString();
        const formattedTime = timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });

        // Set status icon and class
        let statusIcon = "bx-check-circle";
        let statusClass = "success";

        if (activity.status === "failed") {
            statusIcon = "bx-x-circle";
            statusClass = "error";
        } else if (activity.status === "pending") {
            statusIcon = "bx-time";
            statusClass = "pending";
        }

        activityItem.innerHTML = `
            <div class="activity-icon ${statusClass}">
                <i class='bx ${statusIcon}'></i>
            </div>
            <div class="activity-content">
                <div class="activity-header">
                    <h4 class="activity-title">
                    <p>To:</p> 
                    </p>${
            activity.recipient
        }</p></h4>
                    <span class="activity-time">${formattedDate} at ${formattedTime}</span>
                </div>
                <p class="activity-description">${activity.subject}</p>
                <div class="activity-status ${statusClass}">
                    <span>${
            activity.status.charAt(0).toUpperCase() +
            activity.status.slice(1)
        }</span>
                </div>
            </div>
        `;

        activityList.appendChild(activityItem);
    });
}

/**
 * Update usage progress bar
 */
function updateUsageProgress(used, total) {
    const percentage = Math.min(Math.round((used / total) * 100), 100);

    // Update progress bar width
    const progressBar = document.getElementById("usage-progress-bar");
    progressBar.style.width = `${percentage}%`;

    // Update usage count text
    document.getElementById(
        "usage-count"
    ).textContent = `${used}/${total} emails`;

    // Change color based on usage percentage
    if (percentage > 80) {
        progressBar.style.backgroundColor = "var(--danger-color)";
    } else if (percentage > 60) {
        progressBar.style.backgroundColor = "orange";
    } else {
        progressBar.style.backgroundColor = "var(--accent-color)";
    }
}

/**
 * Setup event listeners for dashboard interactions
 */
function setupEventListeners() {
    // View all activity button
    const viewAllActivityBtn = document.getElementById("view-all-activity");
    if (viewAllActivityBtn) {
        viewAllActivityBtn.addEventListener("click", function (e) {
            e.preventDefault();
            // In a real app, this would navigate to an activity log page
            // console.log("View all activity clicked");
            populateSidebarContent('history');
            fetchEmails();
        });
    }

    // Send test email button
    const sendTestEmailBtn = document.getElementById("send-test-email");
    if (sendTestEmailBtn) {
        sendTestEmailBtn.addEventListener("click", function (e) {
            e.preventDefault();
            // In a real app, this would open a modal to send a test email
            // console.log('Send test email clicked');
            showConsoleTab();
        });
    }

    // Refresh dashboard button
    const refreshDashboardBtn = document.getElementById("refresh-dashboard");
    if (refreshDashboardBtn) {
        refreshDashboardBtn.addEventListener("click", function (e) {
            e.preventDefault();
            refreshDashboard();
        });
    }
}

/**
 * Helper functions for tab navigation
 */

function showDashboardTab(event) {
    if (event) event.preventDefault();
    const dashboardTab = document.querySelector(
        '.sidebar-item[data-at="dashboard"]'
    );
    if (dashboardTab) dashboardTab.click();
}

function showDocsTab(event) {
    if (event) event.preventDefault();
    const docsTab = document.querySelector(
        '.sidebar-item[data-at="documentation"]'
    );
    if (docsTab) docsTab.click();
}

function showApiTab(event) {
    if (event) event.preventDefault();
    const apiTab = document.querySelector('.sidebar-item[data-at="api-keys"]');
    if (apiTab) apiTab.click();
}


function showConsoleTab(event) {
    if (event) event.preventDefault();
    const consoleTab = document.querySelector(
        '.sidebar-item[data-at="test-console"]'
    );
    if (consoleTab) consoleTab.click();
}

function showProfileTab(event) {
    if (event) event.preventDefault();
    const profileTab = document.querySelector(
        '.sidebar-item[data-at="profile"]'
    );
    if (profileTab) profileTab.click();
}

