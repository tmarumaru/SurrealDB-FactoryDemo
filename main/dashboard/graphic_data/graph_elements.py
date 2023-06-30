import sys
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import List, Optional, Union, Any

from matplotlib.artist import Artist
from matplotlib.axes import Axes

MIN_COORDINATE = sys.float_info.min
MAX_COORDINATE = sys.float_info.max


class ColorManager:
    """
    クラフの色管理クラス
    """

    class DisplayMode(Enum):
        """ グラフの表示モード """
        Dark_mode = 0,
        White_mode = 1,

    class ColorIx(IntEnum):
        """ 色定義 """
        BACKGROUND_COLOR = 0,
        FONT_COLOR = 1,
        PROCESS_PRODUCT = 2,
        PROCESS_SEMI_PRODUCT = 3,
        TRANSFER = 4,
        PROCESS_DEFECT = 5,
        H_LINE = 6,

    def __init__(
            self,
            mode: DisplayMode = DisplayMode.White_mode
    ):
        """
        コンストラクタ
        :param mode: 色モード
        """
        self._mode = mode
        self._color_tables: {str, []} = {}
        self._create_color_tables()

    def _create_color_tables(self) -> None:
        """
        色モード毎にカラーマップテーブルを作成する
        :return:
        """

        self._color_tables[ColorManager.DisplayMode.White_mode.name] = [
            'whitesmoke',  # BACKGROUND_COLOR
            'midnightblue',  # FONT_COLOR
            'deepskyblue',  # PROCESS_PRODUCT
            'lime',  # PROCESS_SEMI_PRODUCT
            'yellowgreen',  # TRANSFER,
            'red',  # DEFECT
            'grey',  # H_LINE
        ]
        self._color_tables[ColorManager.DisplayMode.Dark_mode.name] = [
            'midnightblue',  # BACKGROUND_COLOR
            'white',  # FONT_COLOR
            'deepskyblue',  # PROCESS_PRODUCT
            'lime',  # PROCESS_SEMI_PRODUCT
            'yellowgreen',  # TRANSFER,
            'red',  # DEFECT
            'grey',  # H_LINE
        ]

    def set_mode(self, mode: DisplayMode) -> None:
        """
        カラーモード設定
        :param mode: カラーモード
        :return:
        """
        self._mode = mode

    def get_mode(self) -> DisplayMode:
        """
        カラーモード取得
        :return: カラーモード
        """
        return self._mode

    def get_current_color_table(self) -> List[str]:
        """
        現在設定しているカラーテーブル取得
        :return:
        """
        return self._color_tables[self._mode.name]

    def get_color(self, target: ColorIx) -> str:
        """
        色の取得
        :param target: 色指標
        :return: matplotlibの色名
        """
        return self._color_tables[self._mode.name][target.value]


@dataclass
class Point2:
    """ ２次元点要素 """
    x: float
    y: float

    def __repr__(self):
        return f'[{self.x}, {self.y}]'


@dataclass
class Window:
    """ ウィンドウ要素 """
    min: Point2
    max: Point2

    def __repr__(self):
        return f'[{self.min}, {self.max}]'


class ATransformer:
    """
    座標変換 抽象クラス
    """

    @abstractmethod
    def tr(
            self,
            p: Point2
    ) -> (Any, Any):
        """
        座標変換
        :param p: 被変換座標
        :return: 変換結果座標
        """
        pass


class AGraphLib:
    """
    図形管理 抽象クラス
    """

    def __init__(
            self,
            transformer: Optional[ATransformer] = None,
            ax: Optional[Axes] = None,
    ):
        """
        コンストラウタ
        :param transformer: 座標変換クラス
        :param ax: Matplotlib Axes
        """
        self._transformer = transformer
        self._ax = ax

    def set_ax(self, ax) -> None:
        """
        Axes設定
        :param ax: Axes
        :return:
        """
        self._ax = ax

    def get_ax(self, ax: Optional[Axes]) -> Any:
        """
        Axes取得
        :param ax: Axesが設定されていない場合、このAxesを返す
        :return: Matplotlib Axes
        """
        if not (self._ax or ax):
            raise RuntimeError(f'Axes was not setting.')
        return self._ax if self._ax else ax

    def tr(self, p: Point2) -> (Any, Any):
        """
        座標変換
        :param p: 被変換座標
        :return: 返還後の座標
        """
        return self._transformer.tr(p) if self._transformer else (p.x, p.y)


