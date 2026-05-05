import { useEffect, useState, useRef } from 'react'
import GameCanvas from './GameCanvas'
import './index.css'

function App() {
  const [appState, setAppState] = useState('name_input') // 'name_input', 'connecting', 'connected'
  const [serverStatus, setServerStatus] = useState('lobby') // 'lobby', 'playing', 'gameover'
  const [name, setName] = useState('')
  const [ws, setWs] = useState(null)
  const [playerId, setPlayerId] = useState(null)
  const [spectatorMsg, setSpectatorMsg] = useState('')
  const [playersList, setPlayersList] = useState([])
  const [adminId, setAdminId] = useState(null)
  
  // A ref to store the latest server state so the canvas can access it
  const serverStateRef = useRef({
    status: 'lobby',
    admin_id: null,
    arenaRadius: 1000,
    players: [],
    pellets: []
  });

  const connect = (e) => {
    e.preventDefault()
    if (!name.trim()) return;
    
    setAppState('connecting')
    setSpectatorMsg('')

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const socket = new WebSocket(`${protocol}//${host}/ws?name=` + encodeURIComponent(name))

    socket.onopen = () => {

      setWs(socket)
      setAppState('connected')
    }
    
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data)
      
      if (message.type === 'init') {
        setPlayerId(message.data.playerId)
        serverStateRef.current.arenaRadius = message.data.arenaRadius
      } else if (message.type === 'state') {
        serverStateRef.current = message.data
        
        setServerStatus((prev) => {
            if (prev !== message.data.status) {
                if (message.data.status === 'playing') setSpectatorMsg('');
                return message.data.status;
            }
            return prev;
        });
        
        if (message.data.status === 'lobby' || message.data.status === 'gameover') {
            setAdminId(message.data.admin_id)
            setPlayersList(prev => {
                const newIds = message.data.players.map(p => p.id).join(',');
                const oldIds = prev.map(p => p.id).join(',');
                if (newIds !== oldIds) return message.data.players;
                
                const newAlive = message.data.players.map(p => p.is_alive).join(',');
                const oldAlive = prev.map(p => p.is_alive).join(',');
                if (newAlive !== oldAlive) return message.data.players;
                
                return prev;
            })
        }
      } else if (message.type === 'personal_game_over') {
        setSpectatorMsg(message.data.message)
      }
    }
    
    socket.onclose = () => {
      setWs(null)
      setAppState('name_input')
      setServerStatus('lobby')
      setSpectatorMsg('Disconnected from server.')
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [ws])

  return (
    <>
      {appState === 'name_input' && (
        <div className="overlay">
          <h1>Sumo Circles</h1>
          <p>Grow larger and push enemies out of the Ring of Fire!</p>
          <form onSubmit={connect} className="name-form">
            <input 
              type="text" 
              placeholder="Enter your name" 
              value={name} 
              onChange={e => setName(e.target.value)} 
              className="name-input"
              maxLength={15}
              required
            />
            <button className="btn" type="submit">Join Game</button>
          </form>
          {spectatorMsg && <p style={{color: '#ff0055', marginTop: '10px'}}>{spectatorMsg}</p>}
        </div>
      )}
      
      {appState === 'connecting' && (
        <div className="overlay">
          <h2>Connecting...</h2>
        </div>
      )}
      
      {appState === 'connected' && serverStatus === 'lobby' && (
        <div className="overlay lobby-layout">
          <div className="lobby-content">
            <div className="lobby-header">
              <h1>Sumo Circles</h1>
              <p style={{fontSize: '12px', color: '#888'}}>My ID: {playerId} | Admin: {adminId}</p>
            </div>
            
            <div className="lobby-main">
              {/* Left Rules */}
              <div className="side-section left-rules">
                <h2>The Basics</h2>
                <div className="rules-container">
                  <div className="rule-item rule-anim-1">
                    <span className="rule-icon">🕹️</span>
                    <div>
                      <strong>Move</strong>
                      <p>Use <kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> or arrows to navigate.</p>
                    </div>
                  </div>
                  <div className="rule-item rule-anim-2">
                    <span className="rule-icon">⚪</span>
                    <div>
                      <strong>Grow</strong>
                      <p>Collect white pellets to increase your mass.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Center Players */}
              <div className="center-section">
                <h2>Players Ready ({playersList.length})</h2>
                <div className="player-grid">
                  {playersList.map(p => (
                    <div key={p.id} className="player-item" style={{color: p.color, borderColor: p.color}}>
                      <span className="player-dot" style={{backgroundColor: p.color}}></span>
                      <span className="player-name">{p.name}</span>
                      {p.id === adminId && <span className="badge admin-badge">Admin</span>} 
                      {p.id === playerId && <span className="badge you-badge">You</span>}
                    </div>
                  ))}
                </div>
                
                <div className="lobby-actions">
                  {adminId === playerId ? (
                    <button className="btn start-btn pulse-anim" onClick={() => ws.send(JSON.stringify({type: 'start_game'}))}>
                      Start Game
                    </button>
                  ) : (
                    <p className="waiting-text waiting-anim">Waiting for admin to start<span>.</span><span>.</span><span>.</span></p>
                  )}
                </div>
              </div>

              {/* Right Rules */}
              <div className="side-section right-rules">
                <h2>Combat</h2>
                <div className="rules-container">
                  <div className="rule-item rule-anim-3">
                    <span className="rule-icon">💥</span>
                    <div>
                      <strong>Push</strong>
                      <p>Ram into others. Larger mass pushes harder!</p>
                    </div>
                  </div>
                  <div className="rule-item rule-anim-4">
                    <span className="rule-icon">🔥</span>
                    <div>
                      <strong>Survive</strong>
                      <p>Stay inside the shrinking Ring of Fire.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {appState === 'connected' && serverStatus === 'gameover' && (
        <div className="overlay">
          <h1>Game Over</h1>
          <h2 style={{color: '#fff', marginBottom: '20px'}}>
            {playersList.filter(p => p.is_alive).length === 1 
              ? `${playersList.find(p => p.is_alive).name} Wins!` 
              : "Draw!"}
          </h2>
          {adminId === playerId ? (
            <button className="btn" onClick={() => ws.send(JSON.stringify({type: 'play_again'}))}>
              Play Again
            </button>
          ) : (
            <p>Waiting for admin to restart the game...</p>
          )}
        </div>
      )}
      
      {appState === 'connected' && (
        <>
          <GameCanvas 
            ws={ws} 
            playerId={playerId} 
            serverStateRef={serverStateRef} 
          />
          {serverStatus === 'playing' && spectatorMsg && (
            <div className="spectator-toast">
              {spectatorMsg}
            </div>
          )}
        </>
      )}
    </>
  )
}

export default App
