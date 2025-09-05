
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
                value="""
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
                """,
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
