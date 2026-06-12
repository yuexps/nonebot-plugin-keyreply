# KeyReply 插件

Nonebot2 根据关键词自动回复设定词条的插件。

## 安装

### 使用 nb-cli 安装 (推荐)
在你的 NoneBot 项目根目录下运行：
```bash
nb plugin install nonebot-plugin-keyreply
```

<details>
<summary><b>使用包管理器安装</b></summary>

根据你使用的包管理器，在 NoneBot 项目中运行：

* **pip**:
  ```bash
  pip install nonebot-plugin-keyreply
  ```
* **pdm**:
  ```bash
  pdm add nonebot-plugin-keyreply
  ```
* **poetry**:
  ```bash
  poetry add nonebot-plugin-keyreply
  ```

随后在项目的配置文件中（如 `pyproject.toml` 的 `plugins` 列表中）添加：
```toml
plugins = ["nonebot_plugin_keyreply"]
```
</details>

## 核心特性

- **群聊隔离**：群聊自动回复仅匹配当前群配置的专属词条，各群数据完全隔离，不互相干扰。
- **多种匹配模式**：支持精确匹配（默认）、模糊匹配（包含匹配）以及正则表达式匹配。
- **管理权限受控**：词条的添加、修改和删除指令仅限超级用户（`SUPERUSER`）或群管理员/群主（`GROUP_ADMIN | GROUP_OWNER`）执行。

## 指令说明

所有指令前缀默认为 `/reply`（实际前缀取决于您的 Nonebot 配置文件中的 `COMMAND_START` 设定）。

### 1. 添加词条
* **指令格式**：`/reply add [-f|-r] [-g] <关键词> <回复内容>`
* **参数说明**：
  - `-f` / `--fuzzy`：设置为模糊匹配（即消息中包含该关键词即可触发回复）。
  - `-r` / `--regex`：设置为正则表达式匹配（消息内容符合该正则表达式即可触发回复）。
  - `-g` / `--global`：设置为全局词条（仅超级用户可配置）。若在群聊中不加此参数，词条将仅在当前群生效；若在私聊中配置，默认即为全局生效。
* **双引号规范**：
  - 如果关键词或回复内容**不含空格**，直接以空格分隔即可：  
    `/reply add 测试 收到`
  - 如果关键词或回复内容中**包含空格**，请使用双引号包裹：  
    `/reply add "早上 好" "您好！今天也是元气满满的一天！"`

### 2. 修改词条（覆盖）
* **指令格式**：`/reply edit [-g] <关键词> <新回复内容>`
* **说明**：覆盖修改指定关键词的回复内容。

### 3. 删除词条
* **指令格式**：`/reply del [-g] <关键词>`
* **说明**：删除指定关键词的回复规则。

### 4. 列表与详情查询
* **指令格式**：
  - `/reply list [-g]`：列出当前生效的所有词条关键词列表。
  - `/reply list [-g] <关键词>`：查看指定关键词的匹配规则、具体回复内容与生效范围等详情。

---

## 插件配置项

您可以在 Nonebot2 的 `.env.*` 配置文件中添加以下配置：

```env
# 词条规则保存的文件路径（相对于项目根目录）
KEYREPLY_DATA_PATH="data/keyreply/rules.json"
```
