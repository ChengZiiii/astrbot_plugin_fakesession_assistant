# Changelog

本项目的更改记录在此文件。

All notable changes to this project are documented in this file.

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)；
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2-fork.1] - 2026-11-09

### 修复

- 图片来源形态自适应：AstrBot 4.x 的 preprocess 阶段会把收到的图片下载到本地，并把 Image 组件的 `url`/`file` 改写成本地路径（或 `file://` URI），导致 `/伪造消息` 附带图片时报 `not a valid url`。现在按来源形态分发：http(s) URL 走 `Image.fromURL`，本地路径/`file://` URI 走 `Image.fromFileSystem`（bot 与协议端同机，本地路径直接可用）。

### Fixed

- Image source-shape adaptation: AstrBot 4.x's preprocess stage rewrites `Image` components' `url`/`file` to local paths after downloading, breaking `/伪造消息` with an attached image (`not a valid url`). URLs now go through `Image.fromURL`, local paths / `file://` URIs through `Image.fromFileSystem`.

> 本仓库为上游 [OMSociety/astrbot_plugin_fakesession_assistant](https://github.com/OMSociety/astrbot_plugin_fakesession_assistant) 的 fork，由 ChengZiiii 维护，用于自部署环境（AstrBot 4.x + NapCat/SnowLuma 同机部署）的适配修复。

## [1.1.2] - 2026-09-25

### 修复

- 合并转发解析：末尾的兜底图片分配不再把已归属的图片重复追加一份。

### Fixed

- Merged-forward parsing: the trailing fallback image assignment no longer appends a duplicate copy of an image that has already been assigned.

## [1.1.1] - 2026-09-13

### 新增

- 三条命令新增英文别名：`/fake-message`（伪造消息）、`/fake-appearance`（伪造外表）、`/fake-help`（伪造帮助），`/伪造帮助` 输出中同步列出；中文命令保持不变。

## [1.1.0] - 2026-09-13

### 新增

- **WebUI 四语本地化**：新增 `zh-CN` / `en-US` / `ru-RU` / `ja-JP` 四份 i18n 文件（`.astrbot-plugin/i18n/`），插件名与简介文案在四种界面语言下均正确显示（本插件无配置 schema，仅 metadata 段）。
- README 新增多语言版本（English / Русский / 日本語），顶部提供语言导航。

## [1.0.2] - 2026-09-07

### 修复

- 修复图片紧跟「伪造消息」命令词时被丢弃（不再分配到任何发言段）的解析边角问题。
- 移除已停止服务的外部昵称 API 兜底（实测返回"本站所有API服务已停止"，此前每次昵称未知都会白打一次请求后仍回退 QQ 号显示），昵称查询保留 OneBot 通道。
- 修复 OneBot 昵称查询恒失效的问题：`call_action` 返回的是已解包的数据字典，此前按 {status, retcode, data} 信封结构判断导致永远取不到昵称（该缺陷自上游版本即存在）。

### 变更

- 移除未再使用的 aiohttp 依赖声明。

## [1.0.1] - 2026-09-06

### 新增

- @ 提及生效：内容中的 `@QQ号` 现在转换为真正的 @ 提及（此前会被静默删除）。

### 修复

- 修复私聊等免前缀场景下 `/伪造消息`、`/伪造外表` 只返回帮助文本的问题。

### 变更

- 移除「启用 LLM 工具」配置开关（该开关实际从未生效），工具启停统一走框架自带的插件 LLM 工具管理。
