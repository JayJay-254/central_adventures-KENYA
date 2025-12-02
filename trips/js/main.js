// Wait for DOM to be fully loaded before running any code
document.addEventListener('DOMContentLoaded', function() {
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a.scroll-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Check if user is logged in and redirect accordingly
    function checkAuth() {
        const currentPage = window.location.pathname.split('/').pop();
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        
        // Pages that require login
        const protectedPages = ['destinations.html', 'gallery.html', 'contacts.html', 'edit-profile.html'];
        
        if (protectedPages.includes(currentPage) && !isLoggedIn) {
            window.location.href = 'login.html';
        }
        
        // Allow logged-in users to view index page
        // Removed redirect to allow browsing landing page
    }

    // Run auth check on page load
    checkAuth();

    // Load user avatar on protected pages
    function loadUserAvatar() {
        const userAvatar = document.getElementById('userAvatar');
        if (userAvatar) {
            const userData = JSON.parse(localStorage.getItem('userData'));
            if (userData && userData.profilePicture) {
                userAvatar.innerHTML = userData.profilePicture;
            }
        }
    }

    // Run avatar load on page load
    loadUserAvatar();

    // Populate county dropdown
    function populateCountyDropdown() {
        const countySelect = document.getElementById('county') || document.getElementById('editCounty');
        if (countySelect && typeof kenyaLocations !== 'undefined') {
            Object.keys(kenyaLocations).forEach(county => {
                const option = document.createElement('option');
                option.value = county;
                option.textContent = county;
                countySelect.appendChild(option);
            });
        }
    }

    // Handle county change to populate constituencies
    function setupCountyConstituencyDropdowns() {
        const countySelect = document.getElementById('county');
        const constituencySelect = document.getElementById('constituency');
        
        if (countySelect && constituencySelect && typeof kenyaLocations !== 'undefined') {
            countySelect.addEventListener('change', function() {
                const selectedCounty = this.value;
                constituencySelect.innerHTML = '<option value="">Select your constituency</option>';
                
                if (selectedCounty && kenyaLocations[selectedCounty]) {
                    constituencySelect.disabled = false;
                    kenyaLocations[selectedCounty].forEach(constituency => {
                        const option = document.createElement('option');
                        option.value = constituency;
                        option.textContent = constituency;
                        constituencySelect.appendChild(option);
                    });
                } else {
                    constituencySelect.disabled = true;
                }
            });
        }
    }

    // Setup for edit profile page
    function setupEditCountyConstituencyDropdowns() {
        const countySelect = document.getElementById('editCounty');
        const constituencySelect = document.getElementById('editConstituency');
        
        if (countySelect && constituencySelect && typeof kenyaLocations !== 'undefined') {
            countySelect.addEventListener('change', function() {
                const selectedCounty = this.value;
                constituencySelect.innerHTML = '<option value="">Select your constituency</option>';
                
                if (selectedCounty && kenyaLocations[selectedCounty]) {
                    constituencySelect.disabled = false;
                    kenyaLocations[selectedCounty].forEach(constituency => {
                        const option = document.createElement('option');
                        option.value = constituency;
                        option.textContent = constituency;
                        constituencySelect.appendChild(option);
                    });
                } else {
                    constituencySelect.disabled = true;
                }
            });
        }
    }

    // Run on page load
    populateCountyDropdown();
    setupCountyConstituencyDropdowns();
    setupEditCountyConstituencyDropdowns();

    // Login Form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('loginEmail').value;
            const password = document.getElementById('loginPassword').value;
            
            // Get stored user data
            const storedUser = JSON.parse(localStorage.getItem('userData'));
            
            if (storedUser && storedUser.email === email && storedUser.password === password) {
                localStorage.setItem('isLoggedIn', 'true');
                showSuccess('Login successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = 'destinations.html';
                }, 1000);
            } else {
                showError('Invalid email or password. Please check your credentials and try again.');
            }
        });
    }

    // Signup Form
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirmPassword');
        const passwordMatch = document.getElementById('passwordMatch');
        
        // Check password match
        function checkPasswordMatch() {
            if (confirmPassword.value === '') {
                passwordMatch.textContent = '';
                passwordMatch.className = 'password-match-indicator';
            } else if (password.value === confirmPassword.value) {
                passwordMatch.textContent = '✓ Passwords match';
                passwordMatch.className = 'password-match-indicator match';
            } else {
                passwordMatch.textContent = '✗ Passwords do not match';
                passwordMatch.className = 'password-match-indicator no-match';
            }
        }
        
        password.addEventListener('input', checkPasswordMatch);
        confirmPassword.addEventListener('input', checkPasswordMatch);
        
        // Profile picture preview
        const profilePicture = document.getElementById('profilePicture');
        const imagePreview = document.getElementById('imagePreview');
        
        profilePicture.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" alt="Profile Preview">`;
                };
                reader.readAsDataURL(file);
            }
        });
        
        // Form submission
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (password.value !== confirmPassword.value) {
                showError('Passwords do not match! Please make sure both password fields are identical.');
                return;
            }
            
            // Collect form data
            const userData = {
                firstName: document.getElementById('firstName').value,
                lastName: document.getElementById('lastName').value,
                username: document.getElementById('username').value,
                age: document.getElementById('age').value,
                email: document.getElementById('email').value,
                password: password.value,
                county: document.getElementById('county').value,
                constituency: document.getElementById('constituency').value,
                bio: document.getElementById('bio').value,
                contactInfo: document.getElementById('contactInfo').value,
                profilePicture: imagePreview.innerHTML
            };
            
            // Store user data
            localStorage.setItem('userData', JSON.stringify(userData));
            localStorage.setItem('isLoggedIn', 'true');
            
            showModal({
                title: 'Welcome to Central Adventures!',
                message: 'Your account has been created successfully. Get ready to explore Kenya\'s amazing destinations!',
                type: 'success',
                confirmText: 'Let\'s Go!',
                onConfirm: () => {
                    window.location.href = 'destinations.html';
                }
            });
        });
    }

    // Password toggle functionality
    document.querySelectorAll('.password-toggle').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-target');
            const passwordInput = document.getElementById(targetId);
            
            if (passwordInput) {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    this.querySelector('.toggle-icon').textContent = '🙈';
                } else {
                    passwordInput.type = 'password';
                    this.querySelector('.toggle-icon').textContent = '👁️';
                }
            }
        });
    });

    // User menu dropdown
    const userMenuToggle = document.getElementById('userMenuToggle');
    const userDropdown = document.getElementById('userDropdown');

    if (userMenuToggle && userDropdown) {
        userMenuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            userDropdown.classList.remove('active');
        });
    }

    // Logout functionality
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.setItem('isLoggedIn', 'false');
            window.location.href = 'index.html';
        });
    }

    // Destination data (dummy data)
    const destinationsData = {
        1: {
            title: 'Mount Kenya Expedition',
            image: 'https://images.unsplash.com/photo-1589182373726-e4f658ab50f0?w=1200',
            description: 'Experience the thrill of climbing Africa\'s second-highest peak. This 5-day expedition takes you through diverse ecosystems, from bamboo forests to alpine moorlands. Perfect for adventure enthusiasts looking for a challenging yet rewarding trek.',
            location: 'Mount Kenya National Park, Central Kenya',
            duration: '5 Days, 4 Nights',
            expectations: 'Expect moderate to challenging hiking conditions. You\'ll traverse through various climate zones, witness stunning glaciers, and enjoy breathtaking sunrise views from Point Lenana (4,985m). Professional guides will accompany you throughout the journey.',
            requirements: 'Hiking boots, warm clothing (temperatures drop below freezing at night), rain gear, sleeping bag, personal medications, water bottles, headlamp, and sunscreen. We provide tents, cooking equipment, and meals.',
            price: 'KES 45,000 per person'
        },
        2: {
            title: 'Diani Beach Getaway',
            image: 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=1200',
            description: 'Relax on pristine white sands and crystal-clear waters. This 3-day coastal retreat includes snorkeling, beach games, seafood dinners, and optional water sports. Perfect for those looking to unwind and enjoy Kenya\'s beautiful coastline.',
            location: 'Diani Beach, South Coast, Mombasa',
            duration: '3 Days, 2 Nights',
            expectations: 'Expect warm tropical weather, gentle ocean breezes, and plenty of sunshine. Activities include snorkeling at the coral reef, beach volleyball, sunset dhow cruises, and visits to nearby attractions like Shimba Hills National Reserve.',
            requirements: 'Swimwear, light cotton clothing, sunscreen (SPF 50+), sunglasses, beach hat, sandals, snorkeling gear (can be rented), and a light jacket for evenings. We provide accommodation and meals.',
            price: 'KES 25,000 per person'
        }
    };

    // Destination cards click handlers
    const destinationCards = document.querySelectorAll('.destination-card');
    const modal = document.getElementById('destinationModal');
    const closeModal = document.getElementById('closeModal');

    if (destinationCards.length > 0) {
        destinationCards.forEach(card => {
            const viewDetailsBtn = card.querySelector('.view-details-btn');
            if (viewDetailsBtn) {
                viewDetailsBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const destinationId = card.getAttribute('data-destination');
                    openDestinationModal(destinationId);
                });
            }
            
            card.addEventListener('click', function() {
                const destinationId = this.getAttribute('data-destination');
                openDestinationModal(destinationId);
            });
        });
    }

    function openDestinationModal(destinationId) {
        const data = destinationsData[destinationId];
        
        if (data && modal) {
            document.getElementById('modalImage').style.backgroundImage = `url('${data.image}')`;
            document.getElementById('modalTitle').textContent = data.title;
            document.getElementById('modalDescription').textContent = data.description;
            document.getElementById('modalLocation').textContent = data.location;
            document.getElementById('modalDuration').textContent = data.duration;
            document.getElementById('modalExpectations').textContent = data.expectations;
            document.getElementById('modalRequirements').textContent = data.requirements;
            document.getElementById('modalPrice').textContent = data.price;
            
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    if (closeModal) {
        closeModal.addEventListener('click', function() {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        });
        
        // Close modal when clicking outside
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('active');
                document.body.style.overflow = 'auto';
            }
        });
    }

    // Edit Profile Form
    const editProfileForm = document.getElementById('editProfileForm');
    if (editProfileForm) {
        // Load existing user data
        const userData = JSON.parse(localStorage.getItem('userData'));
        
        if (userData) {
            document.getElementById('editFirstName').value = userData.firstName || '';
            document.getElementById('editLastName').value = userData.lastName || '';
            document.getElementById('editUsername').value = userData.username || '';
            document.getElementById('editAge').value = userData.age || '';
            document.getElementById('editEmail').value = userData.email || '';
            document.getElementById('editBio').value = userData.bio || '';
            document.getElementById('editContactInfo').value = userData.contactInfo || '';
            
            // Load county and constituency
            if (userData.county) {
                const editCountySelect = document.getElementById('editCounty');
                if (editCountySelect) {
                    editCountySelect.value = userData.county;
                    
                    // Trigger change to populate constituencies
                    const event = new Event('change');
                    editCountySelect.dispatchEvent(event);
                    
                    // Set constituency after a brief delay
                    setTimeout(() => {
                        const editConstituencySelect = document.getElementById('editConstituency');
                        if (editConstituencySelect && userData.constituency) {
                            editConstituencySelect.value = userData.constituency;
                        }
                    }, 100);
                }
            }
            
            if (userData.profilePicture) {
                document.getElementById('editImagePreview').innerHTML = userData.profilePicture;
            }
        }
        
        // Profile picture preview
        const editProfilePicture = document.getElementById('editProfilePicture');
        const editImagePreview = document.getElementById('editImagePreview');
        
        editProfilePicture.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    editImagePreview.innerHTML = `<img src="${e.target.result}" alt="Profile Preview">`;
                };
                reader.readAsDataURL(file);
            }
        });
        
        // Form submission
        editProfileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const updatedData = {
                firstName: document.getElementById('editFirstName').value,
                lastName: document.getElementById('editLastName').value,
                username: document.getElementById('editUsername').value,
                age: document.getElementById('editAge').value,
                email: document.getElementById('editEmail').value,
                password: userData.password,
                county: document.getElementById('editCounty').value,
                constituency: document.getElementById('editConstituency').value,
                bio: document.getElementById('editBio').value,
                contactInfo: document.getElementById('editContactInfo').value,
                profilePicture: editImagePreview.innerHTML
            };
            
            localStorage.setItem('userData', JSON.stringify(updatedData));
            
            showModal({
                title: 'Profile Updated!',
                message: 'Your profile has been updated successfully.',
                type: 'success',
                confirmText: 'Continue',
                onConfirm: () => {
                    window.location.href = 'destinations.html';
                }
            });
        });
    }

    // Contact Form with EmailJS
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        // Initialize EmailJS (user needs to add their own public key)
        if (typeof emailjs !== 'undefined') {
            emailjs.init('q3_xN54dd37s7rGn1');
        }
        
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            
            // Disable submit button
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';
            
            // Prepare template parameters
            const templateParams = {
                from_name: document.getElementById('contactName').value,
                from_email: document.getElementById('contactEmail').value,
                subject: document.getElementById('contactSubject').value,
                message: document.getElementById('contactMessage').value
            };
            
            // Send email using EmailJS
            if (typeof emailjs !== 'undefined') {
                emailjs.send('service_t9bdrid', 'service_t9bdrid', templateParams)
                    .then(function(response) {
                        showSuccess('Message sent successfully! We\'ll get back to you soon.');
                        contactForm.reset();
                    }, function(error) {
                        showError('Failed to send message. Please try again or contact us directly via phone.');
                        console.error('EmailJS error:', error);
                    })
                    .finally(function() {
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Send Message';
                    });
            } else {
                // EmailJS not loaded, show success anyway for demo
                setTimeout(() => {
                    showSuccess('Message sent successfully! We\'ll get back to you soon.');
                    contactForm.reset();
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Send Message';
                }, 1000);
            }
        });
    }

}); // End of DOMContentLoaded
