from pprint import pprint
import random
import time
from typing import Dict, Tuple
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from delauney import Delauney, VoronoiEdge
from quad_edge import QuadEdge, Site
from shader import Shader
import numpy as np
import glm

from voronoi_and_delauney_visualization import VDV


glfw.init()
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.SAMPLES, 16)

window = glfw.create_window(720, 720, "Visualization", None, None)
glfw.make_context_current(window)


vertex_src = """
# version 330
layout(location = 0) in vec2 aPosition;
layout(location = 1) in vec3 aColor;

out vec3 vColor;
uniform mat4 projection;

void main()
{
    gl_Position = projection * vec4(aPosition, 0.0, 1.0);
    vColor = aColor;
}
"""

fragment_src = """
# version 330
in vec3 vColor;
out vec4 outColor;

void main()
{
    outColor = vec4(vColor, 1.0);
}
"""

shader = Shader(vertex_src, fragment_src)



glClearColor(0.35, 0.45, 0.50, 1.00)
glPointSize(5.0)

left = 0  # Maps to -1 in the original space
right = 10000  # Maps to 1 in the original space
bottom = 0  # Maps to -1 in the original space
top = 10000  # Maps to 1 in the original space

zNear = -1.0  # Example value, adjust as needed
zFar = 1.0  # Example value, adjust as needed

projection = glm.ortho(left, right, bottom, top, zNear, zFar)

vdv = VDV()
vdv.set_mouse_button_callback(window)
vdv.set_button_callback(window)

while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    shader.bind()
    shader.set_mat4("projection", glm.value_ptr(projection))

    vdv.display()

    glfw.swap_buffers(window)
