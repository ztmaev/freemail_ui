document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const apiKeyValue = document.getElementById('apiKeyValue');
    const copyApiKeyBtn = document.getElementById('copyApiKeyBtn');
    const regenerateKeyBtn = document.getElementById('regenerateKeyBtn');
    const regenerateKeyText = document.getElementById('regenerateKeyText');
    const requestCode = document.getElementById('requestCode');
    const copyRequestBtn = document.getElementById('copyRequestBtn');
    const copyResponseBtn = document.getElementById('copyResponseBtn');
    const responseCode = document.getElementById('responseCode');
    const apiKeyDisplay = document.querySelector('.api-key-display');
    const apiKeyDisplayNone = document.querySelector('.api-key-none');
    const apiKeyRegenerateBtn = document.getElementById('regenerateKeyBtn');
    const apiKeyGenerateBtn = document.getElementById('generateKeyBtn');    

    // No caching - always fetch from server

    // Generate a random API key
    function generateApiKey(length = 32) {
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        return result;
    }


    // Copy text to clipboard
    async function copyToClipboard(text, successMessage) {
        try {
            await navigator.clipboard.writeText(text);
            showGlobalNotif('success', successMessage);
        } catch (err) {
            showGlobalNotif('error', 'Failed to copy text');
            console.error('Failed to copy: ', err);
        }
    }

    // Always fetch API key from server
    async function getApiKey() {
        try {
            // Call the API endpoint to get key
            const response = await fetch('/api/get_api_key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const data = await response.json();
                if (data && data.api_key) {
                    return data.api_key;
                }

                throw new Error('Failed to get API key');
            }

            const data = await response.json();
            return data.api_key;
        } catch (error) {
            console.error('Error getting API key:', error);
            showGlobalNotif('error', 'Failed to get API key');
            return 'Error: Could not retrieve API key';
        }
    }

    // Function removed - code block is now hard-coded in HTML


    // Initialize the API key
async function initializeApiKey() {
    apiKeyValue.textContent = 'Loading...';

    const apiKey = await getApiKey();

    if (apiKey === 'None') {
        apiKeyDisplay.classList.add('hidden');
        apiKeyDisplayNone.classList.remove('hidden');
        apiKeyRegenerateBtn.classList.add('hidden');
        apiKeyGenerateBtn.classList.remove('hidden');
    } else {
        apiKeyDisplay.classList.remove('hidden');
        apiKeyDisplayNone.classList.add('hidden');
        apiKeyRegenerateBtn.classList.remove('hidden');
        apiKeyGenerateBtn.classList.add('hidden');
        apiKeyValue.textContent = apiKey;
    }
}
    //generate api key
    async function generateApiKey() {
        // Update button state
        apiKeyGenerateBtn.disabled = true;
        //replace bx-plus with bx-refresh
        apiKeyGenerateBtn.querySelector('i').classList.remove('bx-plus');
        apiKeyGenerateBtn.querySelector('i').classList.add('bx-refresh');
        apiKeyGenerateBtn.querySelector('i').classList.add('bx-spin');  
        try {
            // Call the API endpoint to generate key
            const response = await fetch('/api/generate_api_key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to generate API key');
            }

            const data = await response.json();
            const newKey = data.api_key;

            // Update displayed key
            apiKeyValue.textContent = newKey;
            
            // Update UI elements
            apiKeyDisplay.classList.remove('hidden');
            apiKeyDisplayNone.classList.add('hidden');
            apiKeyRegenerateBtn.classList.remove('hidden');
            apiKeyGenerateBtn.classList.add('hidden');

            // Show success message
            showGlobalNotif('success', 'API Key generated successfully');
        }
        catch (error) {
            console.error('Error generating API key:', error);
            showGlobalNotif('error', 'Failed to generate API key'); 
        }
    }

    // Regenerate API key
    async function regenerateApiKey() {
        // Update button state
        regenerateKeyBtn.disabled = true;
        regenerateKeyText.textContent = 'Regenerating...';
        apiKeyValue.textContent = 'Getting new API key...';
        copyApiKeyBtn.classList.add('hidden');
        regenerateKeyBtn.querySelector('i').classList.add('bx-spin');

        try {
            // Call the API endpoint to regenerate key
            const response = await fetch('/api/regenerate_api_key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to regenerate API key');
            }

            const data = await response.json();
            const newKey = data.api_key;

            // Update displayed key
            apiKeyValue.textContent = newKey;

            // Show success message
            showGlobalNotif('success', 'API Key regenerated successfully');
        } catch (error) {
            console.error('Error regenerating API key:', error);
            showGlobalNotif('error', 'Failed to regenerate API key');
        } finally {
            // Reset button state
            regenerateKeyBtn.disabled = false;
            regenerateKeyText.textContent = 'Regenerate Key';
            copyApiKeyBtn.classList.remove('hidden');
            regenerateKeyBtn.querySelector('i').classList.remove('bx-spin');
        }
    }

    // Event Listeners
    copyApiKeyBtn.addEventListener('click', function () {
        copyToClipboard(apiKeyValue.textContent, 'API Key copied to clipboard');
    });

    generateKeyBtn.addEventListener('click', generateApiKey);

    regenerateKeyBtn.addEventListener('click', regenerateApiKey);

    copyRequestBtn.addEventListener('click', function () {
        copyToClipboard(requestCode.textContent, 'Request example copied to clipboard');
    });

    copyResponseBtn.addEventListener('click', function () {
        copyToClipboard(responseCode.textContent, 'Response example copied to clipboard');
    });

    // Initialize highlight.js syntax highlighting
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('pre code').forEach((block) => {
            // hljs.highlightBlock(block);
            hljs.highlightElement(block);
        });
    }

    // Initialize
    initializeApiKey();
});