from manim import *

class HelloWorld(Scene):
    def construct(self):
        # Create a text object
        text = Text("Hello, Manim!", font_size=48)
        
        # Animate the text writing itself onto the screen
        self.play(Write(text))
        self.wait(1)