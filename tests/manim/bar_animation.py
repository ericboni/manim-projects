from manim import *
import random
X_AXIS_RUN_TIME = 1   # seconds for the x-axis to draw in
Y_AXIS_RUN_TIME = 1   # seconds for the y-axis to draw in
BAR_WIDTH = 0.6         # 0-1 of each slot; smaller = more space between bars
BAR_LAG_RATIO = 0.2     # stagger between each bar's pop-up start
len_bars = 15

class BarChartExample(Scene):
    def construct(self):
        chart = BarChart(
            values=[random.randint(1, 50) for _ in range(len_bars)],
            bar_names=[f"bar_{i}" for i in range(len_bars)],
            y_range=[0, 50, 10],
            bar_width=BAR_WIDTH,
            x_axis_config={"label_constructor": Text,},
            y_axis_config={"label_constructor": Text},
        )

        self.play(Create(chart.x_axis, run_time=X_AXIS_RUN_TIME))
        self.play(Create(chart.y_axis, run_time=Y_AXIS_RUN_TIME))

        # Collapse each bar to ~0 height, anchored at its baseline edge, so the
        # grow animation stretches height only and never touches the width.
        full_heights = [bar.height for bar in chart.bars]
        anchors = [DOWN if value >= 0 else UP for value in chart.values]

        for bar, anchor in zip(chart.bars, anchors):
            bar.stretch_to_fit_height(0.001, about_edge=anchor)

        self.play(
            LaggedStart(
                *[
                    bar.animate.stretch_to_fit_height(height, about_edge=anchor)
                    for bar, height, anchor in zip(chart.bars, full_heights, anchors)
                ],
                lag_ratio=BAR_LAG_RATIO,
            )
        )
        self.wait()
