from manim import *

class MainScene(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        t = Text("Hello Manim", color=WHITE)
        self.play(Write(t))
        self.wait(1)