#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2025.09.04 00:00:00                  #
# ================================================== #

import json
import os
import re
import gc
from dataclasses import dataclass, field

from datetime import datetime
from typing import Optional, List, Any
from time import monotonic
from io import StringIO

from pygpt_net.core.render.base import BaseRenderer
from pygpt_net.core.text.utils import has_unclosed_code_tag
from pygpt_net.item.ctx import CtxItem, CtxMeta
from pygpt_net.ui.widget.textarea.input import ChatInput
from pygpt_net.utils import trans
from pygpt_net.core.tabs.tab import Tab

from .body import Body
from .helpers import Helpers
from .parser import Parser
from .pid import PidData

from pygpt_net.core.events import RenderEvent


class Renderer(BaseRenderer):

    NODE_INPUT = 0
    NODE_OUTPUT = 1
    ENDINGS_CODE = (
        "</code></pre></div>",
        "</code></pre></div><br/>",
        "</code></pre></div><br>"
    )
    ENDINGS_LIST = (
        "</ul>",
        "</ol>",
        "</li>"
    )
    RE_AMP_LT_GT = re.compile(r'&amp;(lt|gt);')

    @dataclass(slots=True)
    class _AppendBuffer:
        """Small, allocation-friendly buffer for throttled appends."""
        _buf: StringIO = field(default_factory=StringIO, repr=False)
        _size: int = 0

        def append(self, s: str) -> None:
            if not s:
                return
            self._buf.write(s)
            self._size += len(s)

        def is_empty(self) -> bool:
            return self._size == 0

        def get_and_clear(self) -> str:
            """Return content and replace underlying buffer to release memory eagerly."""
            if self._size == 0:
                return ""
            data = self._buf.getvalue()
            old = self._buf
            # Replace the internal buffer instance to drop capacity immediately
            self._buf = StringIO()
            self._size = 0
            try:
                old.close()
            except Exception:
                pass
            return data

        def clear(self) -> None:
            """Clear content and drop buffer capacity."""
            old = self._buf
            self._buf = StringIO()
            self._size = 0
            try:
                old.close()
            except Exception:
                pass

    def __init__(self, window=None):
        super(Renderer, self).__init__(window)
        """
        WebEngine renderer

        :param window: Window instance
        """
        self.window = window
        self.body = Body(window)
        self.helpers = Helpers(window)
        self.parser = Parser(window)
        self.pids = {}
        self.prev_chunk_replace = False
        self.prev_chunk_newline = False

        app_path = self.window.core.config.get_app_path() if self.window else ""
        self._icon_expand = os.path.join(app_path, "data", "icons", "expand.svg")
        self._icon_sync = os.path.join(app_path, "data", "icons", "sync.svg")
        self._file_prefix = 'file:///' if self.window and self.window.core.platforms.is_windows() else 'file://'

        self._thr = {}
        self._throttle_interval = 0.03  # 30 ms delay

    def prepare(self):
        """
        Prepare renderer
        """
        self.pids = {}

    def on_load(self, meta: CtxMeta = None):
        """
        On load (meta) event

        :param meta: context meta
        """
        node = self.get_output_node(meta)
        node.set_meta(meta)
        self.reset(meta)
        self.parser.reset()
        try:
            node.page().runJavaScript("if (typeof window.prepare !== 'undefined') prepare();")
        except Exception:
            pass

    def on_page_loaded(
            self,
            meta: Optional[CtxMeta] = None,
            tab: Optional[Tab] = None
    ):
        """
        On page loaded callback from WebEngine widget

        :param meta: context meta
        :param tab: Tab
        """
        if meta is None or tab is None:
            return
        pid = tab.pid
        if pid is None or pid not in self.pids:
            return

        self.pids[pid].loaded = True
        if self.pids[pid].html != "" and not self.pids[pid].use_buffer:
            self.clear_chunks_input(pid)
            self.clear_chunks_output(pid)
            self.clear_nodes(pid)
            self.append(pid, self.pids[pid].html, flush=True)
            self.pids[pid].html = ""

    def get_pid(self, meta: CtxMeta):
        """
        Get PID for context meta

        :param meta: context PID
        """
        return self.window.core.ctx.output.get_pid(meta)

    def get_or_create_pid(self, meta: CtxMeta):
        """
        Get PID for context meta and create PID data (if not exists)

        :param meta: context PID
        """
        if meta is not None:
            pid = self.get_pid(meta)
            if pid not in self.pids:
                self.pid_create(pid, meta)
            return pid

    def pid_create(
            self,
            pid: Optional[int],
            meta: CtxMeta
    ):
        """
        Create PID data

        :param pid: PID
        :param meta: context meta
        """
        if pid is not None:
            self.pids[pid] = PidData(pid, meta)

    def get_pid_data(self, pid: int):
        """
        Get PID data for given PID

        :param pid: PID
        """
        if pid in self.pids:
            return self.pids[pid]

    def init(self, pid: Optional[int]):
        """
        Initialize renderer

        :param pid: context PID
        """
        if pid in self.pids and not self.pids[pid].initialized:
            self.flush(pid)
            self.pids[pid].initialized = True
        else:
            self.clear_chunks(pid)

    def to_json(self, data: Any) -> str:
        """
        Convert data to JSON object

        :param data: data to convert
        :return: JSON object or None
        """
        return json.dumps(data, ensure_ascii=False, separators=(',', ':'))

    def state_changed(
            self,
            state: str,
            meta: CtxMeta,
    ):
        """
        On kernel state changed event

        :param state: state name
        :param meta: context meta
        """
        if state == RenderEvent.STATE_BUSY:
            if meta:
                pid = self.get_pid(meta)
                if pid is not None:
                    node = self.get_output_node_by_pid(pid)
                    try:
                        node.page().runJavaScript(
                            "if (typeof window.showLoading !== 'undefined') showLoading();"
                        )
                    except Exception as e:
                        pass

        elif state == RenderEvent.STATE_IDLE:
            for pid in self.pids:
                node = self.get_output_node_by_pid(pid)
                if node is not None:
                    try:
                        node.page().runJavaScript(
                            "if (typeof window.hideLoading !== 'undefined') hideLoading();"
                        )
                    except Exception as e:
                        pass

        elif state == RenderEvent.STATE_ERROR:
            for pid in self.pids:
                node = self.get_output_node_by_pid(pid)
                if node is not None:
                    try:
                        node.page().runJavaScript(
                            "if (typeof window.hideLoading !== 'undefined') hideLoading();"
                        )
                    except Exception as e:
                        pass

    def begin(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            stream: bool = False
    ):
        """
        Render begin

        :param meta: context meta
        :param ctx: context item
        :param stream: True if it is a stream
        """
        pid = self.get_or_create_pid(meta)
        self.init(pid)
        self.reset_names(meta)
        self.tool_output_end()
        self.prev_chunk_replace = False

    def end(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            stream: bool = False
    ):
        """
        Render end

        :param meta: context meta
        :param ctx: context item
        :param stream: True if it is a stream
        """
        pid = self.get_or_create_pid(meta)
        if pid is None:
            return
        if self.pids[pid].item is not None and stream:
            self.append_context_item(meta, self.pids[pid].item)
            self.pids[pid].item = None
        else:
            self.reload()
        self.pids[pid].clear()

    def end_extra(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            stream: bool = False
    ):
        """
        Render end extra

        :param meta: context meta
        :param ctx: context item
        :param stream: True if it is a stream
        """
        self.to_end(ctx)

    def stream_begin(
            self,
            meta: CtxMeta,
            ctx: CtxItem
    ):
        """
        Render stream begin

        :param meta: context meta
        :param ctx: context item
        """
        self.prev_chunk_replace = False
        try:
            self.get_output_node(meta).page().runJavaScript("beginStream();")
        except Exception:
            pass

    def stream_end(
            self,
            meta: CtxMeta,
            ctx: CtxItem
    ):
        """
        Render stream end

        :param meta: context meta
        :param ctx: context item
        """
        self.prev_chunk_replace = False
        pid = self.get_or_create_pid(meta)
        if pid is None:
            return

        self._throttle_emit(pid, force=True)
        self._throttle_reset(pid)
        if self.window.controller.agent.legacy.enabled():
            if self.pids[pid].item is not None:
                self.append_context_item(meta, self.pids[pid].item)
                self.pids[pid].item = None
        self.pids[pid].clear()
        try:
            self.get_output_node(meta).page().runJavaScript("endStream();")
        except Exception:
            pass

        # release strings
        gc.collect()

    def append_context(
            self,
            meta: CtxMeta,
            items: List[CtxItem],
            clear: bool = True
    ):
        """
        Append all context items to output

        :param meta: Context meta
        :param items: context items
        :param clear: True if clear all output before append
        """
        self.tool_output_end()
        self.append_context_all(
            meta,
            items,
            clear=clear,
        )

    def append_context_partial(
            self,
            meta: CtxMeta,
            items: List[CtxItem],
            clear: bool = True
    ):
        """
        Append all context items to output (part by part)

        :param meta: Context meta
        :param items: context items
        :param clear: True if clear all output before append
        """
        if len(items) == 0:
            if meta is None:
                return

        pid = self.get_or_create_pid(meta)
        self.init(pid)

        if clear:
            self.reset(meta)

        self.pids[pid].use_buffer = True
        self.pids[pid].html = ""
        prev_ctx = None
        next_item = None
        total = len(items)
        for i, item in enumerate(items):
            self.update_names(meta, item)
            item.idx = i
            if i == 0:
                item.first = True
            next_item = items[i + 1] if i + 1 < total else None
            self.append_context_item(
                meta,
                item,
                prev_ctx=prev_ctx,
                next_ctx=next_item,
            )
            prev_ctx = item

        prev_ctx = None
        next_item = None
        self.pids[pid].use_buffer = False
        if self.pids[pid].html != "":
            self.append(
                pid,
                self.pids[pid].html,
                flush=True,
            )
        self.parser.reset()

    def append_context_all(
            self,
            meta: CtxMeta,
            items: List[CtxItem],
            clear: bool = True
    ):
        """
        Append all context items to output (whole context at once)

        :param meta: Context meta
        :param items: context items
        :param clear: True if clear all output before append
        """
        if len(items) == 0:
            if meta is None:
                return

        pid = self.get_or_create_pid(meta)
        self.init(pid)

        if clear:
            self.reset(meta, clear_nodes=False)  # nodes will be cleared later, in flush_output()

        self.pids[pid].use_buffer = True
        self.pids[pid].html = ""
        prev_ctx = None
        next_ctx = None
        total = len(items)
        html_parts = []
        for i, item in enumerate(items):
            self.update_names(meta, item)
            item.idx = i
            if i == 0:
                item.first = True
            next_ctx = items[i + 1] if i + 1 < total else None

            # ignore hidden items
            if item.hidden:
                prev_ctx = item
                continue

            # input node
            data = self.prepare_input(meta, item, flush=False)
            if data:
                html = self.prepare_node(
                    meta=meta,
                    ctx=item,
                    html=data,
                    type=self.NODE_INPUT,
                    prev_ctx=prev_ctx,
                    next_ctx=next_ctx,
                )
                if html:
                    html_parts.append(html)

            # output node
            data = self.prepare_output(
                meta,
                item,
                flush=False,
                prev_ctx=prev_ctx,
                next_ctx=next_ctx,
            )
            if data:
                html = self.prepare_node(
                    meta=meta,
                    ctx=item,
                    html=data,
                    type=self.NODE_OUTPUT,
                    prev_ctx=prev_ctx,
                    next_ctx=next_ctx,
                )
                if html:
                    html_parts.append(html)

            prev_ctx = item

        # flush all nodes at once
        if html_parts:
            self.append(
                pid,
                "".join(html_parts),
                replace=True,
            )

        html_parts.clear()
        html_parts = None
        prev_ctx = None
        next_ctx = None
        self.pids[pid].use_buffer = False
        if self.pids[pid].html != "":
            self.append(
                pid,
                self.pids[pid].html,
                flush=True,
                replace=True,
            )
        self.parser.reset()

    def prepare_input(
            self, meta: CtxMeta,
            ctx: CtxItem,
            flush: bool = True,
            append: bool = False
    ) -> Optional[str]:
        """
        Prepare text input

        :param meta: context meta
        :param ctx: context item
        :param flush: flush HTML
        :param append: True if force append node
        :return: Prepared input text or None if internal or empty input
        """
        if ctx.input is None or ctx.input == "":
            return

        text = ctx.input
        if isinstance(ctx.extra, dict) and "sub_reply" in ctx.extra and ctx.extra["sub_reply"]:
            try:
                json_encoded = json.loads(text)
                if isinstance(json_encoded, dict):
                    if "expert_id" in json_encoded and "result" in json_encoded:
                        tmp = "@" + str(ctx.input_name) + ":\n\n" + str(json_encoded["result"])
                        text = tmp
            except json.JSONDecodeError:
                pass

        if ctx.internal \
                and not ctx.first \
                and not ctx.input.strip().startswith("user: ") \
                and not ctx.input.strip().startswith("@"):
            return
        else:
            if ctx.internal and ctx.input.startswith("user: "):
                text = re.sub(r'^user: ', '> ', ctx.input)

        return text.strip()

    def append_input(
            self, meta: CtxMeta,
            ctx: CtxItem,
            flush: bool = True,
            append: bool = False
    ):
        """
        Append text input to output

        :param meta: context meta
        :param ctx: context item
        :param flush: flush HTML
        :param append: True if force append node
        """
        self.tool_output_end()
        pid = self.get_or_create_pid(meta)
        if not flush:
            self.clear_chunks_input(pid)

        self.update_names(meta, ctx)
        text = self.prepare_input(meta, ctx, flush, append)
        if text:
            if flush:
                if self.is_stream() and not append:
                    content = self.prepare_node(meta, ctx, text, self.NODE_INPUT)
                    self.append_chunk_input(meta, ctx, content, begin=False)
                    return
            self.append_node(
                meta=meta,
                ctx=ctx,
                html=text,
                type=self.NODE_INPUT,
            )

    def prepare_output(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            flush: bool = True,
            prev_ctx: Optional[CtxItem] = None,
            next_ctx: Optional[CtxItem] = None
    ) -> Optional[str]:
        """
        Prepare text output

        :param meta: context meta
        :param ctx: context item
        :param flush: flush HTML
        :param prev_ctx: previous context
        :param next_ctx: next context
        :return: Prepared output text or None if empty output
        """
        output = ctx.output
        if isinstance(ctx.extra, dict) and ctx.extra.get("output"):
            if self.window.core.config.get("agent.output.render.all", False):
                output = ctx.output  # full agent output
            else:
                output = ctx.extra["output"]  # final output only
        else:
            if not output:
                return
        return output.strip()

    def append_output(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            flush: bool = True,
            prev_ctx: Optional[CtxItem] = None,
            next_ctx: Optional[CtxItem] = None
    ):
        """
        Append text output to output

        :param meta: context meta
        :param ctx: context item
        :param flush: flush HTML
        :param prev_ctx: previous context
        :param next_ctx: next context
        """
        self.tool_output_end()
        output = self.prepare_output(
            meta=meta,
            ctx=ctx,
            flush=flush,
            prev_ctx=prev_ctx,
            next_ctx=next_ctx,
        )
        if output:
            self.append_node(
                meta=meta,
                ctx=ctx,
                html=output,
                type=self.NODE_OUTPUT,
                prev_ctx=prev_ctx,
                next_ctx=next_ctx,
            )

    def append_chunk(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            text_chunk: str,
            begin: bool = False
    ):
        """
        Append output chunk to output

        :param meta: context meta
        :param ctx: context item
        :param text_chunk: text chunk
        :param begin: if it is the beginning of the text
        """
        pid = self.get_or_create_pid(meta)
        pctx = self.pids[pid]
        pctx.item = ctx

        if not text_chunk:
            if begin:
                pctx.clear()
                self._throttle_emit(pid, force=True)
                self._throttle_reset(pid)
            return

        if begin:
            # Prepare name header once per streaming session
            pctx.header = self.get_name_header(ctx, stream=True)
            self.update_names(meta, ctx)

        name_header_str = pctx.header
        text_chunk = text_chunk if isinstance(text_chunk, str) else str(text_chunk)
        # Escape angle brackets only if present to avoid unnecessary allocations
        if ('<' in text_chunk) or ('>' in text_chunk):
            text_chunk = text_chunk.translate({ord('<'): '&lt;', ord('>'): '&gt;'})

        if begin:
            if self.is_debug():
                debug = self.append_debug(ctx, pid, "stream")
                if debug:
                    text_chunk = debug + text_chunk
            self._throttle_emit(pid, force=True)
            self._throttle_reset(pid)
            pctx.clear()
            pctx.is_cmd = False
            self.clear_chunks_output(pid)
            self.prev_chunk_replace = False

        # Append to the logical buffer (owned by pid)
        pctx.append_buffer(text_chunk)
        buffer = pctx.buffer

        # Cheap detection of open code fence without full parse
        open_code = has_unclosed_code_tag(buffer)

        # Newline/flow state
        is_n = "\n" in text_chunk
        is_newline = is_n or buffer.endswith("\n") or open_code
        force_replace = self.prev_chunk_newline
        self.prev_chunk_newline = bool(is_n)

        replace = False
        if is_newline or force_replace:
            replace = True
            # Do not replace for an open code block unless a newline arrived
            if open_code and not is_n:
                replace = False

        thr = self._throttle_get(pid)
        html = None

        # Only parse when required:
        # - a replace is needed now, or
        # - a replace is pending in the throttle and must be refreshed, or
        # - rarely: we must detect list termination without a newline
        need_parse_for_pending_replace = (thr["op"] == 1)
        need_parse_for_list = False

        if not replace:
            # Very rare case: list closing without newline. Check on a short tail only.
            # This keeps behavior intact while avoiding full-buffer parse on every chunk.
            tail = buffer[-4096:]
            if tail:
                tail_to_parse = f"{tail}\n```" if open_code else tail
                tail_html = self.parser.parse(tail_to_parse)
                need_parse_for_list = tail_html.endswith(self.ENDINGS_LIST)
                # Tail string is short and will be collected promptly
                del tail_html
            if need_parse_for_list:
                replace = True

        if replace or need_parse_for_pending_replace:
            buffer_to_parse = f"{buffer}\n```" if open_code else buffer
            html = self.parser.parse(buffer_to_parse)
            # Help the GC by breaking the reference as soon as possible
            del buffer_to_parse

        is_code_block = open_code

        # Adjust output chunk formatting based on block type
        if not is_code_block:
            if is_n:
                # Convert text newlines to <br/> in non-code context
                text_chunk = text_chunk.replace("\n", "<br/>")
        else:
            # When previous operation replaced content and this chunk closes the fence,
            # prepend a newline so the final code block renders correctly.
            if self.prev_chunk_replace and (is_code_block and not has_unclosed_code_tag(text_chunk)):
                text_chunk = "\n" + text_chunk

        # Update replace flag for next iteration AFTER formatting decisions
        self.prev_chunk_replace = replace

        if begin:
            try:
                self.get_output_node(meta).page().runJavaScript("hideLoading();")
            except Exception:
                pass

        # Queue throttled emission; HTML is only provided when it is really needed
        self._throttle_queue(
            pid=pid,
            name=name_header_str or "",
            html=html if html is not None else "",
            text_chunk=text_chunk,
            replace=replace,
            is_code_block=is_code_block,
        )
        # Explicitly drop local ref to large html string as early as possible
        html = None

        # Emit if throttle interval allows
        self._throttle_emit(pid, force=False)

    def next_chunk(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
    ):
        """
        Flush current stream and start with new chunks

        :param meta: context meta
        :param ctx: context item
        """
        pid = self.get_or_create_pid(meta)
        self._throttle_emit(pid, force=True)
        self._throttle_reset(pid)
        self.pids[pid].item = ctx
        self.pids[pid].buffer = ""
        self.update_names(meta, ctx)
        self.prev_chunk_replace = False
        self.prev_chunk_newline = False
        try:
            self.get_output_node(meta).page().runJavaScript(
                "nextStream();"
            )
        except Exception:
            pass

    def append_chunk_input(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            text_chunk: str,
            begin: bool = False
    ):
        """
        Append output chunk to output

        :param meta: context meta
        :param ctx: context item
        :param text_chunk: text chunk
        :param begin: if it is the beginning of the text
        """
        if text_chunk is None or text_chunk == "":
            return
        if ctx.hidden:
            return

        pid = self.get_or_create_pid(meta)
        self.clear_chunks_input(pid)
        try:
            self.get_output_node(meta).page().runJavaScript(
                f"""appendToInput({self.to_json(
                    self.sanitize_html(
                        self.helpers.format_chunk(text_chunk)
                    )
                )});"""
            )
        except Exception:
            pass

    def append_live(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            text_chunk: str,
            begin: bool = False
    ):
        """
        Append live output chunk to output

        :param meta: context meta
        :param ctx: context item
        :param text_chunk: text chunk
        :param begin: if it is the beginning of the text
        """
        pid = self.get_or_create_pid(meta)
        self.pids[pid].item = ctx
        if text_chunk is None or text_chunk == "":
            if begin:
                self.pids[pid].live_buffer = ""
            return

        self.update_names(meta, ctx)
        raw_chunk = str(text_chunk).translate({ord('<'): '&lt;', ord('>'): '&gt;'})
        if begin:
            debug = ""
            if self.is_debug():
                debug = self.append_debug(ctx, pid, "stream")
            if debug:
                raw_chunk = debug + raw_chunk
            self.pids[pid].live_buffer = ""
            self.pids[pid].is_cmd = False
            self.clear_live(meta, ctx)
        self.pids[pid].append_live_buffer(raw_chunk)

        to_append = self.pids[pid].live_buffer
        if has_unclosed_code_tag(self.pids[pid].live_buffer):
            to_append += "\n```"
        try:
            self.get_output_node(meta).page().runJavaScript(
                f"""replaceLive({self.to_json(
                    self.sanitize_html(
                        self.parser.parse(to_append)
                    )
                )});"""
            )
        except Exception as e:
            pass

    def clear_live(self, meta: CtxMeta, ctx: CtxItem):
        """
        Clear live output

        :param meta: context meta
        :param ctx: context item
        """
        if meta is None:
            return
        pid = self.get_or_create_pid(meta)
        if not self.pids[pid].loaded:
            js = "var element = document.getElementById('_append_live_');if (element) { element.replaceChildren(); }"
        else:
            js = "clearLive();"
        try:
            self.get_output_node_by_pid(pid).page().runJavaScript(js)
        except Exception:
            pass

    def append_node(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            html: str,
            type: int = 1,
            prev_ctx: Optional[CtxItem] = None,
            next_ctx: Optional[CtxItem] = None
    ):
        """
        Append and format raw text to output

        :param meta: context meta
        :param html: text to append
        :param type: type of message
        :param ctx: CtxItem instance
        :param prev_ctx: previous context item
        :param next_ctx: next context item
        """
        if ctx.hidden:
            return

        pid = self.get_or_create_pid(meta)
        self.append(
            pid,
            self.prepare_node(
                meta=meta,
                ctx=ctx,
                html=html,
                type=type,
                prev_ctx=prev_ctx,
                next_ctx=next_ctx,
            )
        )

    def append(
            self,
            pid,
            html: str,
            flush: bool = False,
            replace: bool = False,
    ):
        """
        Append text to output

        :param pid: ctx pid
        :param html: HTML code
        :param flush: True if flush only
        :param replace: True if replace current content
        """
        if self.pids[pid].loaded and not self.pids[pid].use_buffer:
            self.clear_chunks(pid)
            if html:
                self.flush_output(pid, html, replace)
            self.pids[pid].clear()
        else:
            if not flush:
                self.pids[pid].append_html(html)

    def append_context_item(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            prev_ctx: Optional[CtxItem] = None,
            next_ctx: Optional[CtxItem] = None
    ):
        """
        Append context item to output

        :param meta: context meta
        :param ctx: context item
        :param prev_ctx: previous context item
        :param next_ctx: next context item
        """
        self.append_input(
            meta,
            ctx,
            flush=False,
        )
        self.append_output(
            meta,
            ctx,
            flush=False,
            prev_ctx=prev_ctx,
            next_ctx=next_ctx,
        )

    def append_extra(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            footer: bool = False,
            render: bool = True
    ) -> str:
        """
        Append extra data (images, files, etc.) to output

        :param meta: context meta
        :param ctx: context item
        :param footer: True if it is a footer
        :param render: True if render, False if only return HTML
        :return: HTML code
        """
        self.tool_output_end()

        pid = self.get_pid(meta)
        appended = set()
        html_parts = []

        c = len(ctx.images)
        if c > 0:
            n = 1
            for image in ctx.images:
                if image is None:
                    continue
                if image in appended or image in self.pids[pid].images_appended:
                    continue
                try:
                    appended.add(image)
                    html_parts.append(self.body.get_image_html(image, n, c))
                    self.pids[pid].images_appended.append(image)
                    n += 1
                except Exception as e:
                    pass

        c = len(ctx.files)
        if c > 0:
            files_html = []
            n = 1
            for file in ctx.files:
                if file in appended or file in self.pids[pid].files_appended:
                    continue
                try:
                    appended.add(file)
                    files_html.append(self.body.get_file_html(file, n, c))
                    self.pids[pid].files_appended.append(file)
                    n += 1
                except Exception as e:
                    pass
            if files_html:
                html_parts.append("<br/><br/>".join(files_html))

        c = len(ctx.urls)
        if c > 0:
            urls_html = []
            n = 1
            for url in ctx.urls:
                if url in appended or url in self.pids[pid].urls_appended:
                    continue
                try:
                    appended.add(url)
                    urls_html.append(self.body.get_url_html(url, n, c))
                    self.pids[pid].urls_appended.append(url)
                    n += 1
                except Exception as e:
                    pass
            if urls_html:
                html_parts.append("<br/><br/>".join(urls_html))

        if self.window.core.config.get('ctx.sources'):
            if ctx.doc_ids is not None and len(ctx.doc_ids) > 0:
                try:
                    docs = self.body.get_docs_html(ctx.doc_ids)
                    html_parts.append(docs)
                except Exception as e:
                    pass

        html = "".join(html_parts)
        if render and html != "":
            if footer:
                self.append(pid, html)
            else:
                try:
                    self.get_output_node(meta).page().runJavaScript(
                        f"""appendExtra('{ctx.id}',{self.to_json(
                            self.sanitize_html(html)
                        )});"""
                    )
                except Exception as e:
                    pass

        return html

    def append_timestamp(
            self,
            ctx: CtxItem,
            text: str,
            type: Optional[int] = None
    ) -> str:
        """
        Append timestamp to text

        :param ctx: context item
        :param text: Input text
        :param type: Type of message
        :return: Text with timestamp (if enabled)
        """
        if ctx is not None and ctx.input_timestamp is not None:
            timestamp = None
            if type == self.NODE_INPUT:
                timestamp = ctx.input_timestamp
            elif type == self.NODE_OUTPUT:
                timestamp = ctx.output_timestamp
            if timestamp is not None:
                ts = datetime.fromtimestamp(timestamp)
                hour = ts.strftime("%H:%M:%S")
                text = f'<span class="ts">{hour}: </span>{text}'
        return text

    def reset(
            self,
            meta: Optional[CtxMeta] = None,
            clear_nodes: bool = True
    ):
        """
        Reset

        :param meta: Context meta
        :param clear_nodes: True if clear nodes
        """
        pid = self.get_pid(meta)
        if pid is not None and pid in self.pids:
            self.reset_by_pid(pid, clear_nodes=clear_nodes)
        else:
            if meta is not None:
                pid = self.get_or_create_pid(meta)
                self.reset_by_pid(pid, clear_nodes=clear_nodes)

        self.clear_live(meta, CtxItem())

    def reset_by_pid(self, pid: Optional[int], clear_nodes: bool = True):
        """
        Reset by PID

        :param pid: context PID
        :param clear_nodes: True if clear nodes
        """
        self.parser.reset()
        self.pids[pid].item = None
        self.pids[pid].html = ""
        if clear_nodes:
            self.clear_nodes(pid)
        self.clear_chunks(pid)
        self.pids[pid].images_appended = []
        self.pids[pid].urls_appended = []
        self.pids[pid].files_appended = []
        node = self.get_output_node_by_pid(pid)
        if node is not None:
            node.reset_current_content()
        self.reset_names_by_pid(pid)
        self.prev_chunk_replace = False
        self._throttle_reset(pid)

    def clear_input(self):
        """Clear input"""
        self.get_input_node().clear()

    def clear_output(
            self,
            meta: Optional[CtxMeta] = None
    ):
        """
        Clear output

        :param meta: Context meta
        """
        self.prev_chunk_replace = False
        self.reset(meta)

    def clear_chunks(self, pid):
        """
        Clear chunks from output

        :param pid: context PID
        """
        if pid is None:
            return
        self.clear_chunks_input(pid)
        self.clear_chunks_output(pid)

    def clear_chunks_input(
            self,
            pid: Optional[int]
    ):
        """
        Clear chunks from input

        :pid: context PID
        """
        if pid is None:
            return
        if not self.pids[pid].loaded:
            js = "var element = document.getElementById('_append_input_');if (element) { element.replaceChildren(); }"
        else:
            js = "clearInput();"
        try:
            self.get_output_node_by_pid(pid).page().runJavaScript(js)
        except Exception:
            pass

    def clear_chunks_output(
            self,
            pid: Optional[int]
    ):
        """
        Clear chunks from output

        :pid: context PID
        """
        self.prev_chunk_replace = False
        if not self.pids[pid].loaded:
            js = "var element = document.getElementById('_append_output_');if (element) { element.replaceChildren(); }"
        else:
            js = "clearOutput();"
        try:
            self.get_output_node_by_pid(pid).page().runJavaScript(js)
        except Exception:
            pass
        self._throttle_reset(pid)

    def clear_nodes(
            self,
            pid: Optional[int]
    ):
        """
        Clear nodes from output

        :pid: context PID
        """
        if not self.pids[pid].loaded:
            js = "var element = document.getElementById('_nodes_');if (element) { element.replaceChildren(); }"
        else:
            js = "clearNodes();"
        try:
            self.get_output_node_by_pid(pid).page().runJavaScript(js)
        except Exception:
            pass

    def prepare_node(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            html: str,
            type: int = 1,
            prev_ctx: Optional[CtxItem] = None,
            next_ctx: Optional[CtxItem] = None
    ) -> str:
        """
        Prepare node HTML

        :param meta: context meta
        :param ctx: CtxItem instance
        :param html: html text
        :param type: type of message
        :param prev_ctx: previous context item
        :param next_ctx: next context item
        :return: prepared HTML
        """
        pid = self.get_or_create_pid(meta)
        if type == self.NODE_OUTPUT:
            return self.prepare_node_output(
                meta=meta,
                ctx=ctx,
                html=html,
                prev_ctx=prev_ctx,
                next_ctx=next_ctx,
            )
        elif type == self.NODE_INPUT:
            return self.prepare_node_input(
                pid=pid,
                ctx=ctx,
                html=html,
                prev_ctx=prev_ctx,
                next_ctx=next_ctx,
            )

    def prepare_node_input(
            self,
            pid,
            ctx: CtxItem,
            html: str,
            prev_ctx: Optional[CtxItem] = None,
            next_ctx: Optional[CtxItem] = None
    ) -> str:
        """
        Prepare input node

        :param pid: context PID
        :param ctx: CtxItem instance
        :param html: html text
        :param prev_ctx: previous context item
        :param next_ctx: next context item
        :return: prepared HTML
        """
        msg_id = "msg-user-" + str(ctx.id) if ctx is not None else ""
        content = self.append_timestamp(
            ctx,
            self.helpers.format_user_text(html),
            type=self.NODE_INPUT
        )
        html = f"<p>{content}</p>"
        html = self.helpers.post_format_text(html)
        name = self.pids[pid].name_user

        if ctx.internal and ctx.input.startswith("[{"):
            name = trans("msg.name.system")
        if type(ctx.extra) is dict and "agent_evaluate" in ctx.extra:
            name = trans("msg.name.evaluation")

        debug = ""
        if self.is_debug():
            debug = self.append_debug(ctx, pid, "input")

        extra_style = ""
        extra = ""
        if ctx.extra is not None and "footer" in ctx.extra:
            extra = ctx.extra["footer"]
            extra_style = "display:block;"

        return f'<div class="msg-box msg-user" id="{msg_id}"><div class="name-header name-user">{name}</div><div class="msg">{html}<div class="msg-extra" style="{extra_style}">{extra}</div>{debug}</div></div>'

    def prepare_node_output(
            self,
            meta: CtxMeta,
            ctx: CtxItem,
            html: str,
            prev_ctx: Optional[CtxItem] = None,
            next_ctx: Optional[CtxItem] = None
    ) -> str:
        """
        Prepare output node

        :param meta: CtxMeta
        :param ctx: CtxItem instance
        :param html: html text
        :param prev_ctx: previous context item
        :param next_ctx: next context item
        :return: prepared HTML
        """
        is_cmd = (
            next_ctx is not None and
            next_ctx.internal and
            (len(ctx.cmds) > 0 or (ctx.extra_ctx is not None and len(ctx.extra_ctx) > 0))
        )
        pid = self.get_or_create_pid(meta)
        msg_id = f"msg-bot-{ctx.id}" if ctx is not None else ""
        html = self.helpers.pre_format_text(html)
        html = self.parser.parse(html)
        html = self.append_timestamp(ctx, html, type=self.NODE_OUTPUT)
        html = self.helpers.post_format_text(html)
        extra = self.append_extra(meta, ctx, footer=True, render=False)
        footer = self.body.prepare_action_icons(ctx)

        tool_output = ""
        spinner = ""
        output_class = "display:none"

        if is_cmd:
            if ctx.results is not None and len(ctx.results) > 0 \
                    and isinstance(ctx.extra, dict) and "agent_step" in ctx.extra:
                tool_output = self.helpers.format_cmd_text(str(ctx.input), indent=True)
                output_class = ""
            else:
                tool_output = self.helpers.format_cmd_text(str(next_ctx.input), indent=True)
                output_class = ""

        elif ctx.results is not None and len(ctx.results) > 0 \
                and isinstance(ctx.extra, dict) and "agent_step" in ctx.extra:
            tool_output = self.helpers.format_cmd_text(str(ctx.input), indent=True)
        else:
            out = (getattr(ctx, "output", "") or "")
            cmds = getattr(ctx, "cmds", ())
            if next_ctx is None and (
                    cmds
                    or out.startswith(('<tool>{"cmd"', '&lt;tool&gt;{"cmd"'))
                    or out.rstrip().endswith(('}</tool>', '}&lt;/tool&gt;'))
            ):
                spinner_class = ""
                spinner = ""
                # spinner_class = "" if ctx.live else "display:none"
                # spinner = f"<span class=\"spinner\" style=\"{spinner_class}\"><img src=\"{self._file_prefix}{self._icon_sync}\" width=\"30\" height=\"30\" class=\"loading\"></span>"

        tool_extra = self.body.prepare_tool_extra(ctx)
        debug = self.append_debug(ctx, pid, "output") if self.is_debug() else ""
        name_header = self.get_name_header(ctx)

        return f"<div class='msg-box msg-bot' id='{msg_id}'>{name_header}<div class='msg'>{html}{spinner}<div class='msg-tool-extra'>{tool_extra}</div><div class='tool-output' style='{output_class}'><span class='toggle-cmd-output' onclick='toggleToolOutput({ctx.id});' title='{trans('action.cmd.expand')}' role='button'><img src='{self._file_prefix}{self._icon_expand}' width='25' height='25' valign='middle'></span><div class='content' style='display:none'>{tool_output}</div></div><div class='msg-extra'>{extra}</div>{footer}{debug}</div></div>"

    def get_name_header(self, ctx: CtxItem, stream: bool = False) -> str:
        """
        Get name header for the bot

        :param ctx: CtxItem instance
        :param stream: True if it is a stream
        :return: HTML name header
        """
        meta = ctx.meta
        if meta is None:
            return ""
        preset_id = meta.preset
        if preset_id is None or preset_id == "":
            return ""
        preset = self.window.core.presets.get(preset_id)
        if preset is None:
            return ""
        if not preset.ai_personalize:
            return ""

        output_name = ""
        avatar_html = ""
        if preset.ai_name:
            output_name = preset.ai_name
        if preset.ai_avatar:
            presets_dir = self.window.core.config.get_user_dir("presets")
            avatars_dir = os.path.join(presets_dir, "avatars")
            avatar_path = os.path.join(avatars_dir, preset.ai_avatar)
            if os.path.exists(avatar_path):
                avatar_html = f"<img src=\"{self._file_prefix}{avatar_path}\" class=\"avatar\"> "

        if not output_name and not avatar_html:
            return ""

        if stream:
            return f"{avatar_html}{output_name}"
        else:
            return f"<div class=\"name-header name-bot\">{avatar_html}{output_name}</div>"

    def flush_output(
            self,
            pid: Optional[int],
            html: str,
            replace: bool = False
    ):
        """
        Flush output

        :param pid: context PID
        :param html: HTML code
        :param replace: True if replace current content
        """
        try:
            if replace:
                self.get_output_node_by_pid(pid).page().bridge.nodeReplace.emit(
                    self.sanitize_html(html)
                )
            else:
                self.get_output_node_by_pid(pid).page().bridge.node.emit(
                    self.sanitize_html(html)
                )
        except Exception:
            pass
        html = None

    def reload(self):
        """Reload output, called externally only on theme change to redraw content"""
        self.window.controller.ctx.refresh_output()

    def flush(
            self,
            pid:
            Optional[int]
    ):
        """
        Flush output

        :param pid: context PID
        """
        if self.pids[pid].loaded:
            return

        html = self.body.get_html(pid)
        node = self.get_output_node_by_pid(pid)
        if node is not None:
            node.setHtml(html, baseUrl="file://")

    def fresh(
            self,
            meta: Optional[CtxMeta] = None
    ):
        """
        Reset page

        :param meta: context meta
        """
        pid = self.get_or_create_pid(meta)
        if pid is None:
            return
        node = self.get_output_node_by_pid(pid)
        if node is not None:
            node.resetPage()

        self._throttle_reset(pid)

    def get_output_node(
            self,
            meta: Optional[CtxMeta] = None
    ):
        """
        Get output node

        :param meta: context meta
        :return: output node
        """
        return self.window.core.ctx.output.get_current(meta)

    def get_output_node_by_pid(
            self,
            pid: Optional[int]
    ):
        """
        Get output node by PID

        :param pid: context pid
        :return: output node
        """
        return self.window.core.ctx.output.get_by_pid(pid)

    def get_input_node(self) -> ChatInput:
        """
        Get input node

        :return: input node
        """
        return self.window.ui.nodes['input']

    def remove_item(self, ctx: CtxItem):
        """
        Remove item from output

        :param ctx: context item
        """
        try:
            self.get_output_node(ctx.meta).page().runJavaScript(
                f"if (typeof window.removeNode !== 'undefined') removeNode({self.to_json(ctx.id)});"
            )
        except Exception:
            pass

    def remove_items_from(self, ctx: CtxItem):
        """
        Remove item from output

        :param ctx: context item
        """
        try:
            self.get_output_node(ctx.meta).page().runJavaScript(
                f"if (typeof window.removeNodesFromId !== 'undefined') removeNodesFromId({self.to_json(ctx.id)});"
            )
        except Exception:
            pass

    def reset_names(self, meta: CtxMeta):
        """
        Reset names

       :param meta: context meta
        """
        if meta is None:
            return
        pid = self.get_or_create_pid(meta)
        self.reset_names_by_pid(pid)

    def reset_names_by_pid(self, pid: int):
        """
        Reset names by PID

        :param pid: context pid
        """
        self.pids[pid].name_user = trans("chat.name.user")
        self.pids[pid].name_bot = trans("chat.name.bot")

    def on_reply_submit(self, ctx: CtxItem):
        """
        On regenerate submit

        :param ctx: context item
        """
        self.remove_items_from(ctx)

    def on_edit_submit(self, ctx: CtxItem):
        """
        On regenerate submit

        :param ctx: context item
        """
        self.remove_items_from(ctx)

    def on_enable_edit(self, live: bool = True):
        """
        On enable edit icons

        :param live: True if live update
        """
        if not live:
            return
        try:
            nodes = self.get_all_nodes()
            for node in nodes:
                node.page().runJavaScript("if (typeof window.enableEditIcons !== 'undefined') enableEditIcons();")
        except Exception:
            pass

    def on_disable_edit(self, live: bool = True):
        """
        On disable edit icons

        :param live: True if live update
        """
        if not live:
            return
        try:
            nodes = self.get_all_nodes()
            for node in nodes:
                node.page().runJavaScript("if (typeof window.disableEditIcons !== 'undefined') disableEditIcons();")
        except Exception:
            pass

    def on_enable_timestamp(self, live: bool = True):
        """
        On enable timestamp

        :param live: True if live update
        """
        if not live:
            return
        try:
            nodes = self.get_all_nodes()
            for node in nodes:
                node.page().runJavaScript("if (typeof window.enableTimestamp !== 'undefined') enableTimestamp();")
        except Exception:
            pass

    def on_disable_timestamp(self, live: bool = True):
        """
        On disable timestamp

        :param live: True if live update
        """
        if not live:
            return
        try:
            nodes = self.get_all_nodes()
            for node in nodes:
                node.page().runJavaScript("if (typeof window.disableTimestamp !== 'undefined') disableTimestamp();")
        except Exception:
            pass

    def update_names(
            self,
            meta: CtxMeta,
            ctx: CtxItem
    ):
        """
        Update names

        :param meta: context meta
        :param ctx: context item
        """
        pid = self.get_or_create_pid(meta)
        if pid is None:
            return
        if ctx.input_name is not None and ctx.input_name != "":
            self.pids[pid].name_user = ctx.input_name
        if ctx.output_name is not None and ctx.output_name != "":
            self.pids[pid].name_bot = ctx.output_name

    def clear_all(self):
        """Clear all"""
        for pid in self.pids:
            self.clear_chunks(pid)
            self.clear_nodes(pid)
            self.pids[pid].html = ""
            self._throttle_reset(pid)

    def scroll_to_bottom(self):
        """Scroll to bottom"""
        pass

    def append_block(self):
        """Append block to output"""
        pass

    def to_end(self, ctx: CtxItem):
        """
        Move cursor to end of output

        :param ctx: context item
        """
        pass

    def get_all_nodes(self) -> list:
        """
        Return all registered nodes

        :return: list of ChatOutput nodes (tabs)
        """
        return self.window.core.ctx.output.get_all()

    # TODO: on lang change

    def reload_css(self):
        """Reload CSS - all, global"""
        to_json = self.to_json(self.body.prepare_styles())
        nodes = self.get_all_nodes()
        for pid in self.pids:
            if self.pids[pid].loaded:
                for node in nodes:
                    try:
                        node.page().runJavaScript(
                            f"if (typeof window.updateCSS !== 'undefined') updateCSS({to_json});"
                        )
                        if self.window.core.config.get('render.blocks'):
                            node.page().runJavaScript(
                                "if (typeof window.enableBlocks !== 'undefined') enableBlocks();"
                            )
                        else:
                            node.page().runJavaScript(
                                "if (typeof window.disableBlocks !== 'undefined') disableBlocks();"
                            )
                    except Exception as e:
                        pass
                return

    def on_theme_change(self):
        """On theme change"""
        self.window.controller.theme.markdown.load()
        for pid in self.pids:
            if self.pids[pid].loaded:
                self.reload_css()
                return

    def tool_output_append(
            self,
            meta: CtxMeta,
            content: str
    ):
        """
        Add tool output (append)

        :param meta: context meta
        :param content: content
        """
        try:
            self.get_output_node(meta).page().runJavaScript(
                f"""if (typeof window.appendToolOutput !== 'undefined') appendToolOutput({self.to_json(
                    self.sanitize_html(content)
                )});"""
            )
        except Exception:
            pass

    def tool_output_update(
            self,
            meta: CtxMeta,
            content: str
    ):
        """
        Replace tool output

        :param meta: context meta
        :param content: content
        """
        try:
            self.get_output_node(meta).page().runJavaScript(
                f"""if (typeof window.updateToolOutput !== 'undefined') updateToolOutput({self.to_json(
                    self.sanitize_html(content)
                )});"""
            )
        except Exception:
            pass

    def tool_output_clear(self, meta: CtxMeta):
        """
        Clear tool output

        :param meta: context meta
        """
        try:
            self.get_output_node(meta).page().runJavaScript(
                f"if (typeof window.clearToolOutput !== 'undefined') clearToolOutput();"
            )
        except Exception:
            pass

    def tool_output_begin(self, meta: CtxMeta):
        """
        Begin tool output

        :param meta: context meta
        """
        try:
            self.get_output_node(meta).page().runJavaScript(
                f"if (typeof window.beginToolOutput !== 'undefined') beginToolOutput();"
            )
        except Exception:
            pass

    def tool_output_end(self):
        """End tool output"""
        try:
            self.get_output_node().page().runJavaScript(
                f"if (typeof window.endToolOutput !== 'undefined') endToolOutput();"
            )
        except Exception:
            pass

    def sanitize_html(self, html: str) -> str:
        """
        Sanitize HTML to prevent XSS attacks

        :param html: HTML string to sanitize
        :return: sanitized HTML string
        """
        if not html:
            return ""
        # Fast path: avoid regex work and extra allocations when not needed
        if '&amp;' not in html:
            return html
        return self.RE_AMP_LT_GT.sub(r'&\1;', html)

    def append_debug(
            self,
            ctx: CtxItem,
            pid,
            title: Optional[str] = None
    ) -> str:
        """
        Append debug info

        :param ctx: context item
        :param pid: context PID
        :param title: debug title
        :return: HTML debug info
        """
        if title is None:
            title = "debug"
        return f"<div class='debug'><b>{title}:</b> pid: {pid}, ctx: {ctx.to_dict()}</div>"

    def is_debug(self) -> bool:
        """
        Check if debug mode is enabled

        :return: True if debug mode is enabled
        """
        return self.window.core.config.get("debug.render", False)

    def remove_pid(self, pid: int):
        """
        Remove PID from renderer

        :param pid: context PID
        """
        if pid in self.pids:
            del self.pids[pid]
        self._thr.pop(pid, None)

    def _throttle_get(self, pid: int) -> dict:
        """
        Return per-pid throttle state

        :param pid: context PID
        :return: throttle state dictionary
        """
        thr = self._thr.get(pid)
        if thr is None:
            thr = {
                "last": 0.0,
                "op": 0,
                "name": "",
                "replace_html": "",
                "append": Renderer._AppendBuffer(),
                "code": False,
            }
            self._thr[pid] = thr
        return thr

    def _throttle_reset(self, pid: Optional[int]):
        """
        Reset throttle state

        :param pid: context PID
        """
        if pid is None:
            return
        thr = self._thr.get(pid)
        if thr is None:
            return
        thr["op"] = 0
        thr["name"] = ""
        thr["replace_html"] = ""
        # Replace append buffer instance to drop any capacity eagerly
        thr["append"] = Renderer._AppendBuffer()
        thr["code"] = False

    def _throttle_queue(
            self,
            pid: int,
            name: str,
            html: str,
            text_chunk: str,
            replace: bool,
            is_code_block: bool
    ):
        """
        Queue text chunk for throttled output

        :param pid: context PID
        :param name: name header string
        :param html: HTML content to replace or append
        :param text_chunk: text chunk to append
        :param replace: True if the chunk should replace existing content
        :param is_code_block: True if the chunk is a code block
        """
        thr = self._throttle_get(pid)
        if name:
            thr["name"] = name

        if replace:
            thr["op"] = 1
            thr["replace_html"] = html
            # Drop previous append items aggressively when a replace snapshot is available
            thr["append"].clear()
            thr["code"] = bool(is_code_block)
        else:
            if thr["op"] == 1:
                # Refresh the pending replace with the latest HTML snapshot
                thr["replace_html"] = html
                thr["code"] = bool(is_code_block)
                return
            thr["op"] = 2
            thr["append"].append(text_chunk)
            thr["code"] = bool(is_code_block)

    def _throttle_emit(self, pid: int, force: bool = False):
        """
        Emit throttled output to the node

        :param pid: context PID
        :param force: Force emit even if throttle interval has not passed
        """
        thr = self._throttle_get(pid)
        now = monotonic()
        if not force and (now - thr["last"] < self._throttle_interval):
            return

        node = self.get_output_node_by_pid(pid)
        if node is None:
            return

        try:
            if thr["op"] == 1:
                # Replace snapshot
                replace_payload = self.sanitize_html(thr["replace_html"])
                node.page().bridge.chunk.emit(
                    thr["name"],
                    replace_payload,
                    "",
                    True,
                    bool(thr["code"]),
                )
                thr["replace_html"] = ""  # Cut reference ASAP
                thr["last"] = now

                # Append tail (if any)
                if not thr["append"].is_empty():
                    append_str = thr["append"].get_and_clear()
                    node.page().bridge.chunk.emit(
                        thr["name"],
                        "",
                        self.sanitize_html(append_str),
                        False,
                        bool(thr["code"]),
                    )
                    thr["last"] = now

                self._throttle_reset(pid)

            elif thr["op"] == 2 and not thr["append"].is_empty():
                append_str = thr["append"].get_and_clear()
                node.page().bridge.chunk.emit(
                    thr["name"],
                    "",
                    self.sanitize_html(append_str),
                    False,
                    bool(thr["code"]),
                )
                thr["last"] = now
                self._throttle_reset(pid)
        except Exception:
            pass