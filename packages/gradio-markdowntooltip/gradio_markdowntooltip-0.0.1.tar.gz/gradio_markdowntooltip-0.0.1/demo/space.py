
import gradio as gr
from app import demo as app
import os

_docs = {'MarkdownTooltip': {'description': 'Used to render arbitrary MarkdownTooltip output with an optional tooltip. Can also render latex enclosed by dollar signs. As this component does not accept user input,\nit is rarely used as an input component.\n', 'members': {'__init__': {'value': {'type': 'str | I18nData | Callable | None', 'default': 'None', 'description': 'Value to show in MarkdownTooltip component. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'tooltip': {'type': 'str | None', 'default': 'None', 'description': 'Optional tooltip text to show when hovering over the (?) icon. If not provided, no tooltip icon will be displayed.'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'This parameter has no effect'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'This parameter has no effect.'}, 'rtl': {'type': 'bool', 'default': 'False', 'description': 'If True, sets the direction of the rendered text to right-to-left. Default is False, which renders text left-to-right.'}, 'latex_delimiters': {'type': 'list[dict[str, str | bool]] | None', 'default': 'None', 'description': 'A list of dicts of the form {"left": open delimiter (str), "right": close delimiter (str), "display": whether to display in newline (bool)} that will be used to render LaTeX expressions. If not provided, `latex_delimiters` is set to `[{ "left": "$$", "right": "$$", "display": True }]`, so only expressions enclosed in $$ delimiters will be rendered as LaTeX, and in a new line. Pass in an empty list to disable LaTeX rendering. For more information, see the [KaTeX documentation](https://katex.org/docs/autorender.html).'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'sanitize_html': {'type': 'bool', 'default': 'True', 'description': 'If False, will disable HTML sanitization when converted from markdown. This is not recommended, as it can lead to security vulnerabilities.'}, 'line_breaks': {'type': 'bool', 'default': 'False', 'description': 'If True, will enable Github-flavored MarkdownTooltip line breaks in chatbot messages. If False (default), single new lines will be ignored.'}, 'header_links': {'type': 'bool', 'default': 'False', 'description': 'If True, will automatically create anchors for headings, displaying a link icon on hover.'}, 'height': {'type': 'int | str | None', 'default': 'None', 'description': 'The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If markdown content exceeds the height, the component will scroll.'}, 'max_height': {'type': 'int | str | None', 'default': 'None', 'description': 'The maximum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If markdown content exceeds the height, the component will scroll. If markdown content is shorter than the height, the component will shrink to fit the content. Will not have any effect if `height` is set and is smaller than `max_height`.'}, 'min_height': {'type': 'int | str | None', 'default': 'None', 'description': 'The minimum height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. If markdown content exceeds the height, the component will expand to fit the content. Will not have any effect if `height` is set and is larger than `min_height`.'}, 'show_copy_button': {'type': 'bool', 'default': 'False', 'description': 'If True, includes a copy button to copy the text in the MarkdownTooltip component. Default is False.'}, 'container': {'type': 'bool', 'default': 'False', 'description': 'If True, the MarkdownTooltip component will be displayed in a container. Default is False.'}, 'padding': {'type': 'bool', 'default': 'False', 'description': 'If True, the MarkdownTooltip component will have a certain padding (set by the `--block-padding` CSS variable) in all directions. Default is False.'}}, 'postprocess': {'value': {'type': 'str | gradio.i18n.I18nData | None', 'description': 'Expects a valid `str` that can be rendered as MarkdownTooltip.'}}, 'preprocess': {'return': {'type': 'str | None', 'description': 'Passes the `str` of MarkdownTooltip corresponding to the displayed value.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the MarkdownTooltip changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'copy': {'type': None, 'default': None, 'description': 'This listener is triggered when the user copies content from the MarkdownTooltip. Uses event data gradio.CopyData to carry information about the copied content. See EventData documentation on how to use this event data'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'MarkdownTooltip': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_markdowntooltip`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

Python library for easily interacting with trained machine learning models
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_markdowntooltip
```

## Usage

```python

import gradio as gr
from gradio_markdowntooltip import MarkdownTooltip


with gr.Blocks() as demo:
    gr.Markdown("# MarkdownTooltip Demo")
    gr.Markdown("This demo showcases the MarkdownTooltip component with tooltip functionality.")
    
    with gr.Row():
        with gr.Column():
            MarkdownTooltip(
                value="## Basic Markdown",
                label="Without Tooltip",
                tooltip="This is a helpful tooltip that appears when you hover over the question mark icon!",
            )
        
        with gr.Column():
            MarkdownTooltip(
                value="## Enhanced Markdown",
                tooltip="This is a helpful tooltip that appears when you hover over the question mark icon!",
                label="With Tooltip"
            )
    
    with gr.Row():
        with gr.Column():
            MarkdownTooltip(
                value=\"\"\"
## Features List
- **Bold text**
- *Italic text*  
- `Code snippets`
- [Links](https://gradio.app)

### Math Support
Inline math: $x = y + z$

Block math:
$$
\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
$$
                \"\"\",
                tooltip="This tooltip explains the mathematical notation and formatting features available in this markdown component.",
                label="Advanced Features"
            )
        
        with gr.Column():
            MarkdownTooltip(
                value="123",
                tooltip="Tooltips are perfect for providing additional context, explanations, or help text without cluttering the main content area.",
                label="Usage Instructions"
            )


if __name__ == "__main__":
    demo.launch()

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `MarkdownTooltip`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["MarkdownTooltip"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["MarkdownTooltip"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, passes the `str` of MarkdownTooltip corresponding to the displayed value.
- **As output:** Should return, expects a valid `str` that can be rendered as MarkdownTooltip.

 ```python
def predict(
    value: str | None
) -> str | gradio.i18n.I18nData | None:
    return value
```
""", elem_classes=["md-custom", "MarkdownTooltip-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          MarkdownTooltip: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
