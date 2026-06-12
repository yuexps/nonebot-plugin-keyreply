import json
import re
from pathlib import Path
from typing import List, Literal, Optional
from pydantic import BaseModel


class ReplyRule(BaseModel):
    key: str
    reply: str
    match_type: Literal["exact", "fuzzy", "regex"] = "exact"
    group_id: str = "global"


class RuleManager:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.rules: List[ReplyRule] = []
        self.load()

    def load(self) -> None:
        """从本地文件加载规则列表"""
        if not self.data_path.exists():
            self.rules = []
            return
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.rules = [ReplyRule(**item) for item in data]
        except Exception:
            self.rules = []

    def save(self) -> None:
        """保存规则列表到本地文件"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_path, "w", encoding="utf-8") as f:
                # 兼容 Pydantic v1 & v2
                rules_data = []
                for r in self.rules:
                    if hasattr(r, "model_dump"):
                        rules_data.append(r.model_dump())
                    else:
                        rules_data.append(r.dict())
                json.dump(rules_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add_rule(self, key: str, reply: str, match_type: Literal["exact", "fuzzy", "regex"], group_id: str) -> None:
        """添加或覆盖规则"""
        # 移除已有的同群同关键词规则
        self.rules = [r for r in self.rules if not (r.key == key and r.group_id == group_id)]
        self.rules.append(ReplyRule(key=key, reply=reply, match_type=match_type, group_id=group_id))
        self.save()

    def edit_rule(self, key: str, reply: str, group_id: str) -> bool:
        """修改规则，若不存在则返回 False"""
        for r in self.rules:
            if r.key == key and r.group_id == group_id:
                r.reply = reply
                self.save()
                return True
        return False

    def del_rule(self, key: str, group_id: str) -> bool:
        """删除指定规则，若不存在则返回 False"""
        original_len = len(self.rules)
        self.rules = [r for r in self.rules if not (r.key == key and r.group_id == group_id)]
        if len(self.rules) < original_len:
            self.save()
            return True
        return False

    def get_rule(self, key: str, group_id: str) -> Optional[ReplyRule]:
        """获取特定的规则"""
        for r in self.rules:
            if r.key == key and r.group_id == group_id:
                return r
        return None

    def get_rules_for_group(self, group_id: str) -> List[ReplyRule]:
        """获取指定群/范围生效的规则"""
        return [r for r in self.rules if r.group_id == group_id]

    def match(self, text: str, group_id: str) -> Optional[ReplyRule]:
        """根据输入文本匹配首个符合条件的规则"""
        active_rules = self.get_rules_for_group(group_id)
        for rule in active_rules:
            if rule.match_type == "exact":
                if text == rule.key:
                    return rule
            elif rule.match_type == "fuzzy":
                if rule.key in text:
                    return rule
            elif rule.match_type == "regex":
                try:
                    if re.search(rule.key, text):
                        return rule
                except re.error:
                    # 忽略无效的正则表达式
                    continue
        return None
