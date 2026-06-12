<p align="center">
  <a href="https://adapter-onebot.netlify.app/"><img src="https://img.shields.io/badge/nonebot2-plugin-red.svg" alt="nonebot2"></a>
  <a href="https://pypi.org/project/nonebot-plugin-keyreply"><img src="https://img.shields.io/pypi/v/nonebot-plugin-keyreply.svg" alt="pypi"></a>
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
</p>

# nonebot-plugin-keyreply

基于 NoneBot2 的轻量级关键词自动回复插件。

## 特性

- **群聊隔离**：各群聊及私聊数据完全独立，互不干扰。
- **多种匹配**：支持 精确匹配（默认）、模糊匹配、正则匹配。
- **权限受控**：管理指令限超级用户（`SUPERUSER`）或群管理（`GROUP_ADMIN | GROUP_OWNER`）执行。

## 安装

推荐使用 `nb-cli` 安装：
```bash
nb plugin install nonebot-plugin-keyreply
```
<details>
<summary>或使用包管理器</summary>

```bash
pip install nonebot-plugin-keyreply
```
并在 `pyproject.toml` 或 `bot.py` 中加载插件：
```toml
plugins = ["nonebot_plugin_keyreply"]
```
</details>

## 指令说明

指令前缀默认为 `/reply`（实际取决于 `COMMAND_START` 配置）。

| 指令格式 | 参数说明 | 匹配范围参数 | 示例 |
| :--- | :--- | :--- | :--- |
| `/reply add <关键词> <回复>` | `-f` 模糊匹配<br>`-r` 正则匹配 | `-g` 全局词条<br>`-p` 私聊词条 | `/reply add 菜单 "群菜单内容"`<br>`/reply add -f -g 帮助 帮助文档`<br>`/reply add -r -p "hi\|hello" 你好` |
| `/reply edit <关键词> <新回复>` | - | `-g` 全局 / `-p` 私聊 | `/reply edit 菜单 "新菜单"` |
| `/reply del <关键词>` | - | `-g` 全局 / `-p` 私聊 | `/reply del 菜单` |
| `/reply list [关键词]` | - | `-g` 全局 / `-p` 私聊 | `/reply list`<br>`/reply list 菜单` |

> [!IMPORTANT]
> 添加、修改和删除全局（`-g`）与私聊（`-p`）规则仅限超级用户（`SUPERUSER`）执行，查询列表（`list`）不受此限制。
> 如果关键词或回复内容**包含空格**，请使用双引号包裹，例如：`/reply add "早上 好" "您好！"`
