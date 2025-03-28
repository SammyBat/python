# ========================================
#  Cosmic Drift - Wispy Nebula Edition
# ========================================

# --- Core Imports ---
from ursina import *
# --- Standard Prefabs ---
from ursina.prefabs.first_person_controller import FirstPersonController
# --- Shaders ---
from ursina.shaders import unlit_shader
# --- Standard Python Libraries ---
import random
import math
import time

# --- Configuration ---
WINDOW_TITLE = "Cosmic Drift - Wispy Nebula Edition"
FULLSCREEN_MODE = False
STAR_COUNT = 1000      # Further reduce stars slightly if performance is hit by layering
NEBULA_GROUP_COUNT = 12 # Number of nebula *groups* (each group has layers)
LAYERS_PER_NEBULA = 3   # Number of overlapping spheres per group
DEEP_SPACE_OBJECT_COUNT = 8
PLAYER_SPEED = 30
MOUSE_SENSITIVITY = Vec2(80, 80)

# --- Helper Functions ---
def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def random_bright_color(min_saturation=0.7, min_value=0.8, alpha=1.0):
    return color.color(random.uniform(0, 360),
                       random.uniform(min_saturation, 1.0),
                       random.uniform(min_value, 1.0),
                       alpha)

# Slightly adjusted psychedelic function for potentially softer nebula colors
def psychedelic_color(t, offset=0, speed=1.0, saturation=0.75, value=0.85, alpha=0.1): # Lower default alpha/sat/val
    hue = (math.sin(t * 0.15 * speed + offset) * 180 + 180 + offset*10) % 360
    sat_variation = math.sin(t * 0.25 * speed + offset + 2) * 0.05 # Reduced variation
    val_variation = math.sin(t * 0.35 * speed + offset + 4) * 0.03 # Reduced variation
    final_saturation = clamp(saturation + sat_variation, 0.5, 0.9) # Lower max saturation
    final_value = clamp(value + val_variation, 0.6, 0.95) # Lower max value
    final_alpha = clamp(alpha, 0, 1)
    return color.color(hue, final_saturation, final_value, final_alpha)


# --- Game Setup ---
app = Ursina(title=WINDOW_TITLE, borderless=False, fullscreen=FULLSCREEN_MODE)

# --- Background ---
window.color = color.black
sky_sphere = Entity(
    model='sphere', scale=3000, shader=unlit_shader,
    color=color.black, double_sided=True, eternal=True, collider=None
)

# --- Player ---
player = FirstPersonController(
    gravity=0, speed=PLAYER_SPEED, mouse_sensitivity=MOUSE_SENSITIVITY,
    position=(0, 0, 0), visible=False, collider=None, enabled=True
)
player.camera_pivot.visible = False
player.cursor.visible = False
player.cursor.enabled = False

# --- Environment Setup ---

# 1. Starfield
stars = []
for i in range(STAR_COUNT):
    # ... (star creation code remains the same) ...
    star_color = random_bright_color(min_saturation=0.4, min_value=0.7)
    star = Entity(
        model='sphere', shader=unlit_shader, color=star_color,
        scale=random.uniform(0.04, 0.15),
        position=(Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)).normalized()
                  * random.uniform(150, 600))
    )
    star.flicker_speed = random.uniform(1.5, 4.5)
    star.flicker_amount = random.uniform(0.15, 0.5)
    star.base_color = star.color
    star.time_offset = random.uniform(0, 15)
    stars.append(star)


# --- !! MODIFIED: Create Layered Nebulae !! ---
nebulae = [] # This list will now store all individual layer entities
nebula_groups = [] # Optional: keep track of logical groups if needed for complex logic

for i in range(NEBULA_GROUP_COUNT):
    group_center_pos = (Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)).normalized()
                       * random.uniform(400, 1000)) # Place group centers
    group_base_rotation = Vec3(random.uniform(0,360), random.uniform(0,360), random.uniform(0,360))
    group_rotation_speed = Vec3(random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6), random.uniform(-0.4, 0.4)) * 0.6 # Slower overall group rotation

    # Store group properties if needed later
    # nebula_groups.append({'position': group_center_pos, 'rotation_speed': group_rotation_speed})

    for j in range(LAYERS_PER_NEBULA):
        start_time = time.time() + i * 0.2 + j * 0.05 # Slightly offset time for layers

        # --- Properties for this specific layer ---
        layer_alpha = random.uniform(0.03, 0.12) # Keep layers very faint
        layer_color_offset = i * 0.6 + j * 0.3 + random.uniform(-0.5, 0.5)
        layer_color_speed = random.uniform(0.04, 0.12) # Slower color shifts often look better
        layer_scale_multiplier = random.uniform(0.7, 1.3) # Vary layer size within the group
        layer_pos_offset = Vec3(random.uniform(-20, 20), random.uniform(-20, 20), random.uniform(-20, 20)) # Slight position offset
        layer_texture_choice = random.choice(['noise', 'noise', 'radial_gradient']) # Use noise mostly, sometimes gradient

        initial_color = psychedelic_color(start_time, offset=layer_color_offset, speed=layer_color_speed, alpha=layer_alpha)

        nebula_layer = Entity(
            model='sphere',
            # --- Use chosen texture with LARGE scale ---
            texture=layer_texture_choice,
            texture_scale = Vec2(random.uniform(3, 8), random.uniform(3, 8)), # Much larger scale to stretch pattern

            shader=unlit_shader,
            color=initial_color,
            # Base scale for the group, modified per layer
            scale=random.uniform(200, 550) * layer_scale_multiplier,
            # Position relative to group center
            position=group_center_pos + layer_pos_offset,
            # Start with group rotation + slight variation? Or just group rotation.
            rotation=group_base_rotation + Vec3(random.uniform(-10,10),random.uniform(-10,10),random.uniform(-10,10)),
            double_sided=True
        )

        # --- Animate layers mostly as a group ---
        # Store group properties on each layer for easier update loop
        nebula_layer.group_rotation_speed = group_rotation_speed
        nebula_layer.group_center_pos = group_center_pos # Store center to rotate around

        # Store individual properties needed for update
        nebula_layer.color_offset = layer_color_offset
        nebula_layer.color_speed = layer_color_speed
        nebula_layer.base_alpha = layer_alpha # Store alpha if needed

        # Optional pulsing (can be subtle)
        nebula_layer.base_scale = nebula_layer.scale
        nebula_layer.pulse_speed = random.uniform(0.08, 0.3) # Slower pulse
        nebula_layer.pulse_amount = random.uniform(0.02, 0.06) * nebula_layer.base_scale # Smaller pulse amount

        nebulae.append(nebula_layer) # Add the layer to the main list


