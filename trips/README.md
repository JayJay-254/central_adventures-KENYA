# Central Adventures Website Documentation

Welcome to the Central Adventures website! This document provides an overview of the website structure, features, and how to use it.

## Project Overview

Central Adventures is a frontend website for an adventure company in Kenya. The site allows users to browse upcoming trips, contact the company, and manage their profiles.

**Technology Stack:**
- HTML5
- CSS3
- JavaScript (Vanilla)
- Formsplee (for contact form)
- LocalStorage (for user data)

## File Structure

```
Central Adventures/
├── index.html              # Landing page (homepage)
├── login.html              # Login page
├── signup.html             # Registration page
├── destinations.html       # Our Destinations page (main page after login)
├── edit-profile.html       # Edit profile page
├── gallery.html            # Gallery page (placeholder)
├── contacts.html           # Contact form page
├── css/
│   └── styles.css         # All styling
├── js/
│   └── main.js            # All JavaScript functionality
├── images/                # Folder for images (currently uses online placeholders)
└── README.md              # This file
```

## Page Descriptions

### 1. Landing Page (index.html)
**Purpose:** First page visitors see when they arrive at the website

**Features:**
- Hero section with adventure-themed background
- "About Us" button that smoothly scrolls to the about section
- "Get Started" button that takes users to login
- Detailed about section explaining Central Adventures
- Shared footer with social media links

**Access:** Public (no login required)

**Note:** Once logged in, users cannot access this page and will be redirected to destinations

### 2. Login Page (login.html)
**Purpose:** Allows existing users to log into the platform

**Features:**
- Email and password input fields
- Password visibility toggle
- Link to signup page for new users
- Form validation

**How it works:**
- Checks credentials against data stored in browser's localStorage
- Redirects to destinations page on successful login

### 3. Signup Page (signup.html)
**Purpose:** Allows new users to create an account

**Features:**
- Profile picture upload (optional)
- First name and last name fields
- Username selection
- Age input
- Email address
- Password with visibility toggle
- Re-enter password with match indicator
- Location dropdown (all major Kenyan cities)
- Bio text area (optional)
- Contact info field (optional)
- Link to login page for existing users

**Password Matching:**
- Green checkmark appears when passwords match
- Red X appears when passwords don't match
- Submit button works only when passwords match

**Data Storage:**
- All user data is stored in browser's localStorage
- Profile picture is stored as base64 encoded string

### 4. Our Destinations Page (destinations.html)
**Purpose:** Main page showing available trips and adventures

**Features:**
- Header with navigation and user menu
- Grid of destination cards
- Each card shows:
  - Background image of the destination
  - Title
  - Short description (one line)
  - "View Details" button
- Modal popup with full details when card is clicked

**Dummy Destinations:**
1. **Mount Kenya Expedition** - 5-day hiking trip
2. **Diani Beach Getaway** - 3-day coastal retreat

**Modal Details Include:**
- Large destination image
- Full description
- Location
- Duration
- What to expect
- What to bring
- Price
- "Book Now" button

**Access:** Requires login

### 5. Edit Profile Page (edit-profile.html)
**Purpose:** Allows users to update their account information

**Features:**
- All fields from signup page
- Pre-filled with current user data
- Profile picture update
- Save changes button
- Cancel button to return to destinations

**Access:** Requires login (accessible from user dropdown menu)

### 6. Gallery Page (gallery.html)
**Purpose:** Placeholder page for future photo gallery

**Features:**
- Header and footer
- "Coming Soon" message
- Empty state placeholder

**Access:** Requires login

### 7. Contact Page (contacts.html)
**Purpose:** Allows users to send messages to Central Adventures

**Features:**
- Contact form with fields:
  - Name
  - Email
  - Subject
  - Message
- Formsplee integration for sending emails
- Success/error status messages
- Form validation

**Access:** Requires login

## Navigation Structure

### Before Login:
- Landing Page → Login Page → Signup Page
- User can freely move between login and signup

### After Login:
- Main navigation available on all pages:
  - Bookings (Destinations)
  - Gallery
  - Contacts
- User menu dropdown (top right):
  - Edit Profile
  - Logout

### Shared Elements:
- Footer appears on all pages with:
  - Company info
  - Social media links (placeholders)
  - Contact information

