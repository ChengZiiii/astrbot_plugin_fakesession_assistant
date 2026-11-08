"""消息解析器 — QQ号|昵称|内容 格式，\\| 切段，图片按占位符位置归段"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from astrbot.api import logger
from astrbot.api.message_components import Image, Plain

# 图片占位符（Unicode 私有区包裹，正文不可能出现）
IMG_TOKEN = "\ue000IMG{}\ue001"
_IMG_TOKEN_RE = re.compile("\ue000IMG(\\d+)\ue001")


@dataclass
class Segment:
    qq: str
    nickname: str | None = None
    timestamp: int | None = None
    text: str = ""
    images: list[str] = field(default_factory=list)
    at_users: list[str] = field(default_factory=list)


def _split_raw_text(raw: str) -> list[str]:
    return [p.strip() for p in raw.split("\\|") if p.strip()]


def _parse_segment(block: str) -> Segment | None:
    at_pattern = re.compile(r"@(\d{5,12})")
    at_users = at_pattern.findall(block)
    block_clean = at_pattern.sub("", block).strip()
    parts = block_clean.split("|")
    if not parts or not re.match(r"^\d{5,12}$", parts[0].strip()):
        return None

    seg = Segment(qq=parts[0].strip(), at_users=at_users)
    if len(parts) == 1:
        return seg
    if len(parts) == 2:
        seg.text = parts[1].strip()
        return seg

    # `QQ|文本|`（第三段为空）：视为 QQ|文本 的尾随分隔符，
    # 防止内容被吃成昵称、真文本落到空的第三段
    if len(parts) == 3 and not parts[2].strip():
        seg.text = parts[1].strip()
        return seg

    # len >= 3: QQ|nickname|text 或 QQ||text
    second = parts[1].strip()
    if second:
        seg.nickname = second
    seg.text = "|".join(parts[2:]).strip()
    return seg


def parse_message(event, raw_components: list | None = None) -> list[Segment]:
    """从组件流解析：图片以占位符嵌入文本流保位，按 \\| 切块后图片跟随所在块。

    占位符方案取代旧的 offset 换算：图片组件在文本流中的真实位置由
    \\ue000IMG<i>\\ue001 标记，切块后占位符落在哪个块，图片就归哪段——
    图文混排（图片夹在两段命令文本之间）时归属不再漂移。
    """
    comps = raw_components if raw_components is not None else event.message_obj.message

    raw_text = ""
    image_urls: list[str] = []
    for comp in comps:
        if isinstance(comp, Plain):
            raw_text += comp.text
        elif isinstance(comp, Image):
            url = getattr(comp, "url", "") or getattr(comp, "file", "")
            if url:
                raw_text += IMG_TOKEN.format(len(image_urls))
                image_urls.append(url)

    idx = raw_text.find("伪造消息")
    if idx == -1:
        return []
    raw_text = raw_text[idx + len("伪造消息"):]

    segments: list[Segment] = []
    orphan_images: list[str] = []  # 落在被丢弃块（如"伪造外表"的标题块）里的图片
    for block in _split_raw_text(raw_text):
        imgs = [image_urls[int(n)] for n in _IMG_TOKEN_RE.findall(block)]
        block = _IMG_TOKEN_RE.sub("", block)
        seg = _parse_segment(block)
        if seg is None:
            orphan_images.extend(imgs)
            continue
        seg.images.extend(orphan_images)
        orphan_images = []
        seg.images.extend(imgs)
        segments.append(seg)

    # 尾部剩余孤儿图片挂最后一段（如图片写在标题之后的写法）
    if orphan_images and segments:
        segments[-1].images.extend(orphan_images)

    logger.debug(
        f"[FakeSession] 解析: {len(segments)} 个有效段, {len(image_urls)} 张图片"
    )
    return segments
