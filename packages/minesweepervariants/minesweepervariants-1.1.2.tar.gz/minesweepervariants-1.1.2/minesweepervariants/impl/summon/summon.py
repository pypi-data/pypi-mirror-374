#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2025/06/03 05:30
# @Author  : Wu_RH
# @FileName: summon.py
import threading
import time
from typing import Union, List

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar

from ...abs.Mrule import AbstractMinesClueRule
from ...abs.Rrule import AbstractClueRule
from ...abs.rule import AbstractRule
from ...utils.impl_obj import set_total, VALUE_QUESS, MINES_TAG
from .solver import solver_by_csp, solver_model, Switch
from ...utils.tool import get_random, get_logger

from ...abs.Lrule import MinesRules, AbstractMinesRule, Rule0R
from ...abs.board import AbstractBoard, AbstractPosition

from ..impl_obj import get_rule, get_board
from ...impl.rule.Mrule.sharp import RuleSharp as RuleMinesSharp
from ...impl.rule.Rrule.sharp import RuleSharp as RuleClueSharp

from minesweepervariants.config.config import PUZZLE_CONFIG

from ...utils.timer import timer

# ==== 获取默认值 ====
CONFIG = {}
CONFIG.update(PUZZLE_CONFIG)


class GenerateError(Exception):
    pass


