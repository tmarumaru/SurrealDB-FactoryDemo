import datetime
from abc import ABC, abstractmethod
from typing import Any, Optional

from matplotlib import pyplot as plt, dates

import util
from dashboard.graphic_data.graph_element_builder import GraphElementBuilder
from dashboard.graphic_data.graph_elements import Point2, ColorManager, MAX_COORDINATE, MIN_COORDINATE, Window
from dashboard.page2.production_line_data_cache import ProductionLineDataCache

Y_AXIS_BASE = 100
Y_AXIS_HEIGHT = 50
Y_AXIS = {
    'PRODUCTION_LINE:pl001': Y_AXIS_HEIGHT * 1 + Y_AXIS_BASE,
    'STORAGE:storage1': Y_AXIS_HEIGHT * 2 + Y_AXIS_BASE,
    'PRODUCTION_LINE:pl002': Y_AXIS_HEIGHT * 3 + Y_AXIS_BASE,
    'STORAGE:storage2': Y_AXIS_HEIGHT * 4 + Y_AXIS_BASE,
    'PRODUCTION_LINE:pl003': Y_AXIS_HEIGHT * 5 + Y_AXIS_BASE,
    'STORAGE:storage3': Y_AXIS_HEIGHT * 6 + Y_AXIS_BASE,
    'PRODUCTION_LINE:pl004': Y_AXIS_HEIGHT * 12 + Y_AXIS_BASE,
    'STORAGE:storage4': Y_AXIS_HEIGHT * 13 + Y_AXIS_BASE,
    'PRODUCTION_LINE:pl005': Y_AXIS_HEIGHT * 14 + Y_AXIS_BASE,
    'STORAGE:storage5': Y_AXIS_HEIGHT * 15 + Y_AXIS_BASE,
    'PRODUCTION_LINE:pl006': Y_AXIS_HEIGHT * 16 + Y_AXIS_BASE,
    'STORAGE:storage6': Y_AXIS_HEIGHT * 17 + Y_AXIS_BASE,
    'STORAGE:repair1': Y_AXIS_HEIGHT * 18 + Y_AXIS_BASE,
    '?': Y_AXIS_HEIGHT * 19 + Y_AXIS_BASE,
}

FIRST_PROCESSES = ['PRODUCTION_LINE:pl001', 'PRODUCTION_LINE:pl004']
WAREHOUSES = ['STORAGE:storage3', 'STORAGE:storage6']

FONT_SIZE = 6


class ATransformer:

    @abstractmethod
    def tr(
            self,
            p: Point2
    ) -> (Any, Any):
        pass

    @abstractmethod
    def trx(
            self,
            x: float,
    ):
        pass


class Transformer(ATransformer, ABC):

    def tr(
            self,
            p: Point2
    ) -> (Any, Any):
        return datetime.datetime.fromtimestamp(float(p.x), tz=datetime.timezone.utc), p.y

    def trx(self, x: float) -> datetime:
        return datetime.datetime.fromtimestamp(float(x), tz=datetime.timezone.utc)


