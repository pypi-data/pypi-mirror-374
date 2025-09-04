
import gradio as gr
from app import demo as app
import os

_docs = {'TextboxPlus': {'description': 'Creates a textarea for user to enter string input or display string output.\n', 'members': {'__init__': {'value': {'type': 'str | I18nData | Callable | None', 'default': 'None', 'description': 'text to show in textbox. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'type': {'type': 'Literal["text", "password", "email"]', 'default': '"text"', 'description': 'The type of textbox. One of: \'text\' (which allows users to enter any text), \'password\' (which masks text entered by the user), \'email\' (which suggests email input to the browser). For "password" and "email" types, `lines` must be 1 and `max_lines` must be None or 1.'}, 'lines': {'type': 'int', 'default': '1', 'description': 'minimum number of line rows to provide in textarea.'}, 'max_lines': {'type': 'int | None', 'default': 'None', 'description': 'maximum number of line rows to provide in textarea. Must be at least `lines`. If not provided, the maximum number of lines is max(lines, 20) for "text" type, and 1 for "password" and "email" types.'}, 'placeholder': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'placeholder hint to provide behind textarea.'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.'}, 'info': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.'}, 'help': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'A string of help text to display in a tooltip next to the label.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display the label. If False, the copy button is hidden as well as well as the label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'if True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will be rendered as an editable textbox; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'autofocus': {'type': 'bool', 'default': 'False', 'description': 'If True, will focus on the textbox when the page loads. Use this carefully, as it can cause usability issues for sighted and non-sighted users.'}, 'autoscroll': {'type': 'bool', 'default': 'True', 'description': 'If True, will automatically scroll to the bottom of the textbox when the value changes, unless the user scrolls up. If False, will not scroll to the bottom of the textbox when the value changes.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'text_align': {'type': 'Literal["left", "right"] | None', 'default': 'None', 'description': 'How to align the text in the textbox, can be: "left", "right", or None (default). If None, the alignment is left if `rtl` is False, or right if `rtl` is True. Can only be changed if `type` is "text".'}, 'rtl': {'type': 'bool', 'default': 'False', 'description': 'If True and `type` is "text", sets the direction of the text to right-to-left (cursor appears on the left of the text). Default is False, which renders cursor on the right.'}, 'show_copy_button': {'type': 'bool', 'default': 'False', 'description': 'If True, includes a copy button to copy the text in the textbox. Only applies if show_label is True.'}, 'max_length': {'type': 'int | None', 'default': 'None', 'description': 'maximum number of characters (including newlines) allowed in the textbox. If None, there is no maximum length.'}, 'submit_btn': {'type': 'str | bool | None', 'default': 'False', 'description': 'If False, will not show a submit button. If True, will show a submit button with an icon. If a string, will use that string as the submit button text. When the submit button is shown, the border of the textbox will be removed, which is useful for creating a chat interface.'}, 'stop_btn': {'type': 'str | bool | None', 'default': 'False', 'description': 'If False, will not show a stop button. If True, will show a stop button with an icon. If a string, will use that string as the stop button text. When the stop button is shown, the border of the textbox will be removed, which is useful for creating a chat interface.'}, 'html_attributes': {'type': 'InputHTMLAttributes | None', 'default': 'None', 'description': 'An instance of gr.InputHTMLAttributes, which can be used to set HTML attributes for the input/textarea elements. Example: InputHTMLAttributes(autocorrect="off", spellcheck=False) to disable autocorrect and spellcheck.'}}, 'postprocess': {'value': {'type': 'str | None', 'description': 'Expects a {str} returned from function and sets textarea value to it.'}}, 'preprocess': {'return': {'type': 'str | None', 'description': 'Passes text value as a {str} into the function.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the TextboxPlus changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the TextboxPlus.'}, 'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the TextboxPlus. Uses event data gradio.SelectData to carry `value` referring to the label of the TextboxPlus, and `selected` to refer to state of the TextboxPlus. See EventData documentation on how to use this event data'}, 'submit': {'type': None, 'default': None, 'description': 'This listener is triggered when the user presses the Enter key while the TextboxPlus is focused.'}, 'focus': {'type': None, 'default': None, 'description': 'This listener is triggered when the TextboxPlus is focused.'}, 'blur': {'type': None, 'default': None, 'description': 'This listener is triggered when the TextboxPlus is unfocused/blurred.'}, 'stop': {'type': None, 'default': None, 'description': 'This listener is triggered when the user reaches the end of the media playing in the TextboxPlus.'}, 'copy': {'type': None, 'default': None, 'description': 'This listener is triggered when the user copies content from the TextboxPlus. Uses event data gradio.CopyData to carry information about the copied content. See EventData documentation on how to use this event data'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'TextboxPlus': []}}}

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
# `gradio_textboxplus`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

Advanced Textbox Component for Gradio UI
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_textboxplus
```

## Usage

```python
import gradio as gr
from gradio_textboxplus import TextboxPlus # Make sure this import is correct

# --- 1. Define a simple function for the demo ---

def process_text(input_text):
    \"\"\"
    A simple function that takes text and returns it,
    demonstrating the component's input/output capabilities.
    \"\"\"
    if not input_text:
        return "You didn't enter anything!"
    return f"You entered: '{input_text}'"

# --- 2. Build the Gradio App using Blocks ---

with gr.Blocks(theme=gr.themes.Ocean(), title="TextboxPlus Demo") as demo:
    gr.Markdown(
        \"\"\"
        # TextboxPlus Component Demo
        This is a simple demonstration of the `TextboxPlus` custom component,
        highlighting the new `help` tooltip feature.
        \"\"\"
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
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `TextboxPlus`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["TextboxPlus"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["TextboxPlus"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, passes text value as a {str} into the function.
- **As output:** Should return, expects a {str} returned from function and sets textarea value to it.

 ```python
def predict(
    value: str | None
) -> str | None:
    return value
```
""", elem_classes=["md-custom", "TextboxPlus-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          TextboxPlus: [], };
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
