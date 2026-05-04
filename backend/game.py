import math
import random
import uuid

class Player:
    def __init__(self, id: str, arena_radius: float, name: str):
        self.id = id
        self.name = name
        self.is_alive = True
        # Random initial position within current arena
        angle = random.uniform(0, math.pi * 2)
        spawn_radius = max(0.0, arena_radius - 25.0)
        r = math.sqrt(random.uniform(0, 1)) * spawn_radius
        self.x = math.cos(angle) * r
        self.y = math.sin(angle) * r
        self.radius = 20.0
        self.mass = 10.0
        # Random neon color
        colors = ["#ff0055", "#00ffcc", "#ffcc00", "#cc00ff", "#00ccff", "#ff3300", "#33ff00"]
        self.color = random.choice(colors)
        
        # Target position from user input
        self.target_x = self.x
        self.target_y = self.y
        
        # Velocity for knockback
        self.vx = 0.0
        self.vy = 0.0

class Pellet:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.x = random.uniform(-900, 900)
        self.y = random.uniform(-900, 900)
        self.radius = 5.0
        self.color = "#ffffff"

class GameState:
    def __init__(self):
        self.players: dict[str, Player] = {}
        self.pellets: list[Pellet] = []
        self.arenaRadius = 1000.0
        self.arenaShrinkRate = 10.0 # pixels per second
        self.max_pellets = 100
        self.status = 'lobby'
        self.admin_id = None
        
        for _ in range(self.max_pellets):
            self.pellets.append(Pellet())

    def add_player(self, player_id: str, name: str):
        # Reset arena if no active players
        if len(self.players) == 0:
            self.arenaRadius = 1000.0
            self.status = 'lobby'
        self.players[player_id] = Player(player_id, self.arenaRadius, name)
        
        if self.admin_id is None:
            self.admin_id = player_id
            
    def remove_player(self, player_id: str):
        if player_id in self.players:
            del self.players[player_id]
            
        if self.admin_id == player_id:
            if len(self.players) > 0:
                self.admin_id = list(self.players.keys())[0]
            else:
                self.admin_id = None

    def start_game(self):
        if self.status == 'lobby':
            self.status = 'playing'

    def reset_game(self):
        self.status = 'lobby'
        self.arenaRadius = 1000.0
        self.pellets.clear()
        for _ in range(self.max_pellets):
            self.pellets.append(Pellet())
            
        for p in self.players.values():
            p.is_alive = True
            p.radius = 20.0
            p.mass = 10.0
            angle = random.uniform(0, math.pi * 2)
            spawn_radius = max(0.0, self.arenaRadius - 25.0)
            r = math.sqrt(random.uniform(0, 1)) * spawn_radius
            p.x = math.cos(angle) * r
            p.y = math.sin(angle) * r
            p.target_x = p.x
            p.target_y = p.y
            p.vx = 0.0
            p.vy = 0.0

    def set_player_target(self, player_id: str, x: float, y: float):
        if player_id in self.players:
            self.players[player_id].target_x = x
            self.players[player_id].target_y = y

    def get_state(self):
        return {
            "status": self.status,
            "admin_id": self.admin_id,
            "arenaRadius": self.arenaRadius,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "is_alive": p.is_alive,
                    "x": p.x,
                    "y": p.y,
                    "vx": p.vx,
                    "vy": p.vy,
                    "radius": p.radius,
                    "mass": p.mass,
                    "color": p.color
                } for p in self.players.values()
            ],
            "pellets": [
                {
                    "id": p.id,
                    "x": p.x,
                    "y": p.y,
                    "radius": p.radius,
                    "color": p.color
                } for p in self.pellets
            ]
        }

    def tick(self, dt: float):
        if self.status != 'playing':
            return []
            
        # Shrink arena
        self.arenaRadius -= self.arenaShrinkRate * dt
        if self.arenaRadius < 100:
            self.arenaRadius = 100 # Minimum size
            
        # Spawn pellets if needed
        while len(self.pellets) < self.max_pellets:
            # Spawn within arena
            angle = random.uniform(0, math.pi * 2)
            r = math.sqrt(random.uniform(0, 1)) * self.arenaRadius
            pellet = Pellet()
            pellet.x = math.cos(angle) * r
            pellet.y = math.sin(angle) * r
            self.pellets.append(pellet)

        out_of_bounds_players = []

        # Move players toward target
        for p in self.players.values():
            if not p.is_alive:
                continue
                
            # Vector to target
            dx = p.target_x - p.x
            dy = p.target_y - p.y
            dist = math.sqrt(dx**2 + dy**2)
            
            speed = 300.0 * dt # Base speed
            # Reduce speed as mass increases to make big players sluggish
            speed_multiplier = 20.0 / max(20.0, p.radius)
            speed = speed * speed_multiplier
            
            if dist > speed:
                p.x += (dx / dist) * speed
                p.y += (dy / dist) * speed
            else:
                p.x = p.target_x
                p.y = p.target_y

            # Apply velocity from knockbacks
            p.x += p.vx * dt
            p.y += p.vy * dt
            
            # Friction for knockback velocity
            friction = 5.0 * dt
            speed_v = math.sqrt(p.vx**2 + p.vy**2)
            if speed_v > 0:
                drop = speed_v * friction
                new_speed = max(0, speed_v - drop)
                p.vx *= new_speed / speed_v
                p.vy *= new_speed / speed_v
                
            # Check arena bounds
            dist_from_center = math.sqrt(p.x**2 + p.y**2)
            if dist_from_center > self.arenaRadius:
                p.is_alive = False
                out_of_bounds_players.append(p.id)
                
        # Resolve collisions between players
        player_list = [p for p in self.players.values() if p.is_alive]
        for i in range(len(player_list)):
            for j in range(i + 1, len(player_list)):
                p1 = player_list[i]
                p2 = player_list[j]
                
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                dist = math.sqrt(dx**2 + dy**2)
                min_dist = p1.radius + p2.radius
                
                if dist < min_dist and dist > 0:
                    # They are colliding
                    overlap = min_dist - dist
                    
                    # Separate them
                    nx = dx / dist
                    ny = dy / dist
                    
                    # Pushing them apart proportional to inverse mass
                    total_mass = p1.mass + p2.mass
                    p1_ratio = p2.mass / total_mass
                    p2_ratio = p1.mass / total_mass
                    
                    p1.x -= nx * overlap * p1_ratio
                    p1.y -= ny * overlap * p1_ratio
                    p2.x += nx * overlap * p2_ratio
                    p2.y += ny * overlap * p2_ratio
                    
                    # Apply knockback velocity
                    # We want bigger players to bounce smaller ones away
                    base_knockback = 800.0
                    
                    if p1.mass > p2.mass:
                        force = base_knockback * (p1.mass / p2.mass)
                        p2.vx += nx * force
                        p2.vy += ny * force
                    elif p2.mass > p1.mass:
                        force = base_knockback * (p2.mass / p1.mass)
                        p1.vx -= nx * force
                        p1.vy -= ny * force
                    else:
                        p1.vx -= nx * base_knockback * 0.5
                        p1.vy -= ny * base_knockback * 0.5
                        p2.vx += nx * base_knockback * 0.5
                        p2.vy += ny * base_knockback * 0.5
                        
        # Check pellet consumption
        for p in self.players.values():
            if not p.is_alive:
                continue
                
            eaten_pellets = []
            for pellet in self.pellets:
                dx = pellet.x - p.x
                dy = pellet.y - p.y
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist < p.radius + pellet.radius:
                    eaten_pellets.append(pellet)
                    
            for pellet in eaten_pellets:
                if pellet in self.pellets:
                    self.pellets.remove(pellet)
                # Increase mass and radius
                p.mass += 1.0
                p.radius = 20.0 + math.sqrt(p.mass - 10.0) * 3.0
                
        # Check game over condition
        alive_count = sum(1 for p in self.players.values() if p.is_alive)
        if alive_count == 0 or (len(self.players) > 1 and alive_count <= 1):
            self.status = 'gameover'
                
        return out_of_bounds_players
