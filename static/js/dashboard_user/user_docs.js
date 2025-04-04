document.addEventListener('DOMContentLoaded', () => {
    // Tab switching functionality
    const tabTriggers = document.querySelectorAll('.tab-trigger');
    const tabContents = document.querySelectorAll('.tab-content');

    tabTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            // Remove active class from all triggers and contents
            tabTriggers.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked trigger and corresponding content
            trigger.classList.add('active');
            const tabId = trigger.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Copy functionality for inline code and code blocks
    const copyButtons = document.querySelectorAll('.btn-icon[data-copy], .copy-button');

    copyButtons.forEach(button => {
        button.addEventListener('click', async () => {
            let textToCopy;
            let successMessage;

            if (button.hasAttribute('data-copy')) {
                // For inline code
                textToCopy = button.getAttribute('data-copy');
                successMessage = 'API url copied to clipboard';
            } else {
                // For code blocks
                const codeBlock = button.closest('.code-block');
                const codeElement = codeBlock.querySelector('code');
                textToCopy = codeElement.textContent;

                // Determine code type based on class or content analysis
                let codeType = 'Code';

                // Check for language class (hljs adds language classes)
                if (codeElement.className) {
                    const classNames = codeElement.className.split(' ');
                    for (const className of classNames) {
                        if (className.startsWith('language-')) {
                            codeType = className.replace('language-', '');
                            break;
                        }
                    }
                }

                // If no class found, try to detect from content
                if (codeType === 'Code') {
                    const content = textToCopy.toLowerCase();
                    if (content.includes('function') && (content.includes('var ') || content.includes('let ') || content.includes('const '))) {
                        codeType = 'JavaScript';
                    } else if (content.includes('import ') && content.includes('def ')) {
                        codeType = 'Python';
                    } else if (content.trim().startsWith('{') && content.trim().endsWith('}')) {
                        codeType = 'JSON';
                    } else if (content.includes('curl ')) {
                        codeType = 'cURL command';
                    } else if (content.includes('<html') || content.includes('<!doctype')) {
                        codeType = 'HTML';
                    } else if (content.includes('@media') || content.includes('{') && content.includes('}') && content.includes(':')) {
                        codeType = 'CSS';
                    } else if (content.includes('package main') && content.includes('import (') && content.includes('func ')) {
                        codeType = 'Golang';
                    } else if (content.includes('use ') && content.includes('fn ') && (content.includes('struct ') || content.includes('impl '))) {
                        codeType = 'Rust';
                    }
                }

                // Capitalize first letter
                codeType = codeType.charAt(0).toUpperCase() + codeType.slice(1);
                if (codeType === 'Json') {
                    successMessage = 'Response copied to clipboard';
                } else {
                    successMessage = `${codeType} codeblock copied to clipboard`;
                }
            }

            try {
                await navigator.clipboard.writeText(textToCopy);

                // Visual feedback
                const icon = button.querySelector('.bx');
                icon.classList.remove('bx-copy');
                icon.classList.add('bx-check');

                // Show notification
                showGlobalNotif('success', successMessage);

                setTimeout(() => {
                    icon.classList.remove('bx-check');
                    icon.classList.add('bx-copy');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy text:', err);
                showGlobalNotif('error', 'Failed to copy text');
            }
        });
    });

    // Initialize highlight.js syntax highlighting
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('pre code').forEach((block) => {
            // hljs.highlightBlock(block);
            hljs.highlightElement(block);
        });
    }
});


function showApiTab(event) {
    if (event) {
        event.preventDefault()
    }
    const apiButton = document.querySelector(".sidebar-item[data-at=\"api-keys\"]")
    apiButton.click()
}



