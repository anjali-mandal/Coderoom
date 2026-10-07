# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh


# Complete Authentication System Implementation

##  Backend Setup

### 1. **User Model** (`src/models/user.model.js`)
- Email (unique)
- Password (hashed with bcrypt)
- Name
- Projects array (reference)
- Timestamps

### 2. **Authentication Service** (`src/services/auth.service.js`)
- `registerUser()` - Register new users with password hashing
- `loginUser()` - Login with email/password validation
- `verifyToken()` - Validate JWT tokens
- `getUserById()` - Fetch user data

### 3. **Auth Routes** (`src/routes/auth.routes.js`)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### 4. **Auth Controller** (`src/controllers/auth.controller.js`)
- Request validation
- Error handling
- Response formatting

### 5. **Auth Middleware** (`src/middleware/auth.middleware.js`)
- JWT token verification on HTTP routes

### 6. **Socket.io Authentication**
- Middleware added to `server.js`
- JWT verification before socket connection
- Only authenticated users can connect
- User ID and email attached to socket

---

##  Frontend Setup

### 1. **Auth Context** (`src/contexts/AuthContext.jsx`)
- User state management
- Token storage in localStorage
- `register()` - API call to register
- `login()` - API call to login
- `logout()` - Clear token and user state

### 2. **Login Page** (`src/views/auth/Login.jsx`)
- Email and password inputs
- Form validation
- Error handling
- Link to signup page

### 3. **Signup Page** (`src/views/auth/Signup.jsx`)
- Name, email, password, confirm password
- Password matching validation
- Error handling
- Link to login page

### 4. **Auth Styling** (`src/views/auth/Auth.css`)
- Beautiful gradient background
- Form styling
- Error message styling
- Responsive design

### 5. **Protected Routes** (`src/routes/Routes.jsx`)
- `ProtectedRoute` component
- Redirects to login if not authenticated
- `/login` - Login page (public)
- `/signup` - Signup page (public)
- `/` - Home (protected)
- `/create-project` - Create project (protected)
- `/project/:id` - Project details (protected)

### 6. **App Wrapper** (`src/App.jsx`)
- AuthProvider wraps entire app
- Enables useAuth hook everywhere

### 7. **Updated Components**
- **Home.jsx** - Added user greeting and logout button
- **Project.jsx** - Pass JWT token to socket.io connection
- **Home.css** - Styled logout button

---

##  Security Features

✅ Passwords hashed with bcrypt (salt: 10)  
✅ JWT tokens with 7-day expiration  
✅ Token stored in localStorage  
✅ Socket.io requires valid JWT  
✅ Protected routes redirect to login  
✅ Error handling on all endpoints  

---

##  How to Use

### Registration:
```bash
POST http://localhost:3000/auth/register
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

### Login:
```bash
POST http://localhost:3000/auth/login
{
  "email": "john@example.com",
  "password": "password123"
}
```

Returns token and user data.

### Frontend Flow:
1. User lands on app → redirected to `/login` if not authenticated
2. User signs up or logs in
3. Token saved in localStorage
4. User can access protected pages
5. Socket.io connection includes token
6. User can logout anytime

---

##  Dependencies Added

- `bcrypt@^5.1.0` - Password hashing
- `jsonwebtoken@^9.0.2` - JWT token generation
- `dotenv` - Environment variables



---

##  What's Protected Now

✅ All project operations require login  
✅ Socket.io connections require valid JWT  
✅ Chat messages tracked by user  
✅ Only authenticated users can create projects  
✅ Logout clears all session data  

**Everything is ready! Start backend with `npm start` and frontend with `npm run dev`**
