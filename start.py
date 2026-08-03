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
        rows = 20          # 15 years of draft data
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
                sq.set_fill(GREY, opacity=0.7)
                sq.set_stroke(GREY, width=1)
                
                round1_group.add(sq)
                grid_row.append(sq)
                
            # Build Round 2 (Picks 31-60)
            for c in range(picks_per_round):
                sq = Square(side_length=square_size)
                sq.set_fill(GREY, opacity=0.7)
                sq.set_stroke(GREY, width=1)
                
                round2_group.add(sq)
                grid_row.append(sq)

            # Arrange the squares within their respective rounds
            round1_group.arrange(RIGHT, buff=square_buff)
            round2_group.arrange(RIGHT, buff=square_buff)
            
            # Assemble the complete row
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

        # Arrange all rows vertically
        matrix.arrange(DOWN, buff=row_buff)
        
        # Center everything on the screen
        matrix.move_to(ORIGIN)

        # --- 2. Intro Animation (Row by Row) ---
        for r in range(rows):
            current_year_text = matrix[r][0]
            current_round1 = matrix[r][1]
            current_round2 = matrix[r][2]
            
            self.play(
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
        notable_picks = [
                    (0, 0),   # 2010, Pick 1 
                    (0, 12),  # 2010, Pick 13
                    (1, 26),  # 2011, Pick 27
                    (3, 40),  # 2013, Pick 41
                    (4, 1),   # 2014, Pick 2
                    (5, 59),  # 2015, Pick 60
                    (8, 0),   # 2018, Pick 1
                    (9, 13)   # 2019, Pick 14
                ]

        star_transforms = []

        for r, c in notable_picks:
            old_square = self.grid[r][c]
            
            star = Star(inner_radius=0.05, outer_radius=0.12, color=GOLD)
            star.set_fill(GOLD, opacity=1)
            star.set_stroke(GOLD_A, width=1)
            star.move_to(old_square.get_center())
            
            star_transforms.append(ReplacementTransform(old_square, star))
            self.grid[r][c] = star

        self.play(
            LaggedStart(*star_transforms, lag_ratio=0.4),
            run_time=5
        )
        self.wait(2)

        # Fade out all picks except column 0
        fade_out = []
        for row in range(rows):
            for col in range(picks_per_round * 2):
                if col > 0:
                    fade_out.append(FadeOut(self.grid[row][col], shift=DOWN, scale=0.5))
                else:
                    old_obj = self.grid[row][col]
                    new_sq = Square(side_length=square_size, color=GREY)
                    new_sq.move_to(old_obj.get_center())
                    new_sq.set_fill(GREY, opacity=0.7)
                    new_sq.set_stroke(GREY, width=1)
                    fade_out.append(ReplacementTransform(old_obj, new_sq))
                    
                    # Update tracking grid reference
                    self.grid[row][col] = new_sq

        self.play(*fade_out, run_time=2)
        self.wait(2)

        # --- 4. Re-arrange Remaining Squares & Year Labels to the Bottom ---
        
        # Group remaining column-0 squares together
        remaining_squares = VGroup(*[self.grid[row][0] for row in range(rows)])
        
        # Prepare target positions using MoveToTarget
        remaining_squares.generate_target()
        remaining_squares.target.arrange(RIGHT, buff=square_buff*3)  # Extra spacing for clarity
        remaining_squares.target.move_to([0, -2.5, 0]) # Centers row horizontally, places it low on screen
        
        distribute_anims = [MoveToTarget(remaining_squares)]
        
        # Pull the text labels from the original layout matrix and position them under the targets
        for row in range(rows):
            year_label = matrix[row][0]
            corresponding_target_sq = remaining_squares.target[row]
            
            year_label.generate_target()
            
            # Scale down slightly so the rotated labels don't crash into each other
            year_label.target.scale(0.8) 
            
            # Rotate dynamically (45 degrees)
            year_label.target.rotate(45 * DEGREES)
            
            # Snap it right below the square's bottom edge with a small buffer
            year_label.target.next_to(corresponding_target_sq, DOWN, buff=0.15)
            
            distribute_anims.append(MoveToTarget(year_label))
            
        # Execute all movements concurrently
        self.play(*distribute_anims, run_time=2)

        
        self.wait(2)
        # --- 5. Transform Squares into a Bar Chart ---
        bar_anims = []
        
        for row in range(rows):
            sq = self.grid[row][0]
            
            # Save the original baseline Y-coordinate before stretching
            original_bottom_y = sq.get_bottom()[1]
            
            # Generate random visual properties
            random_height = random.uniform(0.5, 4.0)
            random_color = random.choice(sample_colors)
            
            sq.generate_target()
            
            # 1. Stretch the target's height
            sq.target.stretch_to_fit_height(random_height)
            sq.target.stretch_to_fit_width(square_size)
            
            # 2. FIX: Lock the bottom edge back down to where the square originally sat
            sq.target.align_to([0, original_bottom_y, 0], DOWN)
            
            # 3. Apply color styling
            sq.target.set_fill(random_color, opacity=0.8)
            sq.target.set_stroke(random_color, width=1.5)
            
            bar_anims.append(MoveToTarget(sq))
            
        # Animate the bars growing upward simultaneously
        self.play(*bar_anims, run_time=1.5, rate_func=linear)

        self.wait(2)