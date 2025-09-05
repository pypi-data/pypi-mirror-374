import ast
from typing import Dict, Optional
from ariadne_codegen.plugins.base import Plugin
from ariadne_codegen.client_generators import custom_fields, package
import ast
from typing import cast, List, Any
from ariadne_codegen.codegen import (
    generate_ann_assign,
    generate_name,
    generate_call,
    generate_constant,
    generate_method_definition,
    generate_return,
)


class InitTestPlugin(Plugin):
    pass


class CustomFieldsGenerator(custom_fields.CustomFieldsGenerator):

    def _generate_class_field(
        self,
        name: str,
        field_name: str,
        org_name: str,
        field: ast.ClassDef,
        method_required: bool,
        lineno: int,
    ) -> ast.stmt:
        if getattr(field, "args") or method_required:
            return self.generate_product_type_method(
                name, field_name, org_name, getattr(field, "args")
            )
        return generate_ann_assign(
            target=generate_name(name),
            annotation=generate_name(f'"{field_name}"'),
            value=generate_call(
                func=generate_name(field_name), args=[generate_constant(org_name)]
            ),
            lineno=lineno,
        )

    def generate_product_type_method(
        self,
        name: str,
        class_name: str,
        org_name: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> ast.FunctionDef:
        """Generates a method for a product type."""
        arguments = arguments or {}
        field_class_name = generate_name(class_name)
        (
            method_arguments,
            return_arguments_keys,
            return_arguments_values,
        ) = self.argument_generator.generate_arguments(arguments)
        self._imports.extend(self.argument_generator.imports)
        arguments_body: List[ast.stmt] = []
        arguments_keyword: List[ast.keyword] = []

        if arguments:
            (
                arguments_body,
                arguments_keyword,
            ) = self.argument_generator.generate_clear_arguments_section(
                return_arguments_keys, return_arguments_values
            )

        return generate_method_definition(
            name,
            arguments=method_arguments,
            body=cast(
                List[ast.stmt],
                [
                    *arguments_body,
                    generate_return(
                        value=generate_call(
                            func=field_class_name,
                            args=[generate_constant(org_name)],
                            keywords=arguments_keyword,
                        )
                    ),
                ],
            ),
            return_type=generate_name(f'"{class_name}"'),
            decorator_list=[generate_name("classmethod")],
        )


package.CustomFieldsGenerator = CustomFieldsGenerator
