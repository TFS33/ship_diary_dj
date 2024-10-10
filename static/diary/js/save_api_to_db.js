// document.addEventListener('DOMContentLoaded', function() {
//     const messagesContainer = document.getElementById('messages-container');
//
//     function displayMessage(message, isError = false) {
//         const messageElement = document.createElement('div');
//         messageElement.textContent = message;
//         messageElement.className = isError ? 'error-message' : 'success-message';
//         messageElement.style.padding = '10px';
//         messageElement.style.marginBottom = '10px';
//         messageElement.style.backgroundColor = isError ? '#ffcccc' : '#ccffcc';
//         messageElement.style.border = `1px solid ${isError ? '#ff0000' : '#00ff00'}`;
//         messageElement.style.opacity = '1';
//         messageElement.style.transition = 'opacity 1s ease-out';
//         messagesContainer.appendChild(messageElement);
//
//         // Remove the message after 5 seconds with a fade-out effect
//         setTimeout(() => {
//             messageElement.style.opacity = '0';
//             setTimeout(() => {
//                 messagesContainer.removeChild(messageElement);
//             }, 1000);
//         }, 5000);
//     }
//
//     function handleFormSubmit(event) {
//         event.preventDefault();
//         const form = event.target;
//         const formData = new FormData(form);
//
//         fetch(form.action, {
//             method: 'POST',
//             body: formData,
//             headers: {
//                 'X-Requested-With': 'XMLHttpRequest',
//                 'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
//             },
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 displayMessage(data.message);
//             } else {
//                 displayMessage(data.message, true);
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             displayMessage('An error occurred while saving the data.', true);
//         });
//     }
//
//     // Handle save forecast forms
//     const saveForecastForms = document.querySelectorAll('.save-forecast-form');
//     saveForecastForms.forEach(form => {
//         form.addEventListener('submit', handleFormSubmit);
//     });
//
//     // Handle main weather form
//     const weatherForm = document.getElementById('weather-form');
//     if (weatherForm) {
//         weatherForm.addEventListener('submit', handleFormSubmit);
//     }
//
//     // Handle existing messages
//     const existingMessages = document.querySelectorAll('.message');
//     existingMessages.forEach(message => {
//         setTimeout(() => {
//             message.style.opacity = '0';
//             setTimeout(() => {
//                 message.style.display = 'none';
//             }, 1000);
//         }, 5000);
//     });
// });


document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.getElementById('messages-container');

    function displayMessage(message, tags) {
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        messageElement.className = `message ${tags}`;
        messageElement.style.padding = '10px';
        messageElement.style.marginBottom = '10px';
        messageElement.style.backgroundColor = tags === 'success' ? '#ccffcc' : '#ffcccc';
        messageElement.style.border = `1px solid ${tags === 'success' ? '#00ff00' : '#ff0000'}`;
        messageElement.style.opacity = '1';
        messageElement.style.transition = 'opacity 1s ease-out';
        messagesContainer.appendChild(messageElement);

        // Remove the message after 5 seconds with a fade-out effect
        setTimeout(() => {
            messageElement.style.opacity = '0';
            setTimeout(() => {
                messagesContainer.removeChild(messageElement);
            }, 1000);
        }, 5000);
    }

    function handleFormSubmit(event) {
        event.preventDefault(); // Prevent the default form submission

        const form = event.target;
        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .then(response => response.json())
        .then(data => {
            displayMessage(data.message, data.tags);
        })
        .catch(error => {
            console.error('Error:', error);
            displayMessage('An error occurred while saving the data.', 'error');
        });
    }

    // Handle save forecast forms
    const saveForecastForms = document.querySelectorAll('form[action$="save_to_database_marine_api"]');
    saveForecastForms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });

    // Handle existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 1000);
        }, 5000);
    });

    console.log('save_api_to_db.js loaded and executed'); // Debug log
});