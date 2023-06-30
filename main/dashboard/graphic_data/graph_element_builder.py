from typing import Optional, Any, List, Union

from matplotlib.axes import Axes

from dashboard.graphic_data.graph_elements \
    import ColorManager, ATransformer, GraphElement, Point2, Line, Arrow, Text2D, Marker


class GraphElementBuilder:
    """ 図形要素ビルダ """

    def __init__(
            self,
            color_mode: ColorManager.DisplayMode = ColorManager.DisplayMode.Dark_mode,
            transformer: Optional[ATransformer] = None,
            fig: Optional[Any] = None,
            ax: Optional[Axes] = None,
    ):
        """
        コンストラクタ
        :param color_mode: 色群種別
        :param transformer: 座標建艦クラス
        :param ax: Matplotlib.Axes
        """
        self._fig: Any = fig
        self._ax: Any = ax
        self._transformer: Optional[ATransformer] = transformer
        self._elements: List[GraphElement] = []
        self._color_manager = ColorManager(mode=color_mode)

    def get_color(self, color: ColorManager.ColorIx):
        return self._color_manager.get_color(color)

    def get_elements(self) -> List[GraphElement]:
        return self._elements

    def set_fig(self, fig: Any):
        if fig:
            self._fig = fig

    def get_fig(self) -> Any:
        return self._fig

    def set_ax(self, ax: Axes):
        if ax:
            self._ax = ax

    def get_ax(self) -> Axes:
        return self._ax

    def build_line(
            self,
            start: Point2,
            end: Point2,
            line_width: Union[float | int | str],
            color: str,
            solid_capstyle: str = 'butt',
            default_visibility: bool = True,
            **kwargs,
    ) -> Any:
        g = Line(
            start=start,
            end=end,
            line_width=line_width,
            color=color,
            solid_capstyle=solid_capstyle,
            default_visibility=default_visibility,
            transformer=self._transformer,
            ax=self._ax,
            **kwargs,
        )
        self._elements.append(g)
        return g

    def build_arrow(
            self,
            from_pos: Point2,
            to_pos: Point2,
            line_width: Union[float | int | str],
            color: str,
            solid_capstyle: str = 'butt',
            default_visibility: bool = True,
            **kwargs,
    ) -> Any:
        g = Arrow(
            from_pos=from_pos,
            to_pos=to_pos,
            line_width=line_width,
            color=color,
            solid_capstyle=solid_capstyle,
            default_visibility=default_visibility,
            transformer=self._transformer,
            ax=self._ax,
            **kwargs,
        )
        self._elements.append(g)
        return g

    def build_text(
            self,
            start: Point2,
            text: str,
            color: str,
            fontsize: Union[float | int | str],
            horizontal_alignment: str,
            vertical_alignment: str,
            rotation: Union[float | int | str],
            default_visibility: bool = True,
            **kwargs,
    ):
        g = Text2D(
            start=start,
            text=text,
            color=color,
            fontsize=fontsize,
            horizontal_alignment=horizontal_alignment,
            vertical_alignment=vertical_alignment,
            rotation=rotation,
            default_visibility=default_visibility,
            transformer=self._transformer,
            ax=self._ax,
            **kwargs,
        )
        self._elements.append(g)
        return g

    def build_marker(
            self,
            center: Point2,
            marker: str,
            color: str,
            size: int,
            default_visibility: bool = True,
            **kwargs,
    ) -> Any:
        g = Marker(
            center=center,
            marker=marker,
            color=color,
            size=size,
            default_visibility=default_visibility,
            transformer=self._transformer,
            ax=self._ax,
            **kwargs,
        )
        self._elements.append(g)
        return g

    def build(
            self,
            fig: Optional[Any] = None,
            ax: Optional[Axes] = None,
    ) -> None:
        """
        Matplotlib 図形要素生成
        :param fig:
        :param ax:
        :return:
        """
        self.set_fig(fig)
        self.set_ax(ax)
        for element in self.get_elements():
            element.create(self._ax)

    def highlight_graph_elements(
            self,
            target_elements: List[str],
            reset: bool = False
    ) -> None:
        """
        指定された図形を強調表示する
        :param target_elements: 強調表示する図形識別子群
        :param reset: True: 初期状態へ戻す False: 強調表示する
        :return:
        """
        for element in self.get_elements():
            g = element.get_artist()
            if not isinstance(g, list):
                if len(g.get_gid()) <= 0 or reset or g.get_gid() in target_elements:
                    g.set_visible(True)
                else:
                    g.set_visible(False)
            else:
                for gg in g:
                    if len(gg.get_gid()) <= 0 or reset or gg.get_gid() in target_elements:
                        gg.set_visible(True)
                    else:
                        gg.set_visible(False)
