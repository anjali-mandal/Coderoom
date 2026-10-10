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
    const [memberEmails, setMemberEmails] = useState({})
    const [memberMessages, setMemberMessages] = useState({})
    const [invitingProject, setInvitingProject] = useState(null)

    function navigateToProject(projectId) {
        navigate(`/project/${projectId}`)
    }

    function handleLogout() {
        logout()
        navigate('/login')
    }

    function updateMemberEmail(projectId, email) {
        setMemberEmails((current) => ({ ...current, [projectId]: email }))
    }

    async function inviteMember(event, projectId) {
        event.preventDefault()
        event.stopPropagation()

        const email = (memberEmails[projectId] || '').trim()
        if (!email) {
            setMemberMessages((current) => ({ ...current, [projectId]: 'Enter the member email first.' }))
            return
        }

        setInvitingProject(projectId)
        setMemberMessages((current) => ({ ...current, [projectId]: '' }))
        try {
            const response = await apiClient.post(`/projects/${projectId}/members`, { email })
            setMemberEmails((current) => ({ ...current, [projectId]: '' }))
            setMemberMessages((current) => ({
                ...current,
                [projectId]: `${response.data.data.name} added to this project.`,
            }))
        } catch (requestError) {
            const detail = requestError.response?.data?.detail
            const message = Array.isArray(detail)
                ? detail.map((item) => item.msg).join(', ')
                : detail || requestError.message
            setMemberMessages((current) => ({
                ...current,
                [projectId]: message || 'Unable to add this member.',
            }))
        } finally {
            setInvitingProject(null)
        }
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
                                <div className="project-item" key={project._id}>
                                    <div
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
                                    <form
                                        className="home-member-invite"
                                        onSubmit={(event) => inviteMember(event, project._id)}
                                    >
                                        <input
                                            type="email"
                                            value={memberEmails[project._id] || ''}
                                            onChange={(event) => updateMemberEmail(project._id, event.target.value)}
                                            onClick={(event) => event.stopPropagation()}
                                            placeholder="Invite by email"
                                            aria-label={`Invite a member to ${project.name}`}
                                            required
                                        />
                                        <button type="submit" disabled={invitingProject === project._id}>
                                            {invitingProject === project._id ? 'Adding...' : 'Add member'}
                                        </button>
                                        {memberMessages[project._id] && (
                                            <small role="status">{memberMessages[project._id]}</small>
                                        )}
                                    </form>
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
