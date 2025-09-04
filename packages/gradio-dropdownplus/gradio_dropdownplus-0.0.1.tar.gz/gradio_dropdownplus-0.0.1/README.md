---
tags: [gradio-custom-component, Dropdown]
title: gradio_dropdownplus
short_description: Advanced Dropdown Component for Gradio UI
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_dropdownplus`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  

Advanced Dropdown Component for Gradio UI

## Installation

```bash
pip install gradio_dropdownplus
```

## Usage

```python
import gradio as gr
from gradio_dropdownplus import DropdownPlus

# --- 1. Define Choices and Helper Function ---

# Choices for demonstration
MODEL_CHOICES = [
    ("GPT-4 Turbo", "gpt-4-1106-preview"),
    ("Claude 3 Opus", "claude-3-opus-20240229"),
    ("Llama 3 70B", "llama3-70b-8192"),
]

FEATURE_CHOICES = ["Feature A", "Feature B", "Feature C", "Feature D"]

def update_output(model_selection, feature_selection_with_info, multi_selection):
    """Formats the selected values for display."""
    return (
        f"--- SELECTIONS ---\n\n"
        f"Model Selection (Help only): {model_selection}\n\n"
        f"Feature Selection (Help & Info): {feature_selection_with_info}\n\n"
        f"Multi-Select Features: {multi_selection}"
    )

# --- 2. Build the Gradio App ---

with gr.Blocks(theme=gr.themes.Ocean(), title="DropdownPlus Demo") as demo:
    gr.Markdown(
        """
        # DropdownPlus Component Demo
        A demonstration of the `tooltip` functionality in the DropdownPlus component.
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### Interactive Examples")
            
            # --- Example 1: Dropdown with `label` and `help` only ---
            dropdown_help_only = DropdownPlus(
                choices=MODEL_CHOICES,
                label="Select a Model",
                help="This is a tooltip. It appears next to the label and provides brief guidance.",
                interactive=True
            )
            
            # --- Example 2: Dropdown with `label`, `help`, AND `info` ---
            dropdown_with_info = DropdownPlus(
                choices=FEATURE_CHOICES,
                label="Choose a Feature",
                info="This text appears below the label to provide more context.",
                help="The tooltip still appears next to the label, even when 'info' text is present.",
                interactive=True
            )

            # --- Example 3: Multi-select to show it works there too ---
            dropdown_multi = DropdownPlus(
                choices=FEATURE_CHOICES,
                label="Select Multiple Features",
                info="Help and info also work with multiselect.",
                help="Select one or more options.",
                multiselect=True,
                value=["Feature A", "Feature C"], # Default value
                interactive=True
            )
            
        with gr.Column(scale=1):
            gr.Markdown("### Output")
            
            output_textbox = gr.Textbox(
                label="Current Values",
                lines=8,
                interactive=False
            )

    # --- Event Listeners ---
    
    # List of all interactive components
    inputs = [
        dropdown_help_only,
        dropdown_with_info,
        dropdown_multi
    ]
    
    # Any change to any dropdown will update the output textbox
    for component in inputs:
        component.change(
            fn=update_output,
            inputs=inputs,
            outputs=output_textbox
        )

    # Trigger the initial display on load
    demo.load(
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

</td>
<td align="left"><code>value = <gradio_dropdownplus.dropdownplus.DefaultValue object at 0x0000027C72C27490></code></td>
<td align="left">the value selected in dropdown. If `multiselect` is true, this should be list, otherwise a single string or number from among `choices`. By default, the first choice in `choices` is initally selected. If set explicitly to None, no value is initally selected. If a function is provided, the function will be called each time the app loads to set the initial value of this component.</td>
</tr>

<tr>
<td align="left"><code>type</code></td>
<td align="left" style="width: 25%;">

```python
Literal["value", "index"]
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">type of value to be returned by component. "value" returns the string of the choice selected, "index" returns the index of the choice selected.</td>
</tr>

<tr>
<td align="left"><code>multiselect</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, multiple choices can be selected.</td>
</tr>

<tr>
<td align="left"><code>allow_custom_value</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">if True, allows user to enter a custom value that is not in the list of choices.</td>
</tr>

<tr>
<td align="left"><code>max_choices</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">maximum number of choices that can be selected. If None, no limit is enforced.</td>
</tr>

<tr>
<td align="left"><code>filterable</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">if True, user will be able to type into the dropdown and filter the choices by typing. Can only be set to False if `allow_custom_value` is False.</td>
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
<td align="left">if True, will display label.</td>
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
<td align="left">if True, choices in this dropdown will be selectable; if False, selection will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">if False, component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">an optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">an optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">if False, component will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, ...] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">None</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the DropdownPlus changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `input` | This listener is triggered when the user changes the value of the DropdownPlus. |
| `select` | Event listener for when the user selects or deselects the DropdownPlus. Uses event data gradio.SelectData to carry `value` referring to the label of the DropdownPlus, and `selected` to refer to state of the DropdownPlus. See EventData documentation on how to use this event data |
| `focus` | This listener is triggered when the DropdownPlus is focused. |
| `blur` | This listener is triggered when the DropdownPlus is unfocused/blurred. |
| `key_up` | This listener is triggered when the user presses a key while the DropdownPlus is focused. |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, passes the value of the selected dropdown choice as a `str | int | float` or its index as an `int` into the function, depending on `type`. Or, if `multiselect` is True, passes the values of the selected dropdown choices as a list of corresponding values/indices instead.
- **As input:** Should return, expects a `str | int | float` corresponding to the value of the dropdown entry to be selected. Or, if `multiselect` is True, expects a `list` of values corresponding to the selected dropdown entries.

 ```python
 def predict(
     value: str
    | int
    | float
    | list[str | int | float]
    | list[int | None]
    | None
 ) -> str | int | float | list[str | int | float] | None:
     return value
 ```
 
