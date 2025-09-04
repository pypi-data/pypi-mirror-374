from __future__ import annotations
from abc import abstractmethod
from typing import Any, Callable

from .helpers import collapse_element_list
from .scales import make_linear_scale
from .shapes import Shape, Text, Line
from .shared import number, style_def


class Axis(Shape):
    """
    axis of a graph
    """

    default_axis_styles: style_def = {"stroke": "#2e2e2c"}

    def __init__(
        self,
        x_position: number,
        y_position: number,
        data_points,
        axis_length: number,
        label_format: Callable,
        max_ticks: int = 10,
        axis_styles: style_def | None = None,
        tick_length: int = 5,
        min_value=None,
        max_value=None,
        include_zero: bool = False,
        shift: bool = False,
        min_unique_values: int = 2,
        scale_maker=make_linear_scale,
        secondary: bool = False,
        title: str | None = None,
        title_styles: style_def | None = None,
        title_offset: int = 40
    ):
        _ignore = secondary, axis_styles, tick_length
        super().__init__(x_position, y_position)
        self.data_points = data_points
        self.length = axis_length
        self.scale = scale_maker(
            values=data_points,
            max_ticks=max_ticks,
            min_value=min_value,
            max_value=max_value,
            include_zero=include_zero,
            shift=shift,
            min_unique_values=min_unique_values,
        )
        self.label_format = label_format
        self.axis_line: Line | None = None
        self.tick_lines: list[Line] = []
        self.tick_texts: list[Text] = []
        self.grid_lines: list[Line] = []
        self.title: Text | None = None

    def get_element_list(self):
        return collapse_element_list(
            [self.axis_line, self.title] if self.title else [self.axis_line],
            self.tick_lines,
            self.tick_texts,
            self.grid_lines,
        )

    @abstractmethod
    def get_positions(self, values, include_axis=True) -> list[int | float | None]: ...

    def get_ticks_with_positions(self) -> list[tuple[Any, int | float | None]]:
        return list(zip(self.scale.ticks, self.get_positions(self.scale.ticks)))


class XAxis(Axis):
    """
    x-axis of a graph
    """

    default_tick_text_styles = {"text-anchor": "middle", "dominant-baseline": "hanging"}
    default_title_styles = {"text-anchor": "middle", "dominant-baseline": "middle"}

    def __init__(
        self,
        x_position: number,
        y_position: number,
        data_points,
        axis_length: number,
        label_format: Callable,
        max_ticks: int = 10,
        axis_styles: style_def | None = None,
        tick_length: int = 5,
        min_value=None,
        max_value=None,
        include_zero: bool = False,
        shift: bool = False,
        scale_maker=make_linear_scale,
        title: str | None = None,
        title_styles: style_def | None = None,
        title_offset: int = 40
    ):
        super().__init__(
            x_position=x_position,
            y_position=y_position,
            data_points=data_points,
            axis_length=axis_length,
            label_format=label_format,
            max_ticks=max_ticks,
            axis_styles=axis_styles,
            tick_length=tick_length,
            min_value=min_value,
            max_value=max_value,
            include_zero=include_zero,
            shift=shift,
            min_unique_values=2,  # at least two unique values needed on the x-axis to create a meaningful graph
            scale_maker=scale_maker,
        )
        styles = axis_styles or self.default_axis_styles.copy()
        self.axis_line = Line(
            x=self.position.x,
            y=self.position.y,
            width=axis_length,
            height=0,
            styles=styles,
        )

        for tick, pos in self.get_ticks_with_positions():
            if pos is None:  # shifted out of the visible range
                continue
            self.tick_lines.append(
                Line(x=pos, width=0, y=self.position.y, height=tick_length, styles=styles),
            )
            self.tick_texts.append(
                Text(
                    x=pos,
                    y=self.position.y + 2 * tick_length,
                    content=label_format(tick),
                    styles=self.default_tick_text_styles.copy(),
                ),
            )

        if title:
            title_x = self.position.x + self.length / 2  # Center on the axis
            title_y = self.position.y + title_offset
            self.title = Text(
                x=title_x,
                y=title_y,
                content=title,
                styles=title_styles or self.default_title_styles.copy()
            )

    def get_positions(self, values, include_axis=True) -> list[int | float | None]:
        proportions_of_range = [self.scale.value_to_fraction(value) for value in values]
        in_range = (
            (lambda prop: 0.0 <= prop <= 1.0) if include_axis else (lambda prop: 0.0 < prop <= 1.0)
        )
        return [
            self.position.x + prop * self.length if in_range(prop) else None
            for prop in proportions_of_range
        ]