class Summon:
    def __init__(
        self, size: tuple[int, int],
        total: int,
        rules: list[str],
        drop_r: bool = False,
        mask: str = "",
        dye: str = "",
        board: str = "Board1",
        vice_board: bool = False,
    ):
        """
        :param size: 题板的尺寸
        :param total: 雷总数
        :param rules: 单独的右线规则id
        :param dye: 染色规则
        :param board: 题板的实现类id
        :param vice_board: 启用删除副板
        """
        # summon初始化
        self.answer_board = None
        self.drop_r = drop_r
        self.logger = get_logger()
        self.answer_board_str = ""
        self.answer_board_code = None
        self.total = total
        self.vice_board = vice_board
        self.unseed = False

        # 题板初始化
        self.board = get_board(board)(size)

        clue_rules = []
        mines_rules = []
        mines_clue_rules = []

        if "R" not in rules:
            rules.append("R")

        rules_info = []
        for rule_id in rules:
            parts = rule_id.split(CONFIG["delimiter"], 1)
            rule_id = parts[0]
            data = parts[1] if len(parts) == 2 else None
            rule: AbstractRule = get_rule(rule_id)(board=self.board, data=data)
            rules_info.append((rule, data))
            if rule is None:
                self.logger.error("键入了一个未知的规则")
            elif isinstance(rule, AbstractClueRule):
                clue_rules.append(rule)
            elif isinstance(rule, AbstractMinesRule):
                mines_rules.append(rule)
            elif isinstance(rule, AbstractMinesClueRule):
                mines_clue_rules.append(rule)
            else:
                # 如果你不是左线不是中线也不是右线那你怎么混进来的?
                raise ValueError("Unknown Rule")

        for rule in clue_rules + mines_rules + mines_clue_rules:
            rule.combine(rules_info)

        # 清空列表来让他遍历所有规则名
        rules.clear()

        # 左线规则初始化
        self.mines_rules = MinesRules(mines_rules)
        for rule in mines_rules:
            if "R" in rule.name:
                continue
            rules.append(rule.get_name())

        # 中线规则初始化
        if len(mines_clue_rules) == 0:
            self.mines_clue_rule = get_rule("F")(board=self.board, data=None)
        elif len(mines_clue_rules) > 1:
            # 我什么时候写的F#?
            # 我不道啊
            self.mines_clue_rule = RuleMinesSharp(board=self.board, data=mines_clue_rules)
            rules.append("F#")
        else:
            self.mines_clue_rule = mines_clue_rules[0]
            rules.append(self.mines_clue_rule.get_name())

        # 右线规则初始化
        if len(clue_rules) == 0:
            if len(mines_clue_rules) == 0:
                self.clue_rule = get_rule("V")(board=self.board, data=None)
            else:
                self.clue_rule = get_rule("?")(board=self.board, data="")
        elif len(clue_rules) > 1:
            self.clue_rule = RuleClueSharp(board=self.board, data=clue_rules)
            rules.append("#")
        else:
            self.clue_rule = clue_rules[0]
            rules.append(self.clue_rule.get_name())

        if not rules:
            rules.append("V")

        # 掩码规则
        if mask:
            _board: AbstractBoard = self.board.clone()
            _board.dyed(mask[1:] if mask.startswith("&") else mask)
            for pos, is_dyed in _board(mode="dye"):
                if is_dyed: self.board.set_mask(pos)

        # 染色规则
        if dye:
            self.board.dyed(dye)

        # 雷总数初始化
        if total == -1:
            self.init_total()
        else:
            self.total = total
        set_total(total=self.total)

    def init_total(self):
        soft_conds = [-float("inf")]

        def soft_fn(total, diff=0):
            nonlocal soft_conds
            if soft_conds[0] > diff:
                return
            if soft_conds[0] != diff:
                soft_conds.clear()
            if len(soft_conds) == 0:
                soft_conds.append(diff)
            else:
                soft_conds[0] = diff
            soft_conds.append(total)

        self.board: AbstractBoard
        ub = sum([size[0] * size[1] for key in self.board.get_board_keys()
                  for size in [self.board.get_config(key, "size")]])
        info = {
            "size": {key: (size[0], size[1]) for key in self.board.get_board_keys()
                     for size in [self.board.get_config(key, "size")]},
            "interactive": [key for key in self.board.get_board_keys() if
                            self.board.get_config(key, "interactive")],
            "hard_fns": [],
            "soft_fn": soft_fn
        }
        for rule in self.mines_rules.rules + [self.clue_rule, self.mines_clue_rule]:
            rule.suggest_total(info)

        soft_conds = soft_conds[1:]

        soft_cond = sum(soft_conds) / len(soft_conds)

        att_index = 0
        symbol = True
        while att_index < 50:
            if symbol:
                n = round(soft_cond) - int(att_index / 2)
            else:
                n = round(soft_cond) + int(att_index / 2) + 1

            if n < 0:
                continue

            if len(info["hard_fns"]) == 0:
                self.total = n
                set_total(total=n)
                return

            model = cp_model.CpModel()

            total_var = model.NewIntVar(0, ub, "total")
            model.Add(total_var == n)

            for hard_fn in info["hard_fns"]:
                hard_fn(model, total_var)

            solver = cp_model.CpSolver()
            status = timer(solver.Solve)(model)

            if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
                self.total = n
                set_total(total=n)
                return

            att_index += 1
            symbol = not symbol

    def create_puzzle(self):
        if self.summon_board() is None:
            raise ValueError("生成失败 左线/雷数出现矛盾")
        board_bytes = self.board.encode()
        for rule in self.mines_rules.rules + [self.clue_rule, self.mines_clue_rule]:
            rule.init_clear(self.board)
        if self.dig_unique(self.board) is None:
            raise GenerateError
        self.logger.debug(board_bytes, end="\n\n")
        return self.board

    def summon_board(self):
        self.board.clear_board()
        if self.unseed:
            _board = self.random_fill(self.board, self.total)
        else:
            _board = self.fill_valid(self.board, self.total)
        if _board is None:
            return None
        [_board.set_value(pos, None) for pos, _ in _board("C")]
        _board = self.clue_rule.fill(_board)
        _board = self.mines_clue_rule.fill(_board)
        if any([_board.has("N", key=key)
                for key in self.board.get_board_keys()]):
            for rule in self.mines_rules.rules:
                rule.init_board(_board)
            self.answer_board_str = "\n" + _board.show_board()
            self.answer_board_code = _board.encode()
            self.answer_board = _board.clone()
        else:
            self.answer_board_str = "\n" + _board.show_board()
            self.answer_board_code = _board.encode()
            self.answer_board = _board.clone()
        self.logger.debug("题板生成完毕:\n" + _board.show_board())
        self.logger.debug(_board.encode())
        self.answer_board = _board
        self.board = _board.clone()
        return _board

    def random_fill(self, board, total):
        # if len(self.mines_rules.rules) == 1:
        #     return self.fill_valid(board, total)
        switch = Switch()
        random = get_random()
        model = board.get_model()
        for rule in self.mines_rules.rules + [
            self.mines_clue_rule, self.clue_rule
        ]:
            rule.create_constraints(board, switch)
        var_list = [v for _, v in board(mode="variable")]
        model.AddBoolAnd(switch.get_all_vars())
        __count = 0
        random_total = int(total * (2 ** (1 - len(self.mines_rules.rules))))
        while True:
            __count += 1
            print(f"正在随机放雷 正在尝试第{__count}次 (随机放置{random_total}颗雷)", end="\r", flush=True)
            _model = model.clone()
            model.AddBoolAnd(random.sample(var_list, random_total))
            status, solver = solver_model(model, True)
            print(f"第{__count}次求解完毕 status: {status}", end="\r", flush=True)
            if status:
                break
            if random_total <= 0:
                return None
            del model
            model = _model
            random_total = int(0.5 * random_total)
        for pos, var in board(mode="variable"):
            if solver.Value(var):
                board[pos] = MINES_TAG
            else:
                board[pos] = VALUE_QUESS
        print("\n\n", board)
        print(f"随机放雷完毕 共尝试了{__count}次 ", end="\n", flush=True)
        return board

    def fill_valid(self, board: 'AbstractBoard', total: int, model=None) -> Union[AbstractBoard, None]:
        random = get_random()
        history: list[tuple] = []
        if model is None:
            switch = Switch()
            model = board.get_model()
            for rule in self.mines_rules.rules + [
                self.mines_clue_rule, self.clue_rule
            ]:
                rule.create_constraints(board, switch)
            model.AddBoolAnd(switch.get_all_vars())
        positions = [pos for pos, _ in self.board("N")]
        random.shuffle(positions)
        for index in range(len(positions)):
            if total <= 0:
                break
            print(f"正在随机放雷"
                  f"  已放置雷数: {self.total - total}/{self.total}"
                  f"  总剩余位置: {index}/{len(positions)}   ",
                  end="\r", flush=True)
            pos = positions[index]
            _model = model.clone()
            _model.Add(board.get_variable(pos) == 0)
            code = board.encode()
            board[pos] = MINES_TAG
            model.Add(board.get_variable(pos) == 1)
            if len(self.mines_rules.rules) == 1:
                total -= 1
            elif solver_model(model):
                history.append((code, _model))
                total -= 1
            else:
                board: AbstractBoard = type(board)(code=code)
                board[pos] = VALUE_QUESS
                del model
                model = _model
        if solver_model(model):
            return board
        while history:
            code, model = history.pop()
            board = type(board)(code=code)
            board = self.fill_valid(board, total)
            if board is not None:
                return board
        return None

    def dig_unique(self, board: 'AbstractBoard'):
        # import sys
        # if sys.argv[1:2] == ["-s"]:
        #     return self._dig_unique(board)
        state = solver_by_csp(
            self.mines_rules,
            self.clue_rule,
            self.mines_clue_rule,
            board.clone(),
            drop_r=self.drop_r
        )
        if state == 0:
            self.logger.warn("题板无解 需要重新设计")
            self.logger.warn("warn board:\n" + board.show_board())
            return None
        if state == 2:
            self.logger.warn("题板多解 需要重新设计/+R")
            self.logger.warn("warn board:\n" + board.show_board())
            return None

        # 初始统计
        init_clues_count = len([None for _ in board('C')])
        init_mines_count = len([None for _ in board('F')])

        # 共享状态
        progress_info = {
            "idx": 0,
            "phase": 0,
            "running": True,
            "step": True,
            "start_time": time.time()
        }

        def progress_thread():
            def format_time(seconds):
                seconds = int(round(seconds))  # 四舍五入取整
                days, seconds = divmod(seconds, 86400)  # 1天=86400秒
                hours, seconds = divmod(seconds, 3600)  # 1小时=3600秒
                minutes, seconds = divmod(seconds, 60)  # 1分钟=60秒

                parts = []
                if days > 0:
                    parts.append(f"{days}d")
                if hours > 0 or days > 0:  # 如果有天，即使小时=0也要显示
                    parts.append(f"{hours:02d}")
                if minutes > 0 or hours > 0 or days > 0:  # 如果有更高单位，分钟必须显示
                    parts.append(f"{minutes:02d}")
                if (days + hours + minutes) > 0:
                    parts.append(f"{seconds:02d}")  # 秒始终显示
                else:
                    parts.append(f"{seconds}s")

                return ":".join(parts)

            while progress_info["running"]:

                _temp_a_number = len([None for _key in board.get_interactive_keys()
                                     for _, c in board('C', key=_key)
                                     if c != board.get_config(_key, "VALUE")])
                _temp_b_number = len([None for _key in board.get_interactive_keys()
                                     for _, c in board('F', key=_key)
                                     if c != board.get_config(_key, "MINES")])

                total_all = init_mines_count + init_clues_count + _temp_a_number + _temp_b_number

                # 题板所有位置计数
                total_blank = len([None for _ in board('N')])
                total_clue = len([None for _ in board('C')])
                total_flag = len([None for _ in board('F')])

                progress_info["step"] = True

                # 计算当前进度（示例，实际请根据逻辑调整）
                while progress_info["step"]:

                    elapsed = time.time() - progress_info["start_time"]

                    current_step = progress_info["idx"] + progress_info["phase"] * (init_mines_count + init_clues_count)

                    predicted_total = (elapsed / current_step * total_all) if current_step > 0 else 0

                    print(
                        f"总雷数:{self.total}/{total_blank}"
                        f"  线索:{_temp_a_number}/{total_clue}"
                        f"  雷线索:{_temp_b_number}/{total_flag}"
                        f"  进度:{current_step}/{total_all}"
                        f"  用时:{format_time(elapsed)}"
                        f"<{format_time(predicted_total)}"
                        f" ~ {format_time(predicted_total - elapsed)}   ",
                        end="\r", flush=True
                    )
                    time.sleep(0.2)

        # 启动进度线程
        thread = threading.Thread(target=progress_thread, daemon=True)
        thread.start()

        for phase, put_type in enumerate([True, False]):
            if not put_type:
                temp_a_number = len([None for _ in board('C')])
                temp_b_number = len([None for _ in board('F')])
                if (init_clues_count == temp_a_number and
                        init_mines_count == temp_b_number):
                    self.logger.warn("题板无法删除任何线索 提前退出")
                    progress_info["running"] = False
                    thread.join()
                    return None

            c_poses = [(i, t, key) for key in
                       [key for key in board.get_board_keys() if board.get_config(key, "interactive")]
                       for i, t in board("CF", mode="type", key=key)]

            get_random().shuffle(c_poses)

            for idx, (pos, pos_type, key) in enumerate(c_poses + [(None, "", "")]):
                progress_info["idx"] = idx
                progress_info["phase"] = phase
                progress_info["step"] = False

                if pos is None:
                    break
                object_put = None if put_type else board.get_config(
                    key, "VALUE" if pos_type == "C" else "MINES")

                if board.get_value(pos) == object_put:
                    continue

                self.logger.trace("\n" + board.show_board())
                clue = board.get_value(pos)
                board.set_value(pos, object_put)

                if solver_by_csp(
                        self.mines_rules, self.clue_rule, self.mines_clue_rule,
                        board.clone(), drop_r=self.drop_r, answer_board=self.answer_board
                ) == 1:
                    continue
                board.set_value(pos, clue)

        progress_info["running"] = False
        progress_info["step"] = False
        thread.join()
        print(board.show_board())  # 清空残留
        return board
