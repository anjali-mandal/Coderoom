import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import './home.css'
import apiClient from '../../services/apiClient'

const Home = () => {

    const navigate = useNavigate()
    const { logout, user } = useAuth()
    const [projects, setProjects] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    function navigateToProject(projectId) {
        navigate(`/project/${projectId}`)
    }

    function handleLogout() {
        logout()
        navigate('/login')
    }

    useEffect(() => {
        apiClient.get('/projects/get-all')
            .then(response => {
                setProjects(response.data.data)
            })
            .catch((error) => {
                console.error('Error fetching projects:', error)
                setError('Unable to load projects. Please try again.')
            })
            .finally(() => {
                setLoading(false)
            })
    }, [])

    return (
        <main className='home'>
            <section className='home-section'>
                <header className="home-header">
                    <div className="brand-lockup">
                        <span className="brand-mark">/</span>
                        <span>CodeRoom</span>
                    </div>
                    <button onClick={handleLogout} className="logout-btn">Logout</button>
                </header>

                <div className="home-intro">
                    <div>
                        <p className="eyebrow">YOUR WORKSPACE</p>
                        <h1>Good to see you, {user?.name || 'there'}.</h1>
                        <p className="intro-copy">Pick up where you left off or start something new.</p>
                    </div>
                    <button className="new-project-btn" onClick={() => navigate('/create-project')}>
                        <span>+</span> New project
                    </button>
                </div>

                <div className="projects-heading">
                    <div>
                        <p className="eyebrow">COLLECTION</p>
                        <h2>Your projects</h2>
                    </div>
                    <span>{projects.length} total</span>
                </div>

                {loading ? (
                    <div className="projects-state"><p>Loading your workspace...</p></div>
                ) : error ? (
                    <div className="projects-state projects-error"><p>{error}</p></div>
                ) : projects.length === 0 ? (
                    <div className="projects-state empty-state">
                        <span className="empty-icon">+</span>
                        <h3>Your first project starts here.</h3>
                        <p>Create a workspace to start writing code and invite collaborators.</p>
                        <button className="new-project-btn" onClick={() => navigate('/create-project')}>Create project</button>
                    </div>
                ) : (
                    <div className="projects">
                        {projects.map((project) => {
                            return (
                                <div
                                    key={project._id}
                                    onClick={() => {
                                        navigateToProject(project._id)
                                    }}
                                    className="project"
                                >
                                    <div className="project-icon">{project.name.charAt(0).toUpperCase()}</div>
                                    <div className="project-copy">
                                        <strong>{project.name}</strong>
                                        <span>Open workspace <b>↗</b></span>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                )}
            </section>
        </main>
    )
}

export default Home
