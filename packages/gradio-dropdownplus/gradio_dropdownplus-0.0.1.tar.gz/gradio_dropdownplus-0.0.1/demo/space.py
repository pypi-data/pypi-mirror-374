
import gradio as gr
from app import demo as app
import os

_docs = {'DropdownPlus': {'description': 'Creates a dropdown of choices from which a single entry or multiple entries can be selected (as an input component) or displayed (as an output component).\n', 'members': {'__init__': {'choices': {'type': 'Sequence[\n        str | int | float | tuple[str, str | int | float]\n    ]\n    | None', 'default': 'None', 'description': 'a list of string or numeric options to choose from. An option can also be a tuple of the form (name, value), where name is the displayed name of the dropdown choice and value is the value to be passed to the function, or returned by the function.'}, 'value': {'type': 'str\n    | int\n    | float\n    | Sequence[str | int | float]\n    | Callable\n    | DefaultValue\n    | None', 'default': 'value = <gradio_dropdownplus.dropdownplus.DefaultValue object at 0x0000027C72C27490>', 'description': 'the value selected in dropdown. If `multiselect` is true, this should be list, otherwise a single string or number from among `choices`. By default, the first choice in `choices` is initally selected. If set explicitly to None, no value is initally selected. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'type': {'type': 'Literal["value", "index"]', 'default': '"value"', 'description': 'type of value to be returned by component. "value" returns the string of the choice selected, "index" returns the index of the choice selected.'}, 'multiselect': {'type': 'bool | None', 'default': 'None', 'description': 'if True, multiple choices can be selected.'}, 'allow_custom_value': {'type': 'bool', 'default': 'False', 'description': 'if True, allows user to enter a custom value that is not in the list of choices.'}, 'max_choices': {'type': 'int | None', 'default': 'None', 'description': 'maximum number of choices that can be selected. If None, no limit is enforced.'}, 'filterable': {'type': 'bool', 'default': 'True', 'description': 'if True, user will be able to type into the dropdown and filter the choices by typing. Can only be set to False if `allow_custom_value` is False.'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'the label for this component, displayed above the component if `show_label` is `True` and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component corresponds to.'}, 'info': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'additional component description, appears below the label in smaller font. Supports markdown / HTML syntax.'}, 'help': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'A string of help text to display in a tooltip next to the label.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'if True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'if True, choices in this dropdown will be selectable; if False, selection will be disabled. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'if False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'an optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'an optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'if False, component will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': None}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': None}}, 'postprocess': {'value': {'type': 'str | int | float | list[str | int | float] | None', 'description': 'Expects a `str | int | float` corresponding to the value of the dropdown entry to be selected. Or, if `multiselect` is True, expects a `list` of values corresponding to the selected dropdown entries.'}}, 'preprocess': {'return': {'type': 'str\n    | int\n    | float\n    | list[str | int | float]\n    | list[int | None]\n    | None', 'description': 'Passes the value of the selected dropdown choice as a `str | int | float` or its index as an `int` into the function, depending on `type`. Or, if `multiselect` is True, passes the values of the selected dropdown choices as a list of corresponding values/indices instead.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the DropdownPlus changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the DropdownPlus.'}, 'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the DropdownPlus. Uses event data gradio.SelectData to carry `value` referring to the label of the DropdownPlus, and `selected` to refer to state of the DropdownPlus. See EventData documentation on how to use this event data'}, 'focus': {'type': None, 'default': None, 'description': 'This listener is triggered when the DropdownPlus is focused.'}, 'blur': {'type': None, 'default': None, 'description': 'This listener is triggered when the DropdownPlus is unfocused/blurred.'}, 'key_up': {'type': None, 'default': None, 'description': 'This listener is triggered when the user presses a key while the DropdownPlus is focused.'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'DropdownPlus': []}}}

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
# `gradio_dropdownplus`

<div style="display: flex; gap: 7px;">
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20orange">  
</div>

Advanced Dropdown Component for Gradio UI
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
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
    \"\"\"Formats the selected values for display.\"\"\"
    return (
        f"--- SELECTIONS ---\n\n"
        f"Model Selection (Help only): {model_selection}\n\n"
        f"Feature Selection (Help & Info): {feature_selection_with_info}\n\n"
        f"Multi-Select Features: {multi_selection}"
    )

# --- 2. Build the Gradio App ---

with gr.Blocks(theme=gr.themes.Ocean(), title="DropdownPlus Demo") as demo:
    gr.Markdown(
        \"\"\"
        # DropdownPlus Component Demo
        A demonstration of the `tooltip` functionality in the DropdownPlus component.
        \"\"\"
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
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `DropdownPlus`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["DropdownPlus"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["DropdownPlus"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, passes the value of the selected dropdown choice as a `str | int | float` or its index as an `int` into the function, depending on `type`. Or, if `multiselect` is True, passes the values of the selected dropdown choices as a list of corresponding values/indices instead.
- **As output:** Should return, expects a `str | int | float` corresponding to the value of the dropdown entry to be selected. Or, if `multiselect` is True, expects a `list` of values corresponding to the selected dropdown entries.

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
""", elem_classes=["md-custom", "DropdownPlus-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          DropdownPlus: [], };
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
