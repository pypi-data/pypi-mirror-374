---
tags: [gradio-custom-component, TextBox]
title: gradio_textboxplus
short_description: Advanced Textbox Component for Gradio UI
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_textboxplus`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  

Advanced Textbox Component for Gradio UI

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
```

## `TextboxPlus`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | Callable | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">text to show in textbox. If a function is provided, the function will be called each time the app loads to set the initial value of this component.</td>
</tr>

<tr>
<td align="left"><code>type</code></td>
<td align="left" style="width: 25%;">

```python
Literal["text", "password", "email"]
```

</td>
<td align="left"><code>"text"</code></td>
<td align="left">The type of textbox. One of: 'text' (which allows users to enter any text), 'password' (which masks text entered by the user), 'email' (which suggests email input to the browser). For "password" and "email" types, `lines` must be 1 and `max_lines` must be None or 1.</td>
</tr>

<tr>
<td align="left"><code>lines</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>1</code></td>
<td align="left">minimum number of line rows to provide in textarea.</td>
</tr>

<tr>
<td align="left"><code>max_lines</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">maximum number of line rows to provide in textarea. Must be at least `lines`. If not provided, the maximum number of lines is max(lines, 20) for "text" type, and 1 for "password" and "email" types.</td>
</tr>

<tr>
<td align="left"><code>placeholder</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">placeholder hint to provide behind textarea.</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.</td>
</tr>

<tr>
<td align="left"><code>info</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.</td>
</tr>

<tr>
<td align="left"><code>help</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A string of help text to display in a tooltip next to the label.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
Timer | float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.</td>
</tr>

<tr>
<td align="left"><code>inputs</code></td>
<td align="left" style="width: 25%;">

```python
Component | Sequence[Component] | set[Component] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will display the label. If False, the copy button is hidden as well as well as the label.</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">if True, will place the component in a container - providing some extra padding around the border.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will be rendered as an editable textbox; if False, editing will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>autofocus</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, will focus on the textbox when the page loads. Use this carefully, as it can cause usability issues for sighted and non-sighted users.</td>
</tr>

<tr>
<td align="left"><code>autoscroll</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will automatically scroll to the bottom of the textbox when the value changes, unless the user scrolls up. If False, will not scroll to the bottom of the textbox when the value changes.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, ...] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.</td>
</tr>

<tr>
<td align="left"><code>text_align</code></td>
<td align="left" style="width: 25%;">

```python
Literal["left", "right"] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">How to align the text in the textbox, can be: "left", "right", or None (default). If None, the alignment is left if `rtl` is False, or right if `rtl` is True. Can only be changed if `type` is "text".</td>
</tr>

<tr>
<td align="left"><code>rtl</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True and `type` is "text", sets the direction of the text to right-to-left (cursor appears on the left of the text). Default is False, which renders cursor on the right.</td>
</tr>

<tr>
<td align="left"><code>show_copy_button</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, includes a copy button to copy the text in the textbox. Only applies if show_label is True.</td>
</tr>

<tr>
<td align="left"><code>max_length</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">maximum number of characters (including newlines) allowed in the textbox. If None, there is no maximum length.</td>
</tr>

<tr>
<td align="left"><code>submit_btn</code></td>
<td align="left" style="width: 25%;">

```python
str | bool | None
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If False, will not show a submit button. If True, will show a submit button with an icon. If a string, will use that string as the submit button text. When the submit button is shown, the border of the textbox will be removed, which is useful for creating a chat interface.</td>
</tr>

<tr>
<td align="left"><code>stop_btn</code></td>
<td align="left" style="width: 25%;">

```python
str | bool | None
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If False, will not show a stop button. If True, will show a stop button with an icon. If a string, will use that string as the stop button text. When the stop button is shown, the border of the textbox will be removed, which is useful for creating a chat interface.</td>
</tr>

<tr>
<td align="left"><code>html_attributes</code></td>
<td align="left" style="width: 25%;">

```python
InputHTMLAttributes | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An instance of gr.InputHTMLAttributes, which can be used to set HTML attributes for the input/textarea elements. Example: InputHTMLAttributes(autocorrect="off", spellcheck=False) to disable autocorrect and spellcheck.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the TextboxPlus changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `input` | This listener is triggered when the user changes the value of the TextboxPlus. |
| `select` | Event listener for when the user selects or deselects the TextboxPlus. Uses event data gradio.SelectData to carry `value` referring to the label of the TextboxPlus, and `selected` to refer to state of the TextboxPlus. See EventData documentation on how to use this event data |
| `submit` | This listener is triggered when the user presses the Enter key while the TextboxPlus is focused. |
| `focus` | This listener is triggered when the TextboxPlus is focused. |
| `blur` | This listener is triggered when the TextboxPlus is unfocused/blurred. |
| `stop` | This listener is triggered when the user reaches the end of the media playing in the TextboxPlus. |
| `copy` | This listener is triggered when the user copies content from the TextboxPlus. Uses event data gradio.CopyData to carry information about the copied content. See EventData documentation on how to use this event data |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, passes text value as a {str} into the function.
- **As input:** Should return, expects a {str} returned from function and sets textarea value to it.

 ```python
 def predict(
     value: str | None
 ) -> str | None:
     return value
 ```
 
