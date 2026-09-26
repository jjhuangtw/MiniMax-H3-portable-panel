# -*- coding: utf-8 -*-
"""Traditional Chinese / English for the panel.

The Chinese text in the code is the source; `i18n_en.EN` maps it to English.
- T("中文")  static UI text (labels, Markdown, buttons, tab names, dropdown labels). Gradio's frontend
             translates it, following the browser language or the 🌐 toggle.
- L("中文")  text made at run time (errors, warnings, progress, status lines). Resolved on the server
             from the request: the toggle's cookie first, then the browser's Accept-Language.
- Templates with {} placeholders go through L("…{0}…", value) so both languages share the values.

Gradio picks its locale before the page's `head` HTML is added, so LanguageBoot injects a tiny script
at the very top of the page that applies the saved choice (or maps any zh-* browser to zh-TW).
"""
import hashlib

import gradio as gr
from gradio.i18n import I18nData

from i18n_en import EN

LANG_KEY = "h3_lang"            # localStorage + cookie name shared by the toggle and the server
ZH, EN_CODE = "zh-TW", "en"

_zh, _en = {}, {}               # key -> text, handed to gr.I18n; filled as T() is called


def _key(text):
    return "t" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def T(zh, en=None):
    """Static UI text: register the pair and return Gradio's translation marker."""
    if zh is None or not str(zh).strip():
        return zh
    zh = str(zh)
    key = _key(zh)
    _zh[key] = zh
    _en[key] = en if en is not None else EN.get(zh, zh)
    return I18nData(key)


def choices(values):
    """Dropdown / radio choices: translated labels, unchanged values (the code compares values)."""
    return [(T(value), value) for value in values]


def request_language():
    try:
        from gradio.context import LocalContext
        request = LocalContext.request.get(None)
    except LookupError:
        request = None
    if request is None:
        return ZH
    try:
        saved = request.cookies.get(LANG_KEY)
    except Exception:
        saved = None
    if saved in (ZH, EN_CODE):
        return saved
    try:
        accept = (request.headers.get("accept-language") or "").lower()
    except Exception:
        accept = ""
    return ZH if accept.startswith("zh") else EN_CODE


def L(zh, *args, **kwargs):
    """Run-time text in the language of the current request; formats {} placeholders when given args."""
    text = EN.get(zh, zh) if request_language() == EN_CODE else zh
    return text.format(*args, **kwargs) if (args or kwargs) else text


def table(rows, headers):
    """A Dataframe value with plain headers in the request language. Gradio never translates Dataframe
    headers (T() markers show up raw), so tables always carry translated plain-text headers."""
    import pandas as pd
    return pd.DataFrame(list(rows or []), columns=[L(h) for h in headers])


_tables = []                    # (Dataframe, Chinese headers) re-headed on page load


def dataframe(headers, **kwargs):
    """gr.Dataframe with plain Chinese headers; bind_tables() swaps in the viewer's language on load."""
    component = gr.Dataframe(headers=list(headers), **kwargs)
    _tables.append((component, list(headers)))
    return component


def bind_tables(demo):
    """Call once after the UI is built: each registered table starts empty with translated headers."""
    for component, headers in _tables:
        demo.load(lambda h=headers: table([], h), None, component, queue=False)


def build_i18n():
    return gr.I18n(**{ZH: _zh, EN_CODE: _en})


# Runs before Gradio: a saved choice wins, otherwise any Chinese browser is shown zh-TW and the rest English.
BOOT_SCRIPT = f"""<script>
(function () {{
  var lang = null;
  try {{ lang = localStorage.getItem('{LANG_KEY}'); }} catch (e) {{}}
  if (lang !== '{ZH}' && lang !== '{EN_CODE}') {{
    var nav = (navigator.languages && navigator.languages[0]) || navigator.language || '';
    lang = nav.toLowerCase().indexOf('zh') === 0 ? '{ZH}' : '{EN_CODE}';
  }}
  try {{
    Object.defineProperty(navigator, 'language', {{ get: function () {{ return lang; }} }});
    Object.defineProperty(navigator, 'languages', {{ get: function () {{ return [lang]; }} }});
  }} catch (e) {{}}
  document.documentElement.lang = lang;
}})();
</script>""".encode("utf-8")

# The 🌐 button: flip, remember in localStorage (frontend) and a cookie (server messages), reload.
TOGGLE_JS = f"""() => {{
  var current = navigator.language === '{EN_CODE}' ? '{EN_CODE}' : '{ZH}';
  var next = current === '{EN_CODE}' ? '{ZH}' : '{EN_CODE}';
  try {{ localStorage.setItem('{LANG_KEY}', next); }} catch (e) {{}}
  document.cookie = '{LANG_KEY}=' + next + '; path=/; max-age=31536000; SameSite=Lax';
  location.reload();
}}"""


class LanguageBoot:
    """ASGI middleware: put BOOT_SCRIPT at the top of <head> on the panel's page."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("path") != "/":
            return await self.app(scope, receive, send)
        start, chunks = {}, []

        async def capture(message):
            if message["type"] == "http.response.start":
                start.update(message)
                return
            chunks.append(message.get("body", b""))
            if message.get("more_body"):
                return
            body = b"".join(chunks)
            headers = [(k, v) for k, v in start.get("headers", []) if k.lower() != b"content-length"]
            if b"text/html" in dict(start.get("headers", [])).get(b"content-type", b""):
                body = body.replace(b"<head>", b"<head>" + BOOT_SCRIPT, 1)
            await send({**start, "headers": headers + [(b"content-length", str(len(body)).encode())]})
            await send({"type": "http.response.body", "body": body})

        await self.app(scope, receive, capture)


def app_kwargs():
    from starlette.middleware import Middleware
    return {"middleware": [Middleware(LanguageBoot)]}
