import shlex
from nonebot import on_command, on_message, require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

from .rule_manager import RuleManager

__plugin_meta__ = PluginMetadata(
    name="KeyReply",
    description="基于 NoneBot2 的轻量级关键词自动回复插件",
    usage=(
        "管理指令：/reply\n"
        "1. 添加：/reply add [-f 模糊 | -r 正则] [-g 全局 | -p 私聊] <关键词> <回复内容>\n"
        "2. 修改：/reply edit [-g 全局 | -p 私聊] <关键词> <新回复内容>\n"
        "3. 删除：/reply del [-g 全局 | -p 私聊] <关键词>\n"
        "4. 列表/查看：/reply list [-g 全局 | -p 私聊] [关键词]"
    ),
    type="application",
    homepage="https://github.com/yuexps/nonebot-plugin-keyreply",
    supported_adapters={"~onebot.v11"},
)

rule_manager = RuleManager(store.get_plugin_data_file("rules.json"))

# 管理命令
reply_cmd = on_command(
    "reply",
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=5,
    block=True,
)


@reply_cmd.handle()
async def handle_reply(bot: Bot, event: MessageEvent, command_arg: Message = CommandArg()):
    # 提取参数文本
    args_str = command_arg.extract_plain_text().strip()
    if not args_str:
        await reply_cmd.finish(__plugin_meta__.usage)

    # 解析参数
    try:
        args = shlex.split(args_str)
    except ValueError as e:
        await reply_cmd.finish(f"参数解析错误：{str(e)}（请检查双引号是否闭合）")

    sub_cmd = args[0].lower()
    is_superuser = await SUPERUSER(bot, event)

    if sub_cmd == "add":
        match_type = "exact"
        is_global = False
        is_private = False
        clean_args = []
        for arg in args[1:]:
            if arg in ("-f", "--fuzzy"):
                match_type = "fuzzy"
            elif arg in ("-r", "--regex"):
                match_type = "regex"
            elif arg in ("-g", "--global"):
                is_global = True
            elif arg in ("-p", "--private"):
                is_private = True
            else:
                clean_args.append(arg)

        if len(clean_args) < 2:
            await reply_cmd.finish("格式错误：reply add [-f|-r] [-g|-p] <关键词> <回复内容>")

        if is_global and is_private:
            await reply_cmd.finish("格式错误：不能同时指定全局(-g)和私聊(-p)")

        if (is_global or is_private) and not is_superuser:
            await reply_cmd.finish("权限不足：仅超级用户有权配置全局/私聊词条")

        if is_global:
            group_id = "global"
        elif is_private:
            group_id = "private"
        else:
            group_id = str(event.group_id) if isinstance(event, GroupMessageEvent) else "private"

        key = clean_args[0]
        reply = " ".join(clean_args[1:])

        match_types = {"exact": "精确匹配", "fuzzy": "模糊匹配", "regex": "正则匹配"}
        rule_manager.add_rule(key, reply, match_type, group_id)
        scope_map = {"global": "全局", "private": "私聊"}
        scope = scope_map.get(group_id, f"群 {group_id}")
        await reply_cmd.finish(f"添加成功！[{scope}] 关键词「{key}」-> 「{reply}」[类型: {match_types.get(match_type, match_type)}]")

    elif sub_cmd == "edit":
        is_global = False
        is_private = False
        clean_args = []
        for arg in args[1:]:
            if arg in ("-g", "--global"):
                is_global = True
            elif arg in ("-p", "--private"):
                is_private = True
            else:
                clean_args.append(arg)

        if len(clean_args) < 2:
            await reply_cmd.finish("格式错误：reply edit [-g|-p] <关键词> <新回复内容>")

        if is_global and is_private:
            await reply_cmd.finish("格式错误：不能同时指定全局(-g)和私聊(-p)")

        if (is_global or is_private) and not is_superuser:
            await reply_cmd.finish("权限不足：仅超级用户有权配置全局/私聊词条")

        if is_global:
            group_id = "global"
        elif is_private:
            group_id = "private"
        else:
            group_id = str(event.group_id) if isinstance(event, GroupMessageEvent) else "private"

        key = clean_args[0]
        reply = " ".join(clean_args[1:])

        success = rule_manager.edit_rule(key, reply, group_id)
        if success:
            scope_map = {"global": "全局", "private": "私聊"}
            scope = scope_map.get(group_id, f"群 {group_id}")
            await reply_cmd.finish(f"修改成功！已覆盖 [{scope}] 关键词「{key}」的回复")
        else:
            await reply_cmd.finish(f"修改失败：未找到该范围内对应的关键词「{key}」")

    elif sub_cmd == "del":
        is_global = False
        is_private = False
        clean_args = []
        for arg in args[1:]:
            if arg in ("-g", "--global"):
                is_global = True
            elif arg in ("-p", "--private"):
                is_private = True
            else:
                clean_args.append(arg)

        if len(clean_args) < 1:
            await reply_cmd.finish("格式错误：reply del [-g|-p] <关键词>")

        if is_global and is_private:
            await reply_cmd.finish("格式错误：不能同时指定全局(-g)和私聊(-p)")

        if (is_global or is_private) and not is_superuser:
            await reply_cmd.finish("权限不足：仅超级用户有权配置全局/私聊词条")

        if is_global:
            group_id = "global"
        elif is_private:
            group_id = "private"
        else:
            group_id = str(event.group_id) if isinstance(event, GroupMessageEvent) else "private"
            
        key = clean_args[0]

        success = rule_manager.del_rule(key, group_id)
        if success:
            scope_map = {"global": "全局", "private": "私聊"}
            scope = scope_map.get(group_id, f"群 {group_id}")
            await reply_cmd.finish(f"删除成功！已移除 [{scope}] 关键词「{key}」")
        else:
            await reply_cmd.finish(f"删除失败：未找到该范围内对应的关键词「{key}」")

    elif sub_cmd == "list":
        is_global = False
        is_private = False
        clean_args = []
        for arg in args[1:]:
            if arg in ("-g", "--global"):
                is_global = True
            elif arg in ("-p", "--private"):
                is_private = True
            else:
                clean_args.append(arg)

        if is_global and is_private:
            await reply_cmd.finish("格式错误：不能同时指定全局(-g)和私聊(-p)")

        if is_global:
            group_id = "global"
        elif is_private:
            group_id = "private"
        else:
            group_id = str(event.group_id) if isinstance(event, GroupMessageEvent) else "private"

        if len(clean_args) == 0:
            if is_global or group_id == "global":
                rules = rule_manager.get_rules_for_group("global")
                if not rules:
                    await reply_cmd.finish("当前无生效的全局词条")
                lines = [f"- {r.key}" for r in rules]
                await reply_cmd.finish("当前生效的全局词条关键词列表：\n" + "\n".join(lines))
            elif is_private or group_id == "private":
                private_rules = rule_manager.get_rules_for_group("private")
                global_rules = rule_manager.get_rules_for_group("global")
                if not private_rules and not global_rules:
                    await reply_cmd.finish("当前无生效的私聊词条")

                msg_parts = []
                if private_rules:
                    msg_parts.append("【私聊词条】")
                    msg_parts.extend(f"- {r.key}" for r in private_rules)
                if global_rules:
                    if msg_parts:
                        msg_parts.append("")
                    msg_parts.append("【全局词条】")
                    msg_parts.extend(f"- {r.key}" for r in global_rules)

                await reply_cmd.finish("当前生效的词条关键词列表：\n" + "\n".join(msg_parts))
            else:
                group_rules = rule_manager.get_rules_for_group(group_id)
                global_rules = rule_manager.get_rules_for_group("global")
                if not group_rules and not global_rules:
                    await reply_cmd.finish("当前无生效的词条")

                msg_parts = []
                if group_rules:
                    msg_parts.append("【本群词条】")
                    msg_parts.extend(f"- {r.key}" for r in group_rules)
                if global_rules:
                    if msg_parts:
                        msg_parts.append("")
                    msg_parts.append("【全局词条】")
                    msg_parts.extend(f"- {r.key}" for r in global_rules)

                await reply_cmd.finish("当前生效的词条关键词列表：\n" + "\n".join(msg_parts))
        else:
            # 查询指定关键词
            key = clean_args[0]
            rule = rule_manager.get_rule(key, group_id)
            if not rule and group_id != "global":
                # 在当前上下文没找到时，也去全局找一下
                rule = rule_manager.get_rule(key, "global")

            if rule:
                scope_map = {"global": "全局", "private": "私聊"}
                scope = scope_map.get(rule.group_id, f"群 {rule.group_id}")
                match_types = {"exact": "精确匹配", "fuzzy": "模糊匹配", "regex": "正则匹配"}
                reply_text = (
                    f"词条信息：\n"
                    f"关键词：{rule.key}\n"
                    f"回复内容：{rule.reply}\n"
                    f"匹配类型：{match_types.get(rule.match_type, rule.match_type)}\n"
                    f"生效范围：{scope}"
                )
                await reply_cmd.finish(reply_text)
            else:
                await reply_cmd.finish(f"未找到对应的关键词「{key}」")
    else:
        await reply_cmd.finish(f"未知子命令：{sub_cmd}\n{__plugin_meta__.usage}")


# 自动回复监听器
message_reply = on_message(priority=99, block=False)


@message_reply.handle()
async def handle_message(bot: Bot, event: MessageEvent):
    text = event.get_plaintext().strip()
    if not text:
        return

    group_id = str(event.group_id) if isinstance(event, GroupMessageEvent) else "private"
    matched = rule_manager.match(text, group_id)
    if matched:
        await message_reply.send(message=matched.reply)
