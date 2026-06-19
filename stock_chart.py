from manim import *
import numpy as np

class StockChart(Scene):
    def construct(self):
        # Sample stock data: (Time/Index, Price)
        stock_data = [
            [0, 100.00], [1, 102.50], [2, 101.20], [3, 105.00], 
            [4, 104.30], [5, 108.75], [6, 112.10], [7, 110.00]
        ]

        # 1. FIXED: Create a coordinate system that ONLY uses standard Text mobjects
        axes = Axes(
            x_range=[0, 7, 1],
            y_range=[90, 120, 5],
            axis_config={
                "color": BLUE,
            },
            # This completely blocks Manim from generating MathTex for the numbers
            tips=False
        )
        
        # Manually add pure-text labels to the axes to ensure zero LaTeX is called
        axes.add_coordinates(
            dict(zip(range(0, 8), [Text(str(x), font_size=16) for x in range(0, 8)])),
            dict(zip(range(90, 125, 5), [Text(str(y), font_size=16) for y in range(90, 125, 5)]))
        )
        
        # 2. Convert data points to scene coordinates
        points = [axes.coords_to_point(x, y) for x, y in stock_data]
        
        # 3. Create the stock line
        stock_line = VMobject(color=GREEN)
        stock_line.set_points_as_corners(points)

        # 4. Set up the tracking Dot
        dot = Dot(color=YELLOW)
        dot.move_to(points[0])

        # 5. Set up the tracking ValueTracker (anchored to the price)
        price_tracker = ValueTracker(stock_data[0][1])

        # 6. FIXED: Pure text label with f-string formatting
        price_label = always_redraw(
            lambda: Text(
                f"${price_tracker.get_value():.2f}", 
                font_size=20
            ).next_to(dot, UP, buff=0.2)
        )

        # 7. Animation Sequence
        self.play(Create(axes))
        self.play(Create(stock_line), run_time=2)
        self.add(dot, price_label)

        # Move the dot along the path while updating the text label smoothly
        for i in range(1, len(stock_data)):
            target_point = points[i]
            target_price = stock_data[i][1]
            
            self.play(
                dot.animate.move_to(target_point),
                price_tracker.animate.set_value(target_price),
                rate_func=linear,
                run_time=0.8
            )
            
        self.wait(2)