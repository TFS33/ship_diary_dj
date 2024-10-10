document.addEventListener('DOMContentLoaded', function() {
            var messageContainer = document.getElementById('message-container');
            if (messageContainer) {
                setTimeout(function() {
                    messageContainer.style.transition = 'opacity 1s ease-out';
                    messageContainer.style.opacity = '0';
                    setTimeout(function() {
                        messageContainer.style.display = 'none';
                    }, 1000);
                }, 5000);  // Wait 5 seconds before starting to fade out
            }
        });