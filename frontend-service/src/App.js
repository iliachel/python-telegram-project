import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import AdminPage from './components/AdminPage';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

function Navigation() {
    const { user } = useAuth();

    return (
        <nav>
            <Link to="/">Home</Link> |{' '}
            {user ? (
                <Link to="/admin">Admin</Link>
            ) : (
                <>
                    <Link to="/login">Login</Link> |{' '}
                    <Link to="/register">Register</Link>
                </>
            )}
        </nav>
    );
}

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="App">
                    <Navigation />
                    <hr />
                    <Routes>
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/register" element={<RegisterPage />} />
                        <Route path="/" element={<h1>Home Page</h1>} />

                        {/* Protected Route */}
                        <Route path="/admin" element={<ProtectedRoute />}>
                            <Route index element={<AdminPage />} />
                        </Route>
                    </Routes>
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;
