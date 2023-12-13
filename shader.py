from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class Shader:
    def __init__(self, vertex_src, fragment_src) -> None:
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, [vertex_src])
        glCompileShader(vertex_shader)
        self.check_shader(GL_VERTEX_SHADER, vertex_shader)

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, [fragment_src])
        glCompileShader(fragment_shader)
        self.check_shader(GL_FRAGMENT_SHADER, fragment_shader)

        self.__id = glCreateProgram()

        glAttachShader(self.__id, vertex_shader)
        glAttachShader(self.__id, fragment_shader)
        glLinkProgram(self.__id)
        self.check_program(self.__id)

    def bind(self):
        glUseProgram(self.__id)

    def check_shader(self, shader_type, shader):
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            print(error)
            raise RuntimeError(f"{self.get_shader_type_string()} shader compilation error")
        
    def check_program(self, program):
        if not glGetProgramiv(program, GL_LINK_STATUS):
            print(glGetProgramInfoLog(program))
            raise RuntimeError('Linking error')
        
    def get_shader_type_string(self, shader_type):
        if shader_type == GL_VERTEX_SHADER:
            return "Vertex"
        elif shader_type == GL_FRAGMENT_SHADER:
            return "Fragment"
        else:
            return "Unknown"
        
    def set_mat4(self, name, mat):
        glUniformMatrix4fv(glGetUniformLocation(self.__id, name), 1, GL_FALSE, mat)