from manim import *
import random

class HelloWorld(Scene):
    def construct(self):
        # Create a text object
        text = Text("Hello, Manim!", font_size=48)
        
        # Animate the text writing itself onto the screen
        self.play(Write(text))
        self.wait(1)


class NBADraftMatrix(Scene):
    def construct(self):
        # --- Configuration ---
        start_year = 2010  # Adjust this to whatever starting year you want
        rows = 15          # 15 years of draft data
        picks_per_round = 30 
        
        # Sizing and spacing
        square_size = 0.14 
        square_buff = 0.03   # Gap between adjacent squares
        round_buff = 0.25    # Extra gap separating Round 1 and Round 2
        label_buff = 0.40    # Gap between the Year text and the first pick
        row_buff = 0.12      # Vertical gap between draft years
        
        sample_colors = [BLUE, PURPLE, RED, TEAL, GREEN, GOLD, ORANGE, MAROON]

        # Master group to hold all 15 rows
        matrix = VGroup()
        
        # 2D list to store individual square references for future animations
        # Access a square using: self.grid[row_index][column_index] (0 to 59)
        self.grid = []

        # --- 1. Building the Layout ---
        for i in range(rows):
            current_year = start_year + i
            
            # Sub-groups for this specific year
            row_master_group = VGroup()
            round1_group = VGroup()
            round2_group = VGroup()
            grid_row = []
            
            # Create Year Label
            year_label = Text(str(current_year), font_size=16, weight=BOLD, color=GRAY_A)
            
            # Build Round 1 (Picks 1-30)
            for c in range(picks_per_round):
                sq = Square(side_length=square_size)
                random_color = random.choice(sample_colors)
                random_color = WHITE
                sq.set_fill(random_color, opacity=0.7)
                sq.set_stroke(random_color, width=1)
                
                round1_group.add(sq)
                grid_row.append(sq)
                
            # Build Round 2 (Picks 31-60)
            for c in range(picks_per_round):
                sq = Square(side_length=square_size)
                random_color = random.choice(sample_colors)
                random_color = GREY
                sq.set_fill(random_color, opacity=0.7)
                sq.set_stroke(random_color, width=1)
                
                round2_group.add(sq)
                grid_row.append(sq)

            # Arrange the squares within their respective rounds
            round1_group.arrange(RIGHT, buff=square_buff)
            round2_group.arrange(RIGHT, buff=square_buff)
            
            # Assemble the complete row from left to right:
            # [Year Label] -> [Round 1] -> [Gap] -> [Round 2]
            row_master_group.add(year_label)
            row_master_group.add(round1_group)
            row_master_group.add(round2_group)
            
            # Handle the horizontal positioning layout
            round1_group.next_to(year_label, RIGHT, buff=label_buff)
            round2_group.next_to(round1_group, RIGHT, buff=round_buff)
            
            # Align the center-y of the text cleanly with the center-y of the shapes
            year_label.align_to(round1_group, UP)
            
            matrix.add(row_master_group)
            self.grid.append(grid_row)

        # Arrange all 10 rows vertically
        matrix.arrange(DOWN, buff=row_buff)
        
        # Center everything on the screen
        matrix.move_to(ORIGIN)

        # --- 2. Intro Animation (Row by Row) ---
        for r in range(rows):
            # Target the components of the current row group
            current_year_text = matrix[r][0]
            current_round1 = matrix[r][1]
            current_round2 = matrix[r][2]
            
            self.play(
                # Fade the text in slightly faster than the squares sweep
                FadeIn(current_year_text, shift=RIGHT, run_time=0.25),
                LaggedStart(
                    *[FadeIn(sq, scale=0.3) for sq in current_round1], 
                    *[FadeIn(sq, scale=0.3) for sq in current_round2],
                    lag_ratio=0.012
                ),
                run_time=0.2
            )
        
        self.wait(3)

        # --- 3. Dynamic Targeted Selection Example ---
        # Note: self.grid[row][column] mapping remains perfectly intact!
        # Let's cleanly animate Pick 1 (Index 0) and Pick 31 (Index 30) of the first year (Index 0)
        
        notable_picks = [
                    (0, 0),   # 2015, Pick 1 
                    (0, 12),  # 2015, Pick 13
                    (1, 26),  # 2016, Pick 27
                    (3, 40),  # 2018, Pick 41
                    (4, 1),   # 2019, Pick 2
                    (5, 59),  # 2020, Pick 60
                    (8, 0),   # 2023, Pick 1
                    (9, 13)   # 2024, Pick 14
                ]

        # This list will hold all individual transform animations generated below
        star_transforms = []

        for r, c in notable_picks:
            old_square = self.grid[r][c]
            
            # 1. Spawn a Star at the exact center of the square we want to morph
            # n_effects=5 creates a standard 5-pointed star. Adjust inner_radius for sharpness.
            star = Star(inner_radius=0.05, outer_radius=0.12, color=GOLD)
            star.set_fill(GOLD, opacity=1)
            star.set_stroke(GOLD_A, width=1)
            star.move_to(old_square.get_center())
            
            # 2. Package the transformation command into our animation array
            star_transforms.append(ReplacementTransform(old_square, star))
            
            # 3. Update the tracking grid reference so future animations know it's a star
            self.grid[r][c] = star

        # 4. Trigger all the star transformations dynamically using Python unpacking (*)
        # We can wrap it in LaggedStart to make the conversions ripple sequentially
        self.play(
            LaggedStart(*star_transforms, lag_ratio=0.4),
            run_time=5
        )
        self.wait(2)
        
        self.wait(2)