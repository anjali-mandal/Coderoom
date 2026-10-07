import PropTypes from 'prop-types'
import { BrowserRouter as AppRouter, Route, Routes as AppRoutes, Navigate } from 'react-router-dom'
import Home from '../views/home/Home'
import CreateProject from '../views/create-project/CreateProject'
import Project from '../views/project/Project'
import Login from '../views/auth/Login'
import Signup from '../views/auth/Signup'
import { useAuth } from '../contexts/AuthContext'

// Protected Route component
function ProtectedRoute({ element }) {
    const { token, loading } = useAuth();
    if (loading) {
        return <div>Checking session...</div>;
    }
    return token ? element : <Navigate to="/login" />;
}

ProtectedRoute.propTypes = {
    element: PropTypes.node.isRequired,
}

const Routes = () => {
    return (
        <AppRouter>
            <AppRoutes>
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/" element={<ProtectedRoute element={<Home />} />} />
                <Route path="/create-project" element={<ProtectedRoute element={<CreateProject />} />} />
                <Route path='/project/:id' element={<ProtectedRoute element={<Project />} />} />
            </AppRoutes>
        </AppRouter>
    )
}

export default Routes