class ProductionLinesStatusView:

    def __init__(
            self,
            production_data_cache: ProductionLineDataCache,
            transformer: ATransformer = Transformer(),
            color_mode: ColorManager.DisplayMode = ColorManager.DisplayMode.Dark_mode,
    ):
        self._production_data_cache = production_data_cache
        self._graphic_builder = GraphElementBuilder(color_mode=color_mode, transformer=transformer)
        self._transformer = transformer
        self._window = None
        self._fig = None
        self._ax = None
        self._init()

    def _init(self):

        x_min, x_max = MAX_COORDINATE, MIN_COORDINATE
        y_min, y_max = MAX_COORDINATE, MIN_COORDINATE
        number_of_unfinished_works = 0

        # 各仕掛品毎の工程作業グラフを作成する
        for product_id, product_data in self._production_data_cache.products_data.items():
            # 仕掛品毎の作業履歴を処理する
            for history_ix in product_data.production_histories:
                production_history = self._production_data_cache.product_work_histories[history_ix]
                # 工程作業開始時間
                started = production_history.get('started_utime', None)
                # 工程作業終了時間
                ended = production_history.get('ended_utime', None)
                # 製造ライン識別子取得
                production_line = production_history.get('production_line', '?')
                # 工程終了時間が無い（仕掛中）の仕掛品数を加算
                if not (started and ended):
                    number_of_unfinished_works += 1

                # 製品の仕掛品と部品の仕掛品でグラフの色を変える
                color = self._graphic_builder.get_color(ColorManager.ColorIx.PROCESS_DEFECT) \
                    if production_history.get('inspection_result', '') == 'NG' \
                    else self._graphic_builder.get_color(ColorManager.ColorIx.PROCESS_PRODUCT) \
                    if self._production_data_cache.products[product_data.product_info_index].get('data', {}).get(
                    'type') == 'PRODUCT' \
                    else self._graphic_builder.get_color(ColorManager.ColorIx.PROCESS_SEMI_PRODUCT)

                # グラフ開始点
                start = Point2(started, Y_AXIS[production_line])
                # 終了点：仕掛中（工程の終了時間が無い）は開始時間に適当な値を加えグラフ描画する
                end = Point2(ended, Y_AXIS[production_line]) \
                    if ended else Point2(start.x + 100, Y_AXIS[production_line])

                # 工程作業の線分描画
                self._graphic_builder.build_line(
                    start=start,
                    end=end,
                    line_width=5,
                    color=color,
                    solid_capstyle='butt',
                    zorder=1,
                    gid=product_id.split(':')[1],
                )

                # 製造ラインが、'pl001', 'pl004' の場合、工程作業線分の下へ仕掛品番号を表示する
                if production_line == 'PRODUCTION_LINE:pl001' or production_line == 'PRODUCTION_LINE:pl004':
                    self._graphic_builder.build_text(
                        start=Point2(started, Y_AXIS[production_line]),
                        text=production_history.get('product', '?').split(':')[1] + ' ',
                        color=self._graphic_builder.get_color(ColorManager.ColorIx.FONT_COLOR),
                        fontsize=FONT_SIZE,
                        horizontal_alignment='left',
                        vertical_alignment='top',
                        rotation=90,
                        gid=product_id.split(':')[1],
                    )

                # グラフ図形の最大値、最小値を求める
                x_min = min(x_min, started, ended if ended else MAX_COORDINATE)
                x_max = max(x_max, started, ended if ended else MIN_COORDINATE)
                y_min = min(y_min, Y_AXIS[production_line])
                y_max = max(y_max, Y_AXIS[production_line])

            # 移動履歴から仕掛品の移動グラフを描画する
            for history_ix in product_data.transfer_work_histories:
                transfer_working_history = self._production_data_cache.product_transfer_work_histories[history_ix]
                # 移動時刻
                timestamp = float(transfer_working_history.get('timestamp_utime', None))
                # 対象仕掛品識別子
                product_id = transfer_working_history.get('product', '?').split(':')[1]
                # 移動元識別子
                from_id = transfer_working_history.get('from_id', None)
                # 移動先識別子
                to_id = transfer_working_history.get('to_id', None)

                # 欠陥品はrepair1貯蔵庫に移動されるが、グラフにすると見にくいので描画しない
                if to_id == 'STORAGE:repair1':
                    continue

                # 次の移動作業をが存在すれば、貯蔵庫に存在した線分を描画する
                if to_id.split(':')[0] == 'STORAGE':
                    for ix in product_data.transfer_work_histories:
                        tx_work_history = self._production_data_cache.product_transfer_work_histories[ix]
                        tx_from_id = tx_work_history.get('from_id', None)
                        if tx_from_id and tx_from_id == to_id:
                            tx_timestamp = float(tx_work_history.get('timestamp_utime', None))
                            self._graphic_builder.build_line(
                                start=Point2(timestamp, Y_AXIS[to_id]),
                                end=Point2(tx_timestamp, Y_AXIS[tx_from_id]),
                                line_width=3,
                                color=self._graphic_builder.get_color(ColorManager.ColorIx.TRANSFER),
                                zorder=1,
                                gid=product_id,
                            )

                if to_id in ['STORAGE:storage3', 'STORAGE:storage6']:
                    color = self._graphic_builder.get_color(ColorManager.ColorIx.PROCESS_PRODUCT) \
                        if self._production_data_cache.products[product_data.product_info_index].get('data', {}).get(
                        'type') == 'PRODUCT' \
                        else self._graphic_builder.get_color(ColorManager.ColorIx.PROCESS_SEMI_PRODUCT)
                    self._graphic_builder.build_marker(
                        center=Point2(timestamp, Y_AXIS[to_id]),
                        marker='D',
                        color=color,
                        size=8,
                        zorder=1,
                        gid=product_id,
                    )

                self._graphic_builder.build_arrow(
                    from_pos=Point2(timestamp, Y_AXIS[from_id]),
                    to_pos=Point2(timestamp, Y_AXIS[to_id]),
                    line_width=1,
                    color=self._graphic_builder.get_color(ColorManager.ColorIx.TRANSFER),
                    solid_capstyle='butt',
                    gid=product_id,
                )

                x_min = min(x_min, timestamp)
                x_max = max(x_max, timestamp)
                y_min = min(y_min, Y_AXIS[from_id], Y_AXIS[to_id])
                y_max = max(y_max, Y_AXIS[from_id], Y_AXIS[to_id])

        # TODO 暫定的にview_x_minを変更する
        x_min = util.convert_utc_string_to_datetime('2023-01-01T00:00:00+00:00').timestamp()
        # Ｙ軸の上限へ下駄履かせ
        y_max += 10
        window = Window(min=Point2(x_min, y_min), max=Point2(x_max, y_max))
        self._window = window

    def build(
            self,
            view_x_min: Optional[float] = None,
            view_x_max: Optional[float] = None,
    ) -> (Any, Any):
        """
        Matplotlibの図形要素を生成する
        :param view_x_min:  最小Ｘ座標値
        :param view_x_max:  最大Ｘ座標値
        :return: (fig, Windows)
        """

        x_min = self._window.min.x
        y_min = self._window.min.y
        x_max = self._window.max.x
        y_max = self._window.max.y

        if self._ax and self._fig:
            return self._fig, Window(min=Point2(x_min, y_min), max=Point2(x_max, y_max))

        # 製造ライン、貯蔵庫のＸ軸を描画
        for i, production_line in enumerate(self._production_data_cache.production_lines):
            start = Point2(x_min, Y_AXIS[production_line.get('id')])
            end = Point2(x_max, Y_AXIS[production_line.get('id')])

            self._graphic_builder.build_line(
                start=start,
                end=end,
                color=self._graphic_builder.get_color(ColorManager.ColorIx.H_LINE),
                line_style='--',
                line_width=0.2,
                zorder=3,
            )

        for i, storage in enumerate(self._production_data_cache.storages):
            if storage.get('id') == 'STORAGE:repair1':
                continue
            start = Point2(x_min, Y_AXIS[storage.get('id')])
            end = Point2(x_max, Y_AXIS[storage.get('id')])
            self._graphic_builder.build_line(
                start=start,
                end=end,
                color=self._graphic_builder.get_color(ColorManager.ColorIx.H_LINE),
                line_style='--',
                line_width=0.3,
                zorder=3,
            )

        tr = Transformer()
        self._fig, self._ax = plt.subplots()
        self._ax.set_picker(True)
        # グラフ背景色設定
        self._ax.set_facecolor(self._graphic_builder.get_color(ColorManager.ColorIx.BACKGROUND_COLOR))
        self._graphic_builder.set_ax(self._ax)
        self._graphic_builder.set_fig(self._fig)

        # 図形データ生成
        self._graphic_builder.build()

        # Ｘ軸設定
        self._ax.xaxis.set_major_locator(dates.HourLocator())
        self._ax.xaxis.set_major_formatter(dates.DateFormatter('%m/%d %H:%m', tz=datetime.timezone.utc))
        self._ax.xaxis.set_minor_locator(dates.MinuteLocator(interval=15))
        for text in self._ax.get_xminorticklabels():
            text.set_fontsize(FONT_SIZE)
        # Ｘ軸表示を自動調整
        # fig.autofmt_xdate(rotation=90)
        self._fig.autofmt_xdate()

        # Ｘ軸以外を非表示
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.tick_params(labelsize=FONT_SIZE)

        labels = [label.split(':')[1] for label, value in Y_AXIS.items() if label != 'STORAGE:repair1' and label != '?']
        values = [value for label, value in Y_AXIS.items() if label != 'STORAGE:repair1' and label != '?']

        # Y軸の目盛りに任意の文字列を表示
        self._ax.set_yticks(values)
        self._ax.set_yticklabels(labels)

        if view_x_max and view_x_max:
            self._ax.set_xlim(xmin=tr.trx(view_x_min), xmax=tr.trx(view_x_max))
        self._ax.set_ylim(0, self._window.max.y)
        return self._fig, Window(min=Point2(x_min, y_min), max=Point2(x_max, y_max))

    def highlight_product_production_history(
            self,
            selected_product_id: str,
            reset: bool = False
    ) -> None:
        """
        指定された仕掛品の製造履歴をハイラト表示する
        :param selected_product_id:
        :param reset: True: 製造履歴を初期城代へ戻す  False: 指定され仕掛品をハイライト表示する
        :return:
        """

        if selected_product_id == 'all':
            self._graphic_builder.highlight_graph_elements(target_elements=[], reset=reset)
            return

        product_ids = [selected_product_id]
        for parts in self._production_data_cache.products_hash_table.get(selected_product_id).get('parts', []):
            product_ids.append(parts.split(':')[1])
        parts_id = self._production_data_cache.parts_hash_table.get(selected_product_id, None)
        if parts_id:
            product_ids.append(self._production_data_cache.parts_hash_table[selected_product_id])

        self._graphic_builder.highlight_graph_elements(target_elements=product_ids, reset=reset)

    @property
    def production_data_cache(self) -> ProductionLineDataCache:
        return self._production_data_cache

    @property
    def graphic_builder(self) -> GraphElementBuilder:
        return self._graphic_builder

    @property
    def window(self) -> Any:
        return self._window

    @property
    def fig(self) -> Any:
        return self._fig

    @property
    def ax(self) -> Any:
        return self._ax

    def tr(
            self,
            p: Point2,
    ) -> (Any, Any):
        if not p.x or not p.y:
            return None, None
        return datetime.datetime.fromtimestamp(float(p.x), tz=datetime.timezone.utc), p.y

    def trx(self, x: float) -> datetime:
        return self._transformer.trx(x)
