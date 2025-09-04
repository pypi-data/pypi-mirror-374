#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/06/03 18:38
# @Author  : Wu_RH
# @FileName: Rrule.py

from abc import abstractmethod, ABC
from typing import TYPE_CHECKING, List, Dict

from .rule import AbstractRule, AbstractValue
from ..utils.image_create import get_text, get_image, get_dummy, get_col
from ..utils.web_template import Number

if TYPE_CHECKING:
    from minesweepervariants.abs.board import AbstractBoard, AbstractPosition


class AbstractClueRule(AbstractRule):
    """
    数字线索规则
    """

    @abstractmethod
    def fill(self, board: 'AbstractBoard') -> 'AbstractBoard':
        """
        填充所有None为规则线索对象
        :param board: 题板
        :return: 题板
        """
        ...


class AbstractClueValue(AbstractValue, ABC):
    """
    线索格数字对象类
    """

    def __repr__(self) -> str:
        """
        当前值在展示时候的显示字符串
        :return: 显示的字符串
        """
        return "?"

    def compose(self, board) -> Dict:
        """
        返回一个可渲染对象列表
        默认使用__repr__
        """
        return get_col(
            get_dummy(height=0.3),
            get_text(self.__repr__()),
            get_dummy(height=0.3),
        )

    def web_component(self, board) -> Dict:
        """
        返回一个可渲染对象列表
        默认使用__repr__
        """
        if "compose" in type(self).__dict__:
            return self.compose(board)
        return Number(self.__repr__())


# --------实例类-------- #


class ValueQuess(AbstractClueValue):
    """
    问号类(线索非雷)
    """

    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        super().__init__(pos)

    def __repr__(self):
        return "?"

    @classmethod
    def type(cls) -> bytes:
        return b"?"

    def code(self) -> bytes:
        return b""

    def high_light(self, board: 'AbstractBoard') -> List['AbstractPosition'] | None:
        return []


class ValueCross(AbstractClueValue):
    """
    副板的叉号
    """

    def __init__(self, pos: 'AbstractPosition', code: bytes = b''):
        super().__init__(pos)

    def __repr__(self):
        return "X"

    def web_component(self, board) -> Dict:
        return get_image("cross")

    def compose(self, board) -> Dict:
        return get_image("cross")

    @classmethod
    def type(cls) -> bytes:
        return b"X"

    def code(self) -> bytes:
        return b""
