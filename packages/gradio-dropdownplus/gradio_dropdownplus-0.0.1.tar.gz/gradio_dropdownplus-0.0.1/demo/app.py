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