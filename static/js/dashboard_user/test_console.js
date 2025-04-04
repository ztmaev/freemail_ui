document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('emailForm');
    const submitButton = document.getElementById('submitButton');
    const messageTypeSelect = document.getElementById('messageType');
    const messageTextarea = document.getElementById('message');
    const resultCard = document.getElementById('resultCard');
    const resultTitle = document.getElementById('resultTitle');
    const successAlert = document.getElementById('successAlert');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    const emailId = document.getElementById('emailId');
    const resultFooter = document.getElementById('resultFooter');

    // State
    let isLoading = false;

    // Update message placeholder based on selected message type
    messageTypeSelect.addEventListener('change', () => {
        const messageType = messageTypeSelect.value;
        if (messageType === 'html') {
            messageTextarea.placeholder = '<p>Your HTML content here</p>';
        } else {
            messageTextarea.placeholder = 'Your message here';
        }
    });

    // Use global notification system instead of custom toast

    // Set loading state
    function setLoading(loading) {
        isLoading = loading;

        if (loading) {
            submitButton.disabled = true;
            submitButton.innerHTML = `<i class='bx bx-send bx-flashing'></i><span>Sending...</span>`;
        } else {
            submitButton.disabled = false;
            submitButton.innerHTML = `<i class='bx bx-send'></i><span>Send Test Email</span>`;
        }
    }


    // Validate form
    function validateForm(formData) {
        const requiredFields = [ 'senderName', 'subject', 'message', 'receiverEmail'];

        for (const field of requiredFields) {
            if (!formData.get(field)) {
                throw new Error(`Please fill in the ${field.replace(/([A-Z])/g, ' $1').toLowerCase()} field`);
            }
        }

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.get('receiverEmail'))) {
            throw new Error('Please enter a valid email address');
        }
    }

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (isLoading) return;

        setLoading(true);

        try {
            const formData = new FormData(form);

            // Validate form data
            validateForm(formData);

            // Convert FormData to object for display
            const formDataObj = Object.fromEntries(formData);
            // console.log('Form data:', formDataObj);

            // send data to backend
            const response = await fetch('/api/test_console', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formDataObj),
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || 'Failed to send email');
            }
            // Show success notification
            showGlobalNotif('success', data.message);
            // reset form
            form.reset();
            messageTypeSelect.dispatchEvent(new Event('change'));
        } catch (error) {
            console.error('Error:', error);

            // Show error notification
            showGlobalNotif('error', error.message || 'Failed to send email');
        } finally {
            setLoading(false);
        }
    });

    // Initialize message type placeholder
    messageTypeSelect.dispatchEvent(new Event('change'));

    // Initialize message type placeholder
});