import os
from pprint import pprint
from importlib import import_module, util
from django.conf import settings


class TemplateHelper:

    # Map context variables to template class/value/variables names
    def map_context(self, context):
        if not isinstance(context, dict):
            raise TypeError("context must be a dictionary")

        # Menu Fixed (vertical support only)
        if context.get("layout") == "vertical":
            context["menu_fixed_class"] = "layout-menu-fixed" if context.get(
                "menu_fixed") else ""

        # Content Layout
        if context.get("content_layout") == "wide":
            context["container_class"] = "container-fluid"
            context["content_layout_class"] = "layout-wide"
        else:
            context["container_class"] = "container-xxl"
            context["content_layout_class"] = "layout-compact"

    # Get theme variables by scope
    def get_theme_variables(self, scope):
        return settings.THEME_VARIABLES[scope]

    # Set the current page layout and init the layout bootstrap file
    def set_layout(self, view, context=None):
        if context is None:
            context = {}

        # Extract layout from the view path
        layout = os.path.splitext(view)[0].split("/")[0]

        # Get module path
        module = f"templates.{
            settings.THEME_LAYOUT_DIR.replace(
                '/', '.')}.bootstrap.{layout}"

        # Check if the bootstrap file exists
        if util.find_spec(module) is not None:
            # Auto import and init the default bootstrap.py file from the theme
            template_bootstrap = self.import_class(
                module, f"TemplateBootstrap{layout.title().replace('_', '')}"
            )
            template_bootstrap.init(context)
        else:
            module = f"templates.{
                settings.THEME_LAYOUT_DIR.replace(
                    '/', '.')}.bootstrap.default"
            template_bootstrap = self.import_class(
                module, "TemplateBootstrapDefault")
            template_bootstrap.init(context)

        return f"{settings.THEME_LAYOUT_DIR}/{view}"

    # Import a module by string
    def import_class(self, from_module, import_class_name):
        pprint(f"Loading {import_class_name} from {from_module}")
        module = import_module(from_module)
        return getattr(module, import_class_name)
