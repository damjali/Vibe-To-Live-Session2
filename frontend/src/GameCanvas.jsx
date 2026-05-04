import { useRef, useEffect } from 'react';

const GameCanvas = ({ ws, playerId, serverStateRef }) => {
  const canvasRef = useRef(null);
  
  // Track WASD keys
  const keysRef = useRef({ w: false, a: false, s: false, d: false });

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    const handleKeyDown = (e) => {
      const key = e.key.toLowerCase();
      if (['w', 'a', 's', 'd'].includes(key)) {
        keysRef.current[key] = true;
      }
    };

    const handleKeyUp = (e) => {
      const key = e.key.toLowerCase();
      if (['w', 'a', 's', 'd'].includes(key)) {
        keysRef.current[key] = false;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    // Resize canvas to fill window
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    let animationFrameId;

    const render = () => {
      const state = serverStateRef.current;
      const width = canvas.width;
      const height = canvas.height;
      
      // Find my player
      const myPlayer = state.players.find(p => p.id === playerId);
      
      // Calculate camera center. If my player exists, center on them, otherwise center on 0,0
      const camX = myPlayer ? myPlayer.x : 0;
      const camY = myPlayer ? myPlayer.y : 0;
      
      // Send input based on WASD keys
      if (ws && ws.readyState === WebSocket.OPEN && myPlayer) {
        let dx = 0;
        let dy = 0;
        if (keysRef.current.w) dy -= 1;
        if (keysRef.current.s) dy += 1;
        if (keysRef.current.a) dx -= 1;
        if (keysRef.current.d) dx += 1;
        
        let targetWorldX = myPlayer.x;
        let targetWorldY = myPlayer.y;
        
        if (dx !== 0 || dy !== 0) {
          const length = Math.sqrt(dx*dx + dy*dy);
          dx /= length;
          dy /= length;
          targetWorldX += dx * 100;
          targetWorldY += dy * 100;
        }
        
        ws.send(JSON.stringify({
          type: 'input',
          data: { x: targetWorldX, y: targetWorldY }
        }));
      }

      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      ctx.save();
      // Translate to camera position
      ctx.translate(width / 2 - camX, height / 2 - camY);

      // Draw dark grid background
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.lineWidth = 1;
      const gridSize = 50;
      const viewRadius = Math.max(width, height);
      const startX = Math.floor((camX - viewRadius) / gridSize) * gridSize;
      const endX = Math.floor((camX + viewRadius) / gridSize) * gridSize;
      const startY = Math.floor((camY - viewRadius) / gridSize) * gridSize;
      const endY = Math.floor((camY + viewRadius) / gridSize) * gridSize;

      ctx.beginPath();
      for (let x = startX; x <= endX; x += gridSize) {
        ctx.moveTo(x, startY);
        ctx.lineTo(x, endY);
      }
      for (let y = startY; y <= endY; y += gridSize) {
        ctx.moveTo(startX, y);
        ctx.lineTo(endX, y);
      }
      ctx.stroke();

      // Draw Arena (Ring of Fire)
      ctx.beginPath();
      ctx.arc(0, 0, state.arenaRadius, 0, Math.PI * 2);
      ctx.strokeStyle = '#ff3300';
      ctx.lineWidth = 5;
      ctx.stroke();
      
      // Optional: Add glow to ring
      ctx.shadowBlur = 20;
      ctx.shadowColor = '#ff3300';
      ctx.stroke();
      ctx.shadowBlur = 0; // reset

      // Draw Pellets
      for (const pellet of state.pellets) {
        ctx.beginPath();
        ctx.arc(pellet.x, pellet.y, pellet.radius, 0, Math.PI * 2);
        ctx.fillStyle = pellet.color;
        ctx.fill();
        // subtle glow
        ctx.shadowBlur = 10;
        ctx.shadowColor = pellet.color;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // Draw Players
      // Draw other players first, then my player on top
      const others = state.players.filter(p => p.id !== playerId);
      const renderPlayer = (player) => {
        ctx.beginPath();
        ctx.arc(player.x, player.y, player.radius, 0, Math.PI * 2);
        ctx.fillStyle = player.color;
        ctx.fill();
        
        // Neon border
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Glow
        ctx.shadowBlur = 15;
        ctx.shadowColor = player.color;
        ctx.fill();
        ctx.shadowBlur = 0;
        
        // Draw facial expression
        ctx.fillStyle = '#111111'; // dark color for face
        
        // Calculate speed from knockback to determine if pushed
        const speed = Math.sqrt((player.vx || 0)**2 + (player.vy || 0)**2);
        const isAngry = speed > 50;

        // Eyes
        const eyeOffset = player.radius * 0.3;
        const eyeSize = Math.max(2, player.radius * 0.15);
        ctx.beginPath();
        ctx.arc(player.x - eyeOffset, player.y - eyeOffset, eyeSize, 0, Math.PI * 2);
        ctx.arc(player.x + eyeOffset, player.y - eyeOffset, eyeSize, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = '#111111';
        ctx.lineWidth = Math.max(1, player.radius * 0.08);

        if (isAngry) {
          // Angry eyebrows
          ctx.beginPath();
          ctx.moveTo(player.x - eyeOffset * 1.5, player.y - eyeOffset * 1.8);
          ctx.lineTo(player.x - eyeOffset * 0.2, player.y - eyeOffset * 0.8);
          ctx.moveTo(player.x + eyeOffset * 1.5, player.y - eyeOffset * 1.8);
          ctx.lineTo(player.x + eyeOffset * 0.2, player.y - eyeOffset * 0.8);
          ctx.stroke();

          // Angry mouth (frown)
          ctx.beginPath();
          ctx.arc(player.x, player.y + eyeOffset * 0.8, player.radius * 0.3, 1.1 * Math.PI, 1.9 * Math.PI);
          ctx.stroke();
        } else {
          // Mouth (smile)
          ctx.beginPath();
          ctx.arc(player.x, player.y + eyeOffset * 0.2, player.radius * 0.4, 0.1 * Math.PI, 0.9 * Math.PI);
          ctx.stroke();
        }
        
        // Draw player indicator if it's me
        if (player.id === playerId) {
          ctx.beginPath();
          ctx.arc(player.x, player.y, player.radius + 10, 0, Math.PI * 2);
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
          ctx.setLineDash([5, 5]);
          ctx.lineWidth = 1;
          ctx.stroke();
          ctx.setLineDash([]);
        }

        // Draw player name
        ctx.fillStyle = '#ffffff';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
        ctx.shadowBlur = 4;
        ctx.fillText(player.name || "Player", player.x, player.y + player.radius + 15);
        ctx.shadowBlur = 0; // reset
      };

      others.forEach(renderPlayer);
      if (myPlayer) renderPlayer(myPlayer);

      ctx.restore();
      
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, [ws, playerId, serverStateRef]);

  return (
    <canvas 
      ref={canvasRef} 
      style={{ display: 'block' }}
    />
  );
};

export default GameCanvas;
