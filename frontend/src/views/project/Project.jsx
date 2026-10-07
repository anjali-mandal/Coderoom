import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { io as SocketIo } from "socket.io-client"
import Editor from '@monaco-editor/react'
import ReactMarkdown from 'react-markdown'
import { useAuth } from '../../contexts/AuthContext'
import apiClient from '../../services/apiClient'
import "./Project.css"
import { SOCKET_URL } from '../../config/api'

const Project = () => {
    const prams = useParams()
    const { token, user } = useAuth()
    const [ messages, setMessages ] = useState([])
    const [ input, setInput ] = useState("")
    const [ socket, setSocket ] = useState(null)
    const [ code, setCode ] = useState("// Write your code here...\n")
    const [ language, setLanguage ] = useState("javascript")
    const [ review, setReview ] = useState("*No review yet. Click 'get-review' to generate a code review.*")
    const [ memberEmail, setMemberEmail ] = useState('')
    const [ memberMessage, setMemberMessage ] = useState('')
    const [ inviting, setInviting ] = useState(false)

    // Function to handle code changes from the editor
    function handleEditorChange(value) {
        setCode(value)
        socket.emit("code-change", value)
    }

    function handleUserMessage() {
        if (!socket || !input.trim()) {
            return
        }
        setMessages((prev) => {
            return [ ...prev, { text: input.trim(), userId: user?.id } ]
        })
        socket.emit("chat-message", input.trim())
        setInput("")
    }

    function getReview() {
        if (socket) {
            setReview(" Generating review...")
            socket.emit("get-review", code)
        } else {
            setReview(" Socket not connected yet. Please wait...")
        }
    }

    // Function to change programming language
    function changeLanguage(newLanguage) {
        setLanguage(newLanguage)
    }

    async function inviteMember(event) {
        event.preventDefault()
        setMemberMessage('')
        setInviting(true)
        try {
            const response = await apiClient.post(`/projects/${prams.id}/members`, {
                email: memberEmail.trim(),
            })
            setMemberMessage(`${response.data.data.name} added to this project.`)
            setMemberEmail('')
        } catch (error) {
            setMemberMessage(error.response?.data?.detail || 'Unable to add this member.')
        } finally {
            setInviting(false)
        }
    }

    useEffect(() => {
        if (!token) {
            console.log("No token available");
            return;
        }

        const io = SocketIo(SOCKET_URL, {
            auth: {
                token: token
            },
            query: {
                project: prams.id
            },
            transports: ['polling', 'websocket'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 5
        })

        io.on('connect', () => {
            console.log('Socket connected');
            io.emit("chat-history")
            io.emit("get-project-code")
        })

        io.on('connect_error', (error) => {
            console.error('Socket connection error:', error);
        })

        io.on('disconnect', (reason) => {
            console.log('Socket disconnected:', reason);
        })

        io.on('chat-history', (messages) => {
            setMessages(messages.map((message) => ({
                text: message.text || '',
                userId: message.user,
            })))
        })

        io.on('chat-message', (message) => {
            setMessages((prev) => {
                return [ ...prev, typeof message === 'string' ? { text: message } : message ]
            })
        })

        io.on('code-change', (code) => {
            setCode(code)
        })

        io.on('project-code', (code) => {
            setCode(code)
        })

        io.on("code-review", (review) => {
            console.log(review)
            setReview(review)
        })

        io.on('error', (error) => {
            console.error('Socket error:', error);
        })

        setSocket(io)

        return () => {
            io.disconnect()
        }
    }, [token, prams.id])

    return (
        <main className='project-main' >
            <section className='project-section' >
                <div className="chat">

                    <div className="messages">
                        {
                            messages.map((message, index) => {
                                return (<div className={`message ${message.userId === user?.id ? 'message-own' : 'message-other'}`} key={index}>
                                    <span>
                                        {message.text}
                                    </span>
                                </div>)
                            })
                        }
                    </div>

                    <div className="input-area">
                        <input
                            type="text"
                            placeholder='message to project...'
                            onChange={(e) => {
                                setInput(e.target.value)
                            }}
                            value={input}
                        />
                        <button
                            onClick={() => { handleUserMessage() }}
                        ><i className="ri-send-plane-2-fill"></i></button>
                    </div>

                </div>
                <div className="code">
                    <div className="language-selector">
                        <select
                            value={language}
                            onChange={(e) => changeLanguage(e.target.value)}
                        >
                            <option value="javascript">JavaScript</option>
                            <option value="typescript">TypeScript</option>
                            <option value="python">Python</option>
                            <option value="java">Java</option>
                            <option value="csharp">C#</option>
                            <option value="html">HTML</option>
                            <option value="css">CSS</option>
                        </select>
                    </div>
                    <Editor
                        height="90%"
                        width="100%"
                        language={language}
                        value={code}
                        onChange={handleEditorChange}
                        theme="vs-dark"
                        options={{
                            minimap: { enabled: true },
                            fontSize: 14,
                            wordWrap: 'on',
                            automaticLayout: true,
                            formatOnType: true,
                            formatOnPaste: true,
                            cursorBlinking: "smooth",
                        }}
                    />
                </div>
                <div className="review">
                    <form className="member-invite" onSubmit={inviteMember}>
                        <input
                            type="email"
                            value={memberEmail}
                            onChange={(event) => setMemberEmail(event.target.value)}
                            placeholder="Invite by email"
                            required
                        />
                        <button type="submit" disabled={inviting}>
                            {inviting ? 'Adding...' : 'Add member'}
                        </button>
                        {memberMessage && <small role="status">{memberMessage}</small>}
                    </form>
                    <div className="review-content">
                        <ReactMarkdown>{review}</ReactMarkdown>
                    </div>
                    <button
                        onClick={() => {
                            getReview()
                        }}
                        className='get-review' >
                        get-review
                    </button>
                </div>
            </section>
        </main>
    )
}

export default Project