## Key Features

### 1. Authentication System
- Simple localStorage-based authentication
- Pages are protected and redirect to login if not authenticated
- Login state persists across browser sessions

### 2. Password Features
- Toggle visibility (eye icon)
- Real-time password match validation on signup
- Secure password storage in localStorage

### 3. Profile Management
- Image upload with preview
- All profile fields editable
- Data persistence using localStorage

### 4. Destination Browsing
- Visual card-based layout
- Smooth modal popup for details
- Responsive design

### 5. Contact Form
- Formsplee integration
- Form validation
- Status feedback (success/error messages)

## Design Theme

**Adventure-Themed Color Palette:**
- Primary Color: Orange (#d97706) - represents adventure and energy
- Secondary Color: Teal (#0f766e) - represents nature and Kenya's landscapes
- Accent Color: Red (#dc2626) - for important actions
- Dark backgrounds with light text for headers/footer
- Clean, modern design with smooth animations

**Typography:**
- System fonts for fast loading
- Clear hierarchy with different font sizes
- Readable line heights and spacing

**Responsive Design:**
- Mobile-friendly layout
- Adapts to different screen sizes
- Touch-friendly buttons and links

## Data Storage

The website uses browser localStorage to store:
- User authentication state (`isLoggedIn`)
- User profile data (`userData`)

**Note:** This is temporary storage for development. In production, this should be replaced with a proper backend database.

## Adding Custom Images

To add your own destination images:
1. Place images in the `images/` folder
2. Update the image URLs in:
   - `destinations.html` (background-image styles)
   - `js/main.js` (destinationsData object)

Current images use Unsplash placeholders:
- Mount Kenya: https://images.unsplash.com/photo-1589182373726-e4f658ab50f0
- Diani Beach: https://images.unsplash.com/photo-1559827260-dc66d52bef19

## Future Enhancements

This is a frontend prototype. For a production website, you'll need:

1. **Backend Integration:**
   - Django backend (as mentioned in requirements)
   - Database for user management
   - Proper authentication system
   - API endpoints for destinations

2. **Features to Add:**
   - Booking system
   - Payment processing
   - Gallery with uploaded photos
   - User reviews and ratings
   - Trip calendar
   - Admin panel

3. **Security:**
   - Proper password hashing
   - HTTPS connections
   - CSRF protection
   - Input sanitization

## Browser Support

The website works on:
- Chrome (recommended)
- Firefox
- Safari
- Edge
- Opera

Requires JavaScript to be enabled.

## Getting Started

1. **Open the website:**
   - Simply open `index.html` in your web browser
   - No server setup needed for basic functionality

2. **Create an account:**
   - Click "Get Started" or navigate to signup.html
   - Fill in the required fields
   - Click "Create Account"

3. **Login:**
   - Use the email and password you created
   - You'll be redirected to the destinations page

4. **Explore:**
   - Browse destinations
   - Click on a destination to see full details
   - Update your profile
   - Send a message via the contact form

## Contact Form Setup

To make the contact form work, you must:
1. Set up a Formsplee account
2. Configure your email service
3. Update the credentials in `js/main.js`

## Troubleshooting

### Can't login after signup
- Make sure you're using the exact email and password
- Check that JavaScript is enabled
- Try clearing browser cache and signing up again

### Images not loading
- Check your internet connection (current images are hosted online)
- Replace with local images if needed

### Contact form not working
- Make sure Formsplee is properly configured
- Check browser console for errors (F12)
- Verify your Formsplee credentials in main.js

### Page redirects immediately
- This is normal if you're logged in and try to access index.html
- Or if you're not logged in and try to access protected pages

## Development Notes

**Code Style:**
- Comments are kept simple and straightforward
- Functions are named descriptively
- Code is organized by feature/page

**Best Practices:**
- Semantic HTML5 elements used throughout
- CSS organized by component
- JavaScript uses event delegation where appropriate
- No external dependencies except Formsplee

## Credits

**Design & Development:** Central Adventures Website Team
**Images:** Unsplash (placeholder images)
**Icons:** Unicode emoji characters (simple solution, no icon library needed)

---

**Version:** 1.0
**Last Updated:** December 2025

For questions or issues, please use the contact form on the website.
