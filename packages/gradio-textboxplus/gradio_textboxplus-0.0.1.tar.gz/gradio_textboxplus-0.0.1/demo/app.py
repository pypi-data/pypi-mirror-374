import gradio as gr
from gradio_textboxplus import TextboxPlus # Make sure this import is correct

# --- 1. Define a simple function for the demo ---

def process_text(input_text):
    """
    A simple function that takes text and returns it,
    demonstrating the component's input/output capabilities.
    """
    if not input_text:
        return "You didn't enter anything!"
    return f"You entered: '{input_text}'"

# --- 2. Build the Gradio App using Blocks ---

with gr.Blocks(theme=gr.themes.Ocean(), title="TextboxPlus Demo") as demo:
    gr.Markdown(
        """
        # TextboxPlus Component Demo
        This is a simple demonstration of the `TextboxPlus` custom component,
        highlighting the new `help` tooltip feature.
        """
    )

    # --- Interactive Textbox with Help Tooltip ---
    # This is the main component being demonstrated.
    input_box = TextboxPlus(
        label="Your Name",
        info="Please enter your full name.",
        # The key feature: the help text for the tooltip.
        help="Hover over the (?) icon to see this help message, This provides brief, contextual guidance for the user.",
        placeholder="e.g., Jane Doe",
        interactive=True,
        elem_id="textboxplus-input",
    )

  

if __name__ == "__main__":
    demo.launch()