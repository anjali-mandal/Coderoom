import { useState } from 'react'
import "./CreateProject.css"
import { useNavigate } from 'react-router-dom'
import apiClient from '../../services/apiClient'

const CreateProject = () => {
    const [ projectName, setProjectName ] = useState('')
    const [ error, setError ] = useState('')
    const [ loading, setLoading ] = useState(false)
    const navigate = useNavigate()

    async function handleSubmit(e) {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            await apiClient.post('/projects/create', { projectName: projectName.trim() })
            navigate('/')
        } catch {
            setError('Unable to create project. Please try again.')
        } finally {
            setLoading(false)
        }

    }

    return (
        <main className="create-project">
            <section className="create-project-section">

                <form onSubmit={handleSubmit}>
                    <input type="text"
                        name='projectName'
                        placeholder='Project Name'
                        required
                        onChange={(e) => setProjectName(e.target.value)}
                        value={projectName}
                    />

                    {error && <p role="alert">{error}</p>}
                    <input type="submit" disabled={loading} value={loading ? 'Creating...' : 'Create Project'} />
                </form>

            </section>
        </main>
    )
}

export default CreateProject