class YAxis(Axis):
    """
    y-axis of a graph
    """

    default_tick_text_styles = {"text-anchor": "end", "dominant-baseline": "middle"}
    default_sec_tick_text_styles = {"text-anchor": "start", "dominant-baseline": "middle"}
    default_title_styles = {"text-anchor": "middle", "dominant-baseline": "middle"}

    def __init__(
        self,
        x_position: number,
        y_position: number,
        data_points,
        axis_length: number,
        label_format: Callable,
        max_ticks: int = 10,
        axis_styles: style_def | None = None,
        tick_length: int = 5,
        min_value=None,
        max_value=None,
        include_zero: bool = False,
        shift: bool = False,
        scale_maker=make_linear_scale,
        secondary: bool = False,
        title: str | None = None,
        title_styles: style_def | None = None,
        title_offset: int = 40
    ):
        super().__init__(
            x_position=x_position,
            y_position=y_position,
            data_points=data_points,
            axis_length=axis_length,
            label_format=label_format,
            max_ticks=max_ticks,
            axis_styles=axis_styles,
            tick_length=tick_length,
            min_value=min_value,
            max_value=max_value,
            include_zero=include_zero,
            shift=shift,
            secondary=secondary,
            min_unique_values=1,  # one unique value is sufficient for the y-axis
            scale_maker=scale_maker,
        )
        styles = axis_styles or self.default_axis_styles.copy()
        self.axis_line = Line(
            x=self.position.x,
            y=self.position.y,
            width=0,
            height=axis_length,
            styles=styles,
        )

        if secondary:
            tick_pos_offset = 0
            tick_text_offset = 2 * tick_length
            tick_text_styles = self.default_sec_tick_text_styles.copy()
        else:
            tick_pos_offset = -tick_length
            tick_text_offset = -2 * tick_length
            tick_text_styles = self.default_tick_text_styles.copy()

        for tick, pos in self.get_ticks_with_positions():
            if pos is None:  # shifted out of the visible range
                continue
            self.tick_lines.append(
                Line(
                    x=self.position.x + tick_pos_offset,
                    y=pos,
                    width=tick_length,
                    height=0,
                    styles=styles,
                ),
            )
            self.tick_texts.append(
                Text(
                    x=self.position.x + tick_text_offset,
                    y=pos,
                    content=label_format(tick),
                    styles=tick_text_styles,
                ),
            )

        if title:
            title_x = self.position.x + tick_text_offset + (title_offset if secondary else -title_offset)
            title_y = self.position.y + self.length / 2
            styles = title_styles or self.default_title_styles.copy()
            styles['transform'] = f'rotate(-90 {title_x} {title_y})'
            self.title = Text(
                x=title_x,
                y=title_y,
                content=title,
                styles=styles
            )

    def get_positions(self, values, include_axis=True) -> list[int | float | None]:
        proportions_of_range = [1 - self.scale.value_to_fraction(value) for value in values]
        in_range = (
            (lambda prop: 0.0 <= prop <= 1.0) if include_axis else (lambda prop: 0.0 <= prop < 1.0)
        )
        return [
            self.position.y + prop * self.length if in_range(prop) else None
            for prop in proportions_of_range
        ]
