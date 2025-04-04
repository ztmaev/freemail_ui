function showGlobalNotif(status, message) {
    const notifContainer = document.querySelector(".global-notif")
    const notifText = document.querySelector(".global-notif .message")
    const notifIcon = document.querySelector(".global-notif i")

    // Generate a unique ID
    const uniqueId = `notif-${Date.now()}`
    notifContainer.id = uniqueId

    notifContainer.classList.remove("show")

    setTimeout(() => {

        notifContainer.classList.remove("success")
        notifContainer.classList.remove("error")

        notifText.innerText = message

        if (status === "success") {
            notifContainer.classList.add("success")
        } else if (status === "error") {
            notifContainer.classList.add("error")
        }

        notifIcon.addEventListener("click", () => closeNotif(uniqueId))

        notifContainer.classList.add("show")

        setTimeout(() => {
            closeNotif(uniqueId)
        }, 5000);

    }, 10);
}


function closeNotif(id) {
    const notifContainer = document.getElementById(id)
    if (notifContainer) {
        notifContainer.classList.remove("show")
    }
}

function updatePageTitle(title) {
    document.title = title + " | Freemail";
}

function openHomePage() {
    window.location.href = "/";
}


document.addEventListener('DOMContentLoaded', function () {


});


