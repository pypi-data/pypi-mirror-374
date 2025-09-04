---
tags: [gradio-custom-component, ui, form, settings, dataclass]
title: gradio_propertysheet
short_description: Property Sheet Component for Gradio
colorFrom: blue
colorTo: green
sdk: gradio
pinned: true
app_file: space.py
---

# `gradio_dropdownplus`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.5%20-%20blue"> <a href="https://huggingface.co/spaces/elismasilva/gradio_dropdownplus"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Demo-blue"></a><p><span>💻 <a href='https://github.com/DEVAIEXP/gradio_component_dropdownplus'>Component GitHub Code</a></span></p>


Advanced Dropdown Component for Gradio UI

## Installation

```bash
pip install gradio_dropdownplus
```

## Usage

```python
import gradio as gr
from gradio_dropdownplus import DropdownPlus
import time

# --- 1. Define Choices and Helper Functions ---

# A realistic set of choices, including tuples for (display_name, value)
CHOICES_WITH_TUPLES = [
    ("GPT-4 Turbo", "gpt-4-1106-preview"),
    ("GPT-3.5 Turbo", "gpt-3.5-turbo-16k"),
    ("Claude 3 Opus", "claude-3-opus-20240229"),
    ("Claude 3 Sonnet", "claude-3-sonnet-20240229"),
    ("Llama 3 70B", "llama3-70b-8192"),
    ("Mixtral 8x7B", "mixtral-8x7b-32768"),
]

SIMPLE_CHOICES = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]

def update_output(
    single_select, 
    multi_select, 
    custom_value_select, 
    indexed_select
):
    """Updates the output textboxes with the selected values."""
    time.sleep(1) # Simulate some processing time
    output_str = (
        f"--- SELECTIONS ---\n"
        f"Single Select (Value): {single_select}\n"
        f"Multi Select (Values): {multi_select}\n"
        f"Allow Custom Value (Value): {custom_value_select}\n"
        f"Indexed Select (Index): {indexed_select}"
    )
    return output_str

# --- 2. Build the Gradio App ---

with gr.Blocks(theme=gr.themes.Soft(), title="DropdownPlus Demo") as demo:
    gr.Markdown(
        """
        # DropdownPlus Component Demo
        This demo showcases the features of the `DropdownPlus` custom component, including
        single-select, multi-select, custom values, and the new `help` tooltip.
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### Interactive Components")
            
            # --- Single Select with Help Text ---
            dropdown_single = DropdownPlus(
                choices=CHOICES_WITH_TUPLES,
                label="Select a Model",
                info="A standard single-select dropdown.",
                help="Hover over me to see this help tooltip! This demonstrates the new 'help' parameter.",
                interactive=True
            )
            
            # --- Multi Select ---
            dropdown_multi = DropdownPlus(
                choices=SIMPLE_CHOICES,
                label="Select Multiple Fruits",
                info="A multi-select dropdown. Try selecting more than one.",
                multiselect=True,
                value=["Apple", "Cherry"], # Default value
                interactive=True
            )

            # --- Allow Custom Value ---
            dropdown_custom = DropdownPlus(
                choices=SIMPLE_CHOICES,
                label="Select a Fruit or Type Your Own",
                info="This dropdown allows for custom, user-typed values.",
                allow_custom_value=True,
                interactive=True
            )

            # --- Indexed Return Value ---
            dropdown_indexed = DropdownPlus(
                choices=SIMPLE_CHOICES,
                label="Select a Fruit (Returns Index)",
                info="This dropdown will return the numerical index of the choice, not the value.",
                type="index",
                interactive=True
            )
            
        with gr.Column(scale=1):
            gr.Markdown("### Output")
            
            # Display area for the selected values
            output_textbox = gr.Textbox(
                label="Selected Values",
                lines=6,
                interactive=False
            )
            
            submit_button = gr.Button("Submit Selections", variant="primary")
            
            gr.Markdown("### Static Examples")
            
            # --- Static Single Select ---
            DropdownPlus(
                choices=CHOICES_WITH_TUPLES,
                label="Static Single-Select",
                value="claude-3-opus-20240229", # Pre-selected value
                interactive=False
            )

            # --- Static Multi Select ---
            DropdownPlus(
                choices=SIMPLE_CHOICES,
                label="Static Multi-Select",
                value=["Banana", "Date", "Elderberry"],
                multiselect=True,
                interactive=False
            )

    # --- Event Listeners ---
    
    # Gather all dropdown components for the input
    inputs = [
        dropdown_single,
        dropdown_multi,
        dropdown_custom,
        dropdown_indexed
    ]
    
    # Connect the submit button to the update function
    submit_button.click(
        fn=update_output,
        inputs=inputs,
        outputs=output_textbox
    )
    
    # You can also trigger updates on change for real-time feedback
    for dropdown in inputs:
        dropdown.change(
            fn=update_output,
            inputs=inputs,
            outputs=output_textbox
        )

if __name__ == "__main__":
    demo.launch()
```

## `DropdownPlus`

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
<td align="left"><code>choices</code></td>
<td align="left" style="width: 25%;">

```python
Sequence[
        str | int | float | tuple[str, str | int | float]
    ]
    | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">a list of string or numeric options to choose from. An option can also be a tuple of the form (name, value), where name is the displayed name of the dropdown choice and value is the value to be passed to the function, or returned by the function.</td>
</tr>

<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
str
    | int
    | float
    | Sequence[str | int | float]
    | Callable
    | DefaultValue
    | None
```