class GraphElement(AGraphLib):
    """
    図形データ 基底クラス
    """

    def __init__(
            self,
            color: str,
            marker: str = 'o',
            line_style: str = '-',
            line_width: int = 1,
            gid: str = '',
            transformer: Optional[ATransformer] = None,
            ax: Optional[Axes] = None,
            zorder: float = 1,
            default_visibility: bool = True,
    ):
        """
        図形データ基底クラス
        :param color:
        :param marker: see matplotlib.markers
        :param line_style: description
            '-' or 'solid' solid line
            '--' or 'dashed' dashed line
            '-.' or 'dashdot' dash-dotted line
            ':' or 'dotted' dotted line
            'none', 'None', ' ', or '' draw nothing
        """
        super(GraphElement, self).__init__(transformer=transformer, ax=ax)
        self._artist: Any = None
        self.gid = gid
        self.color = color
        self.marker = marker
        self.line_style = line_style
        self.line_width = line_width
        self.zorder = zorder
        self.default_visibility = default_visibility
        self.cid_press = []
        self.cid_release = []
        self.cid_motion = []

    @abstractmethod
    def create(
            self,
            ax: Optional[Axes] = None
    ) -> Any:
        """
        Matplotlib 図形オブジェクト生成
        :param ax: Axes
        :return: 図形オブジェクト
        """
        raise NotImplemented(f'Not implemented "create()" function.')

    def set_artist(self, artist: Any) -> None:
        """
        図形オブジェクト格納
        :param artist: 図形オブジェクト
        :return:
        """
        self._artist = artist

    def get_artist(self) -> Artist:
        """
        図形オブジェクト取得
        :return: 図形オブジェクト
        """
        return self._artist

    def get_gid(self) -> str:
        """
        グループＩＤ取得
        :return:
        """
        return self.gid

    def set_visible(self, mode: bool) -> None:
        """
        図形の表示／非表示
        :param mode: True 図形表示、False 図形を消す
        :return:
        """
        if not isinstance(self._artist, list):
            self._artist.set_visible(mode)
        else:
            for g in self._artist:
                g.set_visible(mode)

    def reset_visible(self) -> None:
        """
        図形の表示状態を初期状態に戻す
        :return:
        """
        self.set_visible(mode=self.default_visibility)

    def get_default_visibility(self) -> bool:
        """
        初期の図形の表示状態を取得する
        :return:
        """
        return self.default_visibility

    @abstractmethod
    def on_press(self, event):
        pass

    @abstractmethod
    def on_release(self, event):
        pass

    @abstractmethod
    def on_motion(self, event):
        pass

    def connect(self, element: Any):
        elements = [element] if not isinstance(element, list) else element
        for e in elements:
            # 'connect to all the events we need'
            e.set_picker(True)
            self.cid_press.append(
                e.figure.canvas.mpl_connect('button_press_event', self.on_press))
            self.cid_release.append(
                e.figure.canvas.mpl_connect('button_release_event', self.on_release))
            self.cid_motion.append(
                e.figure.canvas.mpl_connect('motion_notify_event', self.on_motion))
            e.figure.canvas.mpl_connect('figure_enter_event', self.on_motion)

    def disconnect(self, element: Any):
        elements = [element] if not isinstance(element, list) else element
        for e in elements:
            # 'disconnect all the stored connection ids'
            e.figure.canvas.mpl_disconnect(self.cid_press)
            e.figure.canvas.mpl_disconnect(self.cid_release)
            e.figure.canvas.mpl_disconnect(self.cid_motion)
        self.cid_press.clear()
        self.cid_release.clear()
        self.cid_motion.clear()


class Line(GraphElement):
    """ 線図形 """

    def __init__(
            self,
            start: Point2,
            end: Point2,
            solid_capstyle: str = 'butt',
            **kwargs
    ):
        """
        コンストラクタ
        :param start: 始点
        :param end: 終点
        :param solid_capstyle: 線の形状
        :param kwargs: その他のパラメータ
        """
        super(Line, self).__init__(**kwargs)
        self.start = start
        self.end = end
        self.solid_capstyle = solid_capstyle

        if not (start and end):
            raise RuntimeError(f'Invalid Point2 {start=}, {end=}')

    def create(
            self,
            ax: Optional[Axes] = None
    ) -> Any:
        """
        Matplotlib 図形オブジェクト生成
        :param ax: Zxes
        :return: 生成した図形オブジェクト
        """
        _ax = self.get_ax(ax)
        x, y = zip(self.tr(self.start), self.tr(self.end))
        result = _ax.plot(
            list(x),
            list(y),
            color=self.color,
            linewidth=self.line_width,
            solid_capstyle=self.solid_capstyle,
            zorder=self.zorder,
            gid=self.gid,
        )
        self.set_artist(result)
        # self.connect(result)
        # 初期表示状態設定
        self.set_visible(mode=self.default_visibility)
        return result

    def on_press(self, event):
        pass

    def on_release(self, event):
        pass

    def on_motion(self, event):
        pass


class Polyline(GraphElement):
    """ 折れ線図形 """

    def __init__(
            self,
            points: List[Point2],
            **kwargs
    ):
        """
        コンストラクタ
        :param points: 点群座標 (点の数 ＞ １）
        :param kwargs: Matplotlibへ渡すパラメータ
        """
        super(Polyline, self).__init__(**kwargs)
        self.points: [Point2] = points

    def create(
            self,
            ax: Optional[Axes] = None
    ) -> Any:
        # TODO 実装してない
        pass


