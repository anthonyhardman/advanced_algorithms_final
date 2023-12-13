import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from delauney import Delauney, VoronoiEdge
from quad_edge import QuadEdge, Site
from shader import Shader
import numpy as np
import glm


class VDV:
    def __init__(self) -> None:
        self.delauney_sites = []
        self.delauney_sites_vao = []
        self.voronoi_circumcenters = []
        self.voronoi_edges = []
        self.delauney_edges = []
        self.__show_delauney_edges = True

    def display(self):
        for site in self.delauney_sites_vao:
            glBindVertexArray(site)
            glDrawArrays(GL_POINTS, 0, 1)

        for circumcenter in self.voronoi_circumcenters:
            glBindVertexArray(circumcenter)
            glDrawArrays(GL_POINTS, 0, 1)

        if self.__show_delauney_edges:
            for edge in self.delauney_edges:
                glBindVertexArray(edge)
                glDrawArrays(GL_LINES, 0, 2)

        for edge in self.voronoi_edges:
            glBindVertexArray(edge)
            glDrawArrays(GL_LINES, 0, 2)

    def create_edge_vao(seld, data: np.ndarray):
        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

        glBindVertexArray(vao)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(ctypes.c_float), None
        )

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,5 * sizeof(ctypes.c_float),ctypes.c_void_p(2 * sizeof(ctypes.c_float)))

        return vao
    
    def create_site_vao(self, data: np.ndarray):
        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

        glBindVertexArray(vao)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(ctypes.c_float), None)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(ctypes.c_float), ctypes.c_void_p(2 * sizeof(ctypes.c_float)))

        return vao
    
    def add_delauney_edge(self, e: QuadEdge):
        data = np.array(
            [
                e.origin.x,
                e.origin.y,
                0.0,
                0.0,
                1.0,
                e.dest.x,
                e.dest.y,
                0.0,
                0.0,
                1.0,
            ], dtype=np.float32)
        
        vao = self.create_edge_vao(data)
        self.delauney_edges.append(vao)

    def add_voronoi_edge(self, e: VoronoiEdge):
        data = np.array(
            [
                e.origin.x,
                e.origin.y,
                1.0,
                0.0,
                0.0,
                e.dest.x,
                e.dest.y,
                1.0,
                0.0,
                0.0,
            ], dtype=np.float32)
        
        vao = self.create_edge_vao(data)
        self.voronoi_edges.append(vao)

    def add_delauney_site(self, site: Site):
        data = np.array(
            [
                site.x,
                site.y,
                1.0,
                0.5,
                0.0,
            ], dtype=np.float32)
        
        vao = self.create_site_vao(data)
        self.delauney_sites_vao.append(vao)

    def add_voronoi_circumcenter(self, site: Site):
        data = np.array(
            [
                site.x,
                site.y,
                0.0,
                0.0,
                0.0,
            ], dtype=np.float32)
        
        vao = self.create_site_vao(data)
        self.voronoi_circumcenters.append(vao)

    def set_mouse_button_callback(self, window):
        
        def mouse_button_callback(window, button, action, mods):
            if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
                x, y = glfw.get_cursor_pos(window)
                x = (x / 720) * 10000
                y = 10000 - ((y / 720) * 10000)
                self.delauney_sites.append(Site(x, y))
                self.add_delauney_site(self.delauney_sites[-1])

                if len(self.delauney_sites) > 1:
                    d = Delauney(self.delauney_sites)
                    self.delauney_edges.clear()
                    for e in [edge for edge in d.edges.values() if edge.origin and edge.dest]:
                        self.add_delauney_edge(e)

                    self.voronoi_circumcenters.clear()
                    self.voronoi_edges.clear()
                    circ, v_edges = d.voronoi()
                    for e in v_edges:
                        self.add_voronoi_edge(e)

                    for site in circ:
                        self.add_voronoi_circumcenter(site)

        glfw.set_mouse_button_callback(window, mouse_button_callback)

    def set_button_callback(self, window):
        def key_callback(window, key, scancode, action, mods):
            if key == glfw.KEY_D and action == glfw.PRESS:
                self.__show_delauney_edges = not self.__show_delauney_edges

        glfw.set_key_callback(window, key_callback)