# 3. Deep Space Objects
deep_space_objects = []
for i in range(DEEP_SPACE_OBJECT_COUNT):
    # ... (dso creation code remains the same) ...
    dso_color = color.color(random.uniform(200, 300), random.uniform(0.5, 0.8),
                            random.uniform(0.1, 0.3), random.uniform(0.02, 0.08))
    dso = Entity(
        model=random.choice(['sphere', 'quad']), shader=unlit_shader, color=dso_color,
        scale=random.uniform(900, 1800),
        position=(Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)).normalized()
                  * random.uniform(1100, 1900)),
        rotation=(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)),
        double_sided=True, eternal=True
    )
    dso.rotation_speed = Vec3(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.05, 0.05))
    deep_space_objects.append(dso)


# --- Update Loop ---
def update():
    current_time = time.time()

    # Update Stars
    for star in stars:
        # ... (star update code remains the same) ...
        flicker_mod = (math.sin(current_time * star.flicker_speed + star.time_offset) * 0.5 + 0.5)
        brightness_factor = 1.0 - star.flicker_amount + flicker_mod * star.flicker_amount
        star.color = color.color(star.base_color.h, star.base_color.s,
                                 clamp(star.base_color.v * brightness_factor, 0.05, 1.0),
                                 star.base_color.a)


    # --- !! Update Nebula Layers !! ---
    for nebula_layer in nebulae:
        # --- Rotate layers slowly as a group around their center ---
        # This requires rotating the position vector relative to the center, then adding the center back
        # Apply the group rotation speed (can be complex, let's simplify for now)
        # Simple approach: Just rotate the entity itself based on group speed
        nebula_layer.rotation += nebula_layer.group_rotation_speed * time.dt

        # Calculate new color
        new_color = psychedelic_color(current_time,
                                      offset=nebula_layer.color_offset,
                                      speed=nebula_layer.color_speed,
                                      alpha=nebula_layer.base_alpha) # Use stored alpha
        nebula_layer.color = new_color

        # Optional pulsing
        pulse = math.sin(current_time * nebula_layer.pulse_speed + nebula_layer.color_offset) * nebula_layer.pulse_amount
        nebula_layer.scale = max(nebula_layer.base_scale * 0.1, nebula_layer.base_scale + pulse)


    # Update Deep Space Objects
    for dso in deep_space_objects:
         dso.rotation += dso.rotation_speed * time.dt

    # Camera Sway
    sway_intensity = 0.18
    sway_speed = 0.08
    # ... (camera sway code remains the same) ...
    camera.rotation_x += math.sin(current_time * sway_speed * 1.1 + 1) * sway_intensity * time.dt
    camera.rotation_y += math.cos(current_time * sway_speed * 0.9 + 2) * sway_intensity * time.dt

    # Player Controls
    # ... (player control code remains the same) ...
    move_direction = Vec3(0,0,0)
    if held_keys['a']: move_direction -= camera.right
    if held_keys['d']: move_direction += camera.right
    if held_keys['space']: move_direction += Vec3(0,1,0)
    if held_keys['control'] or held_keys['c']: move_direction -= Vec3(0,1,0)
    if move_direction.length() > 0: player.position += move_direction.normalized() * player.speed * time.dt
    roll_speed = 110
    if held_keys['q']: player.rotation_z += roll_speed * time.dt
    if held_keys['e']: player.rotation_z -= roll_speed * time.dt
    target_speed = PLAYER_SPEED * 3.5 if held_keys['shift'] else PLAYER_SPEED
    player.speed = lerp(player.speed, target_speed, time.dt * 6)
    if held_keys['escape']: application.quit()


# --- Function to Print Controls ---
def print_instructions():
    # ... (print instructions code remains the same) ...
    print("\n" * 2)
    print("=" * 40)
    print("    Cosmic Drift - Wispy Nebula Edition") # Updated Title
    print("=" * 40)
    print("Controls:")
    print("  W / S    : Move Forward / Backward")
    print("  A / D    : Strafe Left / Right")
    print("  Space    : Move Up")
    print("  Ctrl / C : Move Down")
    print("  Q / E    : Roll Left / Right")
    print("  Shift    : Boost Speed")
    print("  Mouse    : Look Around")
    print("  Escape   : Quit")
    print("=" * 40)
    print("\n")

# --- Main Execution Block ---
if __name__ == '__main__':
    print_instructions()
    app.run()