class Circle(GraphElement):
    """ 円図形 """

    def __init__(
            self,
            center: Point2,
            radius: float,
            **kwargs
    ):
        """
        コンストラクタ
        :param center: 中心座標
        :param radius: 半径
        :param kwargs: Matplotlibへ渡すパラメータ
        """
        super(Circle, self).__init__(**kwargs)
        self.center = center
        self.radius = radius

    def create(
            self,
            ax: Optional[Axes] = None
    ) -> Any:
        # TODO 実装してない
        pass


class Arrow(GraphElement):
    """ 矢印図形 """

    def __init__(
            self,
            from_pos: Point2,
            to_pos: Point2,
            solid_capstyle: str = 'butt',
            **kwargs,
    ):
        """
        コンストラクタ
        :param from_pos: 始点
        :param to_pos: 終点
        :param solid_capstyle: 線の形状
        :param kwargs: Matplotlibへのパラメータ
        """
        super(Arrow, self).__init__(**kwargs)
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.dx = to_pos.x - from_pos.x
        self.dy = to_pos.y - from_pos.y
        self.solid_capstyle = solid_capstyle

    def create(
            self,
            ax: Optional[Axes] = None
    ) -> Any:
        """
        Matplotlib 図形オブジェクト生成
        :param ax: Axes
        :return: 生成した図形オブジェクト
        """
        _ax = self.get_ax(ax)
        x, y = zip(self.tr(self.from_pos), self.tr(self.to_pos))
        result = _ax.plot(
            list(x),
            list(y),
            color=self.color,
            linewidth=self.line_width,
            solid_capstyle=self.solid_capstyle,
            zorder=self.zorder,
            gid=self.gid,
        )
        self.set_artist(result)
        # 初期表示状態設定
        self.set_visible(mode=self.default_visibility)
        return result

    def on_press(self, event):
        pass

    def on_release(self, event):
        pass

    def on_motion(self, event):
        pass


class Marker(GraphElement):
    """ マーカー図形 """

    def __init__(
            self,
            center: Point2,
            size: int = 50,
            **kwargs,
    ):
        """
        コンストラクタ
        :param center: 中心座標
        :param size: 大槻さ
        :param kwargs: Matplotlibへのパラメータ
        """
        super(Marker, self).__init__(**kwargs)
        self.center = center
        self.size = size

    def create(
            self,
            ax: Optional[Axes] = None
    ) -> Any:
        """
        Matplotlib 図形オブジェクト生成
        :param ax: Axes
        :return: 生成した図形オブジェエクト
        """
        _ax = self.get_ax(ax)
        center_x, center_y = self.tr(self.center)
        result = _ax.scatter(
            x=center_x, y=center_y,
            c=self.color,
            marker=self.marker,
            s=self.size,
            zorder=self.zorder,
            gid=self.gid,
        )
        self.set_artist(result)
        # self.connect(result)
        # 初期表示状態設定
        self.set_visible(mode=self.default_visibility)
        return result

    def on_press(self, event):
        pass

    def on_release(self, event):
        pass

    def on_motion(self, event):
        pass


class Text2D(GraphElement):
    """ ２次元テキスト図形 """

    def __init__(
            self,
            start: Point2,
            text: str,
            fontsize: Union[str | int] = 'medium',
            horizontal_alignment: str = 'left',
            vertical_alignment: str = 'bottom',
            rotation_mode: Optional[str] = None,
            rotation: Optional[Union[float | str]] = None,
            **kwargs,
    ):
        """
        コンストラクタ
        :param start: 始点
        :param text: 文字列
        :param fontsize: フォントサイズ
            'xx-small'	極極小	0.579
            'x-small'	極小	0.694
            'small'	小	0.833
            'medium'	デフォルト	1.000
            'large'	大	1.2
            'x-large'	極大	1.44
            'xx-large'	極々大	1.728
        :param horizontal_alignment: {'left', 'center', 'right'}
        :param vertical_alignment: {'bottom', 'baseline', 'center', 'center_baseline', 'top'}
        :param rotation_mode: {None, 'default', 'anchor'}
        :param rotation: float or {'vertical', 'horizontal'}
        :param kwargs:
        """
        super(Text2D, self).__init__(**kwargs)
        self.start = start
        self.text = text
        self.fontsize = fontsize
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment
        self.rotation_mode = rotation_mode
        self.rotation = rotation

    def create(
            self,
            ax: Optional[Axes] = None
    ) -> List[Artist]:
        """
        Matplotlib 図形オブジェクト生成
        :param ax: Axes
        :return: 生成した図形オブジェクト
        """
        _ax = self.get_ax(ax)
        start_x, start_y = self.tr(self.start)
        result = _ax.annotate(
            xy=[start_x, start_y],
            text=self.text,
            horizontalalignment=self.horizontal_alignment,
            verticalalignment=self.vertical_alignment,
            rotation=self.rotation,
            color=self.color,
            size=self.fontsize,
            zorder=self.zorder,
            gid=self.gid,
        )
        self.set_artist(result)
        # self.connect(result)
        # 初期表示状態設定
        self.set_visible(mode=self.default_visibility)
        return result

    def on_press(self, event):
        pass

    def on_release(self, event):
        pass

    def on_motion(self, event):
        pass

