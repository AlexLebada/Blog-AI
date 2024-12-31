// ensure script runs after HTML parsing and get access to all the elements of that HTML content
document.addEventListener('DOMContentLoaded', function() {
    const chatlog = document.getElementById('chatlog');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('query');
    const fileUploadContainer = document.getElementById('file-upload-container');
    const fileUploadInput = document.getElementById('file-upload');
    const fileSubmitButton = document.getElementById('file-submit');
    const optionsForm = document.getElementById('options-form');
    const postForm = document.getElementById('post-form');
    const SelectionContainer = document.getElementById('file-dropdown');

    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                return cookie.substring('csrftoken='.length);
            }
        }
        return null;
    }

    // chatbot functionality
    chatForm.addEventListener('submit', function(event) {
        //prevents page reload
        event.preventDefault();

        // Get user input
        const optionsForm = document.querySelector('#options-form');
        const selectedOption = optionsForm.querySelector('input[name="option"]:checked').value;
        const userMessage = userInput.value;

        const selectedDropdown = SelectionContainer.value;
        const FileUploadValue = fileSubmitButton.value
        console.log("filesubmit:",FileUploadValue)
        console.log("selected_dropdown: ",selectedDropdown)
        console.log("selected_option: ",selectedOption)

        // Clear the input field
        userInput.value = '';

        // Add the user message to the chat log
        chatlog.innerHTML += '<p class="user-message"><i>Q: ' + userMessage + '</i></p>';

        const csrfToken = getCSRFToken();

        const bodyData = new URLSearchParams();
        bodyData.append('query', userMessage);
        bodyData.append('selected_dropdown', selectedDropdown);
        bodyData.append('selected_option', selectedOption);
        bodyData.append('file_upload_value', FileUploadValue);
        bodyData.append('submit_chatbot', 'true');

        // Send the user message to the server and get the response
        fetch('/writer_panel/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'X-CSRFToken': csrfToken
            },
            body: bodyData.toString()
        })
        .then(response => response.json())
        .then(data => {
                chatlog.innerHTML += `<p class="bot-message"><b>A: ${data.answer}</b></p>`;
            // Scroll to the bottom of the chat log
            chatlog.scrollTop = chatlog.scrollHeight;
        });
    });

    // Show/hide file upload container based on selected option
    optionsForm.addEventListener('change', function () {
        const selectedOption = document.querySelector('input[name="option"]:checked');
        if (selectedOption && (selectedOption.value === 'option2' || selectedOption.value === 'option3')) {
            fileUploadContainer.style.display = 'flex';
        } else {
            fileUploadContainer.style.display = 'none';
        }
    });

    fileUploadInput.addEventListener('click', function () {
        fileSubmitButton.disabled = false;
        fileSubmitButton.innerText = 'Process';
    })

    // Handle the file upload functionality
    fileSubmitButton.addEventListener('click', function () {
        const csrfToken = getCSRFToken();
        const file = fileUploadInput.files[0];


        fileSubmitButton.disabled = true;
        fileSubmitButton.innerText = 'Processing...';

        if (file) {
            const formData = new FormData();
            formData.append('file', file);

        formData.append('submit_file', 'true');

            fetch('/upload-file/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {

                    if (data.message) {
                    console.log(`File uploaded successfully: ${data.file_name}`)
                    console.log(data.message); // Show success message
                    fileSubmitButton.innerText = 'Processed';
                    fileSubmitButton.value = data.file_name
                    SelectionContainer.value = ""
                    } else if (data.error) {
                        console.log('Error: ' + data.error);
                         fileSubmitButton.disabled = true;// Handle errors
                         fileSubmitButton.innerText = 'wait..';
                    }

                })
                .catch((error) => {
                    console.error('Error uploading file:', error);
                });
        } else {
            console.error('Please select a file to upload.');
        }
    });


    postForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent page reload

        const formData = new FormData(postForm); // Collect form data including the file
        formData.append('submit_post', 'true')
        const csrfToken = getCSRFToken();

        fetch('/writer_panel/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken, // Include CSRF token
            },
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    console.log(data.message); // Show success message
                    postForm.reset()
                } else if (data.error) {
                    console.log('Error: ' + data.error); // Handle errors
                }
            })
            .catch(error => console.error('Error submitting post form:', error));
    });


    SelectionContainer.addEventListener('change', function (event) {
        fileSubmitButton.value = ""
    })

});