// Contact Form Handler with Formsplee Integration
// This provides client-side email sending via Formsplee

document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');

    if (!contactForm) {
        console.log('Contact form not found');
        return;
    }

    // Handle form submission
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent default form submission

        const formData = new FormData(contactForm);
        const formspleeEndpoint = 'https://formspree.io/f/YOUR_FORMSPLEE_ENDPOINT';

        fetch(formspleeEndpoint, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                alert('Message sent successfully!');
                contactForm.reset();
            } else {
                alert('Failed to send message. Please try again later.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again later.');
        });
    });
});
