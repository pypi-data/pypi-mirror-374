"""Properties definition for the plugin."""

from mo.core import Properties, PropertySelectOption, Settings
from mo import translate  # Import translate for localization support

properties = Properties()

# Add your plugin properties here.

# Example: Add a boolean property using translate for the label
# properties.add_bool("enable_feature", translate("property.enable_feature"))
# properties.set_default("enable_feature", True)

# Example: Add an integer property with min/max/step, with translation
# properties.add_int("int_param", translate("property.int_param"), min=1, max=10, step=1)
# properties.set_default("int_param", 5)

# Example: Add a select property with translated options and label
# properties.add_select("mode", translate("property.mode"), [
#     PropertySelectOption(label=translate("property.mode1"), value="mode1"),
#     PropertySelectOption(label=translate("property.mode2"), value="mode2"),
# ])
# properties.set_default("mode", "mode1")

# --- Example: Select property that updates another select's options (using a modified callback) ---
#
# def on_main_select_change(props: Properties, settings: Settings):
#     selected = settings.get_setting("main_select")
#     if selected == "A":
#         options = [
#             PropertySelectOption(label=translate("property.alpha"), value="alpha"),
#             PropertySelectOption(label=translate("property.beta"), value="beta")
#         ]
#     else:
#         options = [
#             PropertySelectOption(label=translate("property.gamma"), value="gamma"),
#             PropertySelectOption(label=translate("property.delta"), value="delta")
#         ]
#     props.update_select_options("secondary_select", options)
#     props.set_default("secondary_select", options[0].value)
#     return props._properties
#
# # Define the main select property with translated label/options
# properties.add_select("main_select", translate("property.main_select"), [
#     PropertySelectOption(label=translate("property.option_a"), value="A"),
#     PropertySelectOption(label=translate("property.option_b"), value="B")
# ])
# properties.set_default("main_select", "A")
# properties.set_modified_callback("main_select", on_main_select_change)
#
# # Define the dependent select property
# properties.add_select("secondary_select", translate("property.secondary_select"), [
#     PropertySelectOption(label=translate("property.alpha"), value="alpha"),
#     PropertySelectOption(label=translate("property.beta"), value="beta")
# ])
# properties.set_default("secondary_select", "alpha")
#
# --- End of dependent select example ---
