import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import os

class Planet:
    AU = 149.6e6 * 1000  # Astronomical unit in meters
    G = 6.67428e-11  # Gravitational constant
    SCALE = 2000 / AU  # Scale for rendering
    TIMESTEP = 3000   # Time step 

    def __init__(self, x, y, z, radius, texture_file, mass, x_vel=0, y_vel=0, z_vel=0):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.texture_file = texture_file
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = x_vel
        self.y_vel = y_vel
        self.z_vel = z_vel

        self.texture_id = self.load_texture(texture_file)

    def load_texture(self, filename):
        image = Image.open(filename)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(image.convert("RGBA"), np.uint8)
        width, height = image.size

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        return texture_id

    def draw(self):
        glPushMatrix()
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glTranslatef(self.x * self.SCALE, self.y * self.SCALE, self.z * self.SCALE)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, self.radius, 50, 50)
        gluDeleteQuadric(quadric)

        glDisable(GL_BLEND)
        glPopMatrix()

    def attraction(self, other):
        other_x, other_y, other_z = other.x, other.y, other.z
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance_z = other_z - self.z
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2 + distance_z ** 2)

        if distance == 0:
            return 0, 0, 0

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        phi = math.acos(distance_z / distance)
        force_x = math.sin(phi) * math.cos(theta) * force
        force_y = math.sin(phi) * math.sin(theta) * force
        force_z = math.cos(phi) * force
        return force_x, force_y, force_z

    def update_position(self, planets):
        total_fx = total_fy = total_fz = 0
        for other_planet in planets:
            if self == other_planet:
                continue

            fx, fy, fz = self.attraction(other_planet)
            total_fx += fx
            total_fy += fy
            total_fz += fz

        sun_force_x, sun_force_y, sun_force_z = self.attraction(planets[0])
        total_fx += sun_force_x
        total_fy += sun_force_y
        total_fz += sun_force_z

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP
        self.z_vel += total_fz / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.z += self.z_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y, self.z))

def calculate_initial_velocities(distance):
    G = 6.67430e-11
    M = 1.989e30
    v = math.sqrt(G * M / distance)
    vx = 0
    vz = v
    return vx, vz

def create_planet(x, y, z, radius, texture_file, mass, planets=None, x_vel=0, y_vel=0, z_vel=0):
    if planets is None:
        planets = []

    new_planet = Planet(x, y, z, radius, texture_file, mass, x_vel, y_vel, z_vel)
    planets.append(new_planet)
    return new_planet

def open_tkinter_window(planets):
    def create_new_planet():
        x = float(x_entry.get()) * Planet.AU
        y = float(y_entry.get()) * Planet.AU
        z = float(z_entry.get()) * Planet.AU
        radius = float(radius_entry.get())
        mass = float(mass_entry.get())
        texture_file = texture_entry.get()
        planet_distance = math.sqrt(x ** 2 + y ** 2 + z ** 2)
        planet_vx, planet_vz = calculate_initial_velocities(planet_distance)
        create_planet(x, y, z, radius, texture_file, mass, planets, planet_vx, 0, planet_vz)
        root.destroy()

    root = tk.Tk()
    root.title("New Planet Input")

    tk.Label(root, text="X (AU):").grid(row=0, column=0)
    x_entry = tk.Entry(root)
    x_entry.grid(row=0, column=1)

    tk.Label(root, text="Y (AU):").grid(row=1, column=0)
    y_entry = tk.Entry(root)
    y_entry.grid(row=1, column=1)

    tk.Label(root, text="Z (AU):").grid(row=2, column=0)
    z_entry = tk.Entry(root)
    z_entry.grid(row=2, column=1)

    tk.Label(root, text="Radius:").grid(row=3, column=0)
    radius_entry = tk.Entry(root)
    radius_entry.grid(row=3, column=1)

    tk.Label(root, text="Mass (kg):").grid(row=4, column=0)
    mass_entry = tk.Entry(root)
    mass_entry.grid(row=4, column=1)

    tk.Label(root, text="Texture File:").grid(row=5, column=0)
    texture_entry = tk.Entry(root)
    texture_entry.grid(row=5, column=1)

    def browse_texture_file():
        filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Texture File", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
        if filename:
            texture_entry.delete(0, tk.END)
            texture_entry.insert(0, filename)

    browse_button = tk.Button(root, text="Browse", command=browse_texture_file)
    browse_button.grid(row=5, column=2)

    create_button = tk.Button(root, text="Create", command=create_new_planet)
    create_button.grid(row=6, columnspan=2)

    root.mainloop()

def main():
    if not glfw.init():
        return

    window = glfw.create_window(1920, 1080, "Planet Simulation", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1920 / 1080, 0.1, 1000000000000000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glTranslatef(0.0, 0.0, -1000.0)
    glRotatef(30, 1, 0, 0)

    sun = Planet(0, 0, 0, 100, "images/sun.jpg", 1.98892 * 10 ** 30)
    sun.sun = True

    planets = [sun]

    planet_data = [
        ("Mercury", 0.39, 12.4, "images/mercury.jpeg", 3.30e23),
        ("Venus", 0.72, 26.0, "images/venus.jpg", 4.87e24),
        ("Earth", 1.0, 26.4, "images/earth.jpg", 5.97e24),
        ("Mars", 1.52, 28.4, "images/mars.jpeg", 6.42e23),
        ("Jupiter", 5.2, 70.0, "images/jupiter.jpeg", 1.90e27),
        ("Saturn", 9.58, 62.0, "images/saturn.jpeg", 5.68e26),
        ("Uranus", 19.22, 25.0, "images/uranus.jpeg", 8.68e25),
        ("Neptune", 30.05, 24.0, "images/neptune.jpeg", 1.02e26),
    ]

    for name, distance_au, radius, texture, mass in planet_data:
        distance_m = distance_au * Planet.AU
        x, y, z = distance_m, 0, 0
        vx, vz = calculate_initial_velocities(distance_m)
        create_planet(x, y, z, radius, texture, mass, planets, vx, 0, vz)

    while not glfw.window_should_close(window):
        for planet in planets:
            planet.update_position(planets)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for planet in planets:
            planet.draw()

        glfw.swap_buffers(window)
        glfw.poll_events()

        # Check for 'C' key press to create a new planet
        if glfw.get_key(window, glfw.KEY_C) == glfw.PRESS:
            open_tkinter_window(planets)

    glfw.terminate()

if __name__ == "__main__":
    main()