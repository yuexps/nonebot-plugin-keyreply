import json
import re
from pathlib import Path
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel


class ReplyRule(BaseModel):
    key: str
    reply: str
    match_type: Literal["exact", "fuzzy", "regex"] = "exact"
    group_id: str = "global"


class RuleManager:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self._rules: Dict[str, List[ReplyRule]] = {}
        self.load()

    @property
    def rules(self) -> List[ReplyRule]:
        """获取扁平化的所有规则列表"""
        all_rules = []
        for group_rules in self._rules.values():
            all_rules.extend(group_rules)
        return all_rules

    def load(self) -> None:
        """从本地文件加载规则字典"""
        if not self.data_path.exists():
            self._rules = {}
            return
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._rules = {}
                if isinstance(data, dict):
                    for group_id, items in data.items():
                        rules_list = []
                        for item in items:
                            item["group_id"] = group_id
                            rules_list.append(ReplyRule(**item))
                        self._rules[group_id] = rules_list
        except Exception:
            self._rules = {}

    def save(self) -> None:
        """保存规则字典到本地文件"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_path, "w", encoding="utf-8") as f:
                data_to_save = {}
                for group_id, rules in self._rules.items():
                    group_rules = []
                    for r in rules:
                        if hasattr(r, "model_dump"):
                            r_dict = r.model_dump()
                        else:
                            r_dict = r.dict()
                        r_dict.pop("group_id", None)
                        group_rules.append(r_dict)
                    data_to_save[group_id] = group_rules
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def add_rule(self, key: str, reply: str, match_type: Literal["exact", "fuzzy", "regex"], group_id: str) -> None:
        """添加或覆盖规则"""
        if group_id not in self._rules:
            self._rules[group_id] = []
        self._rules[group_id] = [r for r in self._rules[group_id] if r.key != key]
        self._rules[group_id].append(ReplyRule(key=key, reply=reply, match_type=match_type, group_id=group_id))
        self.save()

    def edit_rule(self, key: str, reply: str, group_id: str) -> bool:
        """修改规则，若不存在则返回 False"""
        if group_id in self._rules:
            for r in self._rules[group_id]:
                if r.key == key:
                    r.reply = reply
                    self.save()
                    return True
        return False

    def del_rule(self, key: str, group_id: str) -> bool:
        """删除指定规则，若不存在则返回 False"""
        if group_id not in self._rules:
            return False
        original_len = len(self._rules[group_id])
        self._rules[group_id] = [r for r in self._rules[group_id] if r.key != key]
        if len(self._rules[group_id]) < original_len:
            if not self._rules[group_id]:
                del self._rules[group_id]
            self.save()
            return True
        return False

    def get_rule(self, key: str, group_id: str) -> Optional[ReplyRule]:
        """获取特定的规则"""
        if group_id in self._rules:
            for r in self._rules[group_id]:
                if r.key == key:
                    return r
        return None

    def get_rules_for_group(self, group_id: str) -> List[ReplyRule]:
        """获取指定群/范围生效的规则"""
        return self._rules.get(group_id, [])

    def _match_rules(self, text: str, rules: List[ReplyRule]) -> Optional[ReplyRule]:
        """匹配规则列表"""
        for rule in rules:
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
                    continue
        return None

    def match(self, text: str, group_id: str) -> Optional[ReplyRule]:
        """匹配规则，群聊未中时回退全局"""
        matched = self._match_rules(text, self.get_rules_for_group(group_id))
        if matched:
            return matched
        if group_id != "global":
            return self._match_rules(text, self.get_rules_for_group("global"))
        return None

