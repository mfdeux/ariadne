from typing import List, Union

from graphql import DocumentNode, GraphQLSchema, build_ast_schema, extend_schema, parse

from .types import SchemaBindable


def make_executable_schema(
    type_defs: Union[str, List[str]],
    bindables: Union[SchemaBindable, List[SchemaBindable], None] = None,
) -> GraphQLSchema:
    if isinstance(type_defs, list):
        type_defs = join_type_defs(type_defs)

    ast_document = parse(type_defs)
    schema = build_and_extend_schema(ast_document)

    if isinstance(bindables, list):
        for obj in bindables:
            obj.bind_to_schema(schema)
    elif bindables:
        bindables.bind_to_schema(schema)

    return schema


def join_type_defs(type_defs: List[str]) -> str:
    return "\n\n".join(t.strip() for t in type_defs)


def build_and_extend_schema(ast: DocumentNode) -> GraphQLSchema:
    schema = build_ast_schema(ast)
    extension_ast = extract_extensions(ast)

    if extension_ast.definitions:
        schema = extend_schema(schema, extension_ast)

    return schema


EXTENSION_KINDS = [
    "object_type_extension",
    "interface_type_extension",
    "input_object_type_extension",
    "union_type_extension",
    "enum_type_extension",
]


def extract_extensions(ast: DocumentNode) -> DocumentNode:
    extensions = [node for node in ast.definitions if node.kind in EXTENSION_KINDS]
    return DocumentNode(definitions=extensions)
