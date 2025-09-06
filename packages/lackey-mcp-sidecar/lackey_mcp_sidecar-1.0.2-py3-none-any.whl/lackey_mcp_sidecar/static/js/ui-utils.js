// UI-utils.js - Copy functionality, border pulse feedback, and modal handling

// Utility function to copy text to clipboard
function copyToClipboard(text, sourceElement) {
    navigator.clipboard.writeText(text).then(function() {
        showCopyFeedback(sourceElement);
    }).catch(function(err) {
        console.error('Failed to copy text: ', err);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showCopyFeedback(sourceElement);
    });
}

// Show copy feedback with pulsing border animation and/or top alert
function showCopyFeedback(sourceElement) {
    // Find the appropriate parent element to animate
    let targetElement = null;
    
    if (sourceElement) {
        // If called from an event, use the source element
        targetElement = sourceElement;
    } else {
        // Try to find the copy button that was clicked
        targetElement = event?.target;
    }
    
    let showAlert = false;
    
    if (targetElement) {
        // Find the closest task node, modal, or card to animate
        const parentElement = targetElement.closest('.task-node, .modal-content, .task-item, .project-item, .card');
        
        if (parentElement) {
            // Check if we're in a modal - if so, show the alert instead of just pulse
            const isInModal = parentElement.closest('.modal-content');
            
            if (isInModal) {
                showAlert = true;
            } else {
                // Add the pulse animation for non-modal elements
                parentElement.classList.add('id-copied');
                
                // Remove the class after animation completes
                setTimeout(() => {
                    parentElement.classList.remove('id-copied');
                }, 1000);
            }
        } else {
            // No suitable parent found, show alert
            showAlert = true;
        }
    } else {
        // No source element, show alert
        showAlert = true;
    }
    
    // Show top-center alert for modals or when pulse isn't suitable
    if (showAlert) {
        showCopyAlert();
    }
}

// Show glassmorphic top-center copy alert
function showCopyAlert() {
    // Remove any existing alert
    const existingAlert = document.querySelector('.copy-alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = 'copy-alert';
    alert.textContent = 'ID Copied to Clipboard!';
    document.body.appendChild(alert);
    
    // Show alert with animation
    setTimeout(() => {
        alert.classList.add('show');
    }, 10);
    
    // Hide and remove alert after 2.5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 400);
    }, 2500);
}

// Generic feedback alert function
function showFeedback(message, type = 'success') {
    // Remove any existing feedback alert
    const existingAlert = document.querySelector('.feedback-alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `feedback-alert feedback-${type}`;
    alert.textContent = message;
    document.body.appendChild(alert);
    
    // Show alert with animation
    setTimeout(() => {
        alert.classList.add('show');
    }, 10);
    
    // Hide and remove alert after 2.5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 400);
    }, 2500);
}
