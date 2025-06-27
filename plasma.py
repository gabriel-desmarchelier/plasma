#!/usr/bin/env python

from tree_sitter import Language, Parser
import argparse
import logging


def print_state_set(parent):

    global mermaid_code
    global indent
    global indentation

    for state_set_child in parent.children:
        # Looking for the state set name
        if state_set_child.type == "identifier":
            state_set_name = state_set_child.text.decode("utf-8")
            logging.debug("new state set found : %s", state_set_name)
            mermaid_code += f"    {state_set_name}:::state_set_style\n"
            mermaid_code += f"    {state_set_name} : {state_set_name}\n"

        # Looking for a new state
        if state_set_child.type == "state":
            print_state(state_set_child)


def print_state(parent):

    global mermaid_code
    global indent
    global indentation

    for state_child in parent.children:
        # Looking for the state name
        if state_child.type == "identifier":
            state_name = state_child.text.decode("utf-8")
            logging.debug("new state found : %s", state_name)
            mermaid_code += f"    {state_name}:::state_style\n"
            mermaid_code += f"    {state_name} : {state_name}\n"
        elif state_child.type == "state_block":
            print_state_block(state_name, state_child)


def print_state_block(state_name, parent):

    global mermaid_code
    global indent
    global indentation

    transition_state_id = 0
    for state_block_child in parent.children:
        # Looking for the entry in the state
        if state_block_child.type == "entry":
            logging.debug("state entry found")
            for entry_child in state_block_child.children:
                if entry_child.type == "block":
                    for entry_block_child in entry_child.children:
                        # Looking for the statements in the entry block
                        if entry_block_child.type == "statement":
                            print_statement(
                                entry_block_child,
                                state_name,
                            )
        # Looking for "when"
        elif state_block_child.type == "transition":
            transition_state_id += 1
            print_transition(state_name, state_block_child, transition_state_id)


def print_transition(state_name, parent, transition_state_id):

    global mermaid_code
    global indent
    global indentation

    transition_state_name = state_name + "_transition_" + str(transition_state_id)
    logging.debug(
        "new transition found : %s",
        transition_state_name,
    )
    mermaid_code += f"    {transition_state_name}:::transition_style\n"
    mermaid_code += f"    {state_name} -->{transition_state_name}\n"
    for transition_child in parent.children:
        # Looking for transition binary expression condition
        if transition_child.type == "binary_expression":  # or 'call_expression':
            condition = transition_child.text.decode("utf-8")
            mermaid_code += f"    {transition_state_name} : when {condition}\n"
        # Looking for transition functions condtion
        elif transition_child.type == "call_expression":
            for call_expression_child in transition_child.children:
                if call_expression_child.type == "identifier":
                    function = call_expression_child.text.decode("utf-8")
                    if function == "delay":
                        condition = transition_child.text.decode("utf-8")
                        mermaid_code += (
                            f"    {transition_state_name} : when {condition}\n"
                        )
        # Looking for transition actions
        elif transition_child.type == "block":
            indent = 0
            for transition_block_child in transition_child.children:
                if transition_block_child.type == "statement":
                    print_statement(
                        transition_block_child,
                        transition_state_name,
                    )
        elif transition_child.type == "identifier":
            link_name = transition_child.text.decode("utf-8")
            mermaid_code += f"    {transition_state_name} -->{link_name}\n"


def print_if_statement(parent, transition_state_name):

    global mermaid_code
    global indent
    global indentation

    for if_statement_child in parent.children:
        if if_statement_child.type == "binary_expression":
            condition = if_statement_child.text.decode("utf-8")
            mermaid_code += f"    {transition_state_name} : {indentation} if ({condition}) #colon; \n"
            indent += 1
            apply_indent()
        elif if_statement_child.type == "statement":
            for statement_child in if_statement_child.children:
                if statement_child.type == "block":
                    for block_child in statement_child.children:
                        if block_child.type == "statement":
                            print_statement(block_child, transition_state_name)
        # Looking for an else
        elif if_statement_child.type == "else_statement":
            for else_statement_child in if_statement_child.children:
                if else_statement_child.type == "statement":
                    for statement_child in else_statement_child.children:
                        # Looking for "else if" statements
                        if statement_child.type == "if_statement":
                            logging.debug("ELIF statement found")
                            print_else_if_statement(
                                statement_child, transition_state_name
                            )
                        elif statement_child.type == "block":
                            indent -= 1
                            apply_indent()
                            mermaid_code += f"    {transition_state_name} : {indentation} else #colon; \n"
                            indent += 1
                            apply_indent()
                            for block_child in statement_child.children:
                                if block_child.type == "statement":
                                    print_statement(block_child, transition_state_name)
    indent -= 1
    apply_indent()


def print_else_if_statement(parent, transition_state_name):

    global mermaid_code
    global indent
    global indentation

    for if_statement_child in parent.children:
        # Looking for condition of the if
        if if_statement_child.type == "binary_expression":
            condition = if_statement_child.text.decode("utf-8")
            indent -= 1
            apply_indent()
            mermaid_code += f"    {transition_state_name} : {indentation} else if ({condition}) #colon; \n"
            indent += 1
            apply_indent()
        elif if_statement_child.type == "statement":
            for statement_child in if_statement_child.children:
                if statement_child.type == "block":
                    for block_child in statement_child.children:
                        if block_child.type == "statement":
                            print_statement(block_child, transition_state_name)
        # Looking for an else
        elif if_statement_child.type == "else_statement":
            for else_statement_child in if_statement_child.children:
                if else_statement_child.type == "statement":
                    for statement_child in else_statement_child.children:
                        # Looking for another if after the else
                        if statement_child.type == "if_statement":
                            print_else_if_statement(
                                statement_child, transition_state_name
                            )
                        if statement_child.type == "block":
                            logging.debug("ELSE statement found after ELIF")
                            indent -= 1
                            apply_indent()
                            mermaid_code += f"    {transition_state_name} : {indentation} else #colon; \n"
                            indent += 1
                            apply_indent()
                            for block_child in statement_child.children:
                                if block_child.type == "statement":
                                    print_statement(block_child, transition_state_name)


def print_while_statement(parent, transition_state_name):

    global mermaid_code
    global indent
    global indentation

    for while_statement_child in parent.children:
        if while_statement_child.type == "binary_expression":
            condition = while_statement_child.text.decode("utf-8")
            mermaid_code += f"    {transition_state_name} : {indentation} while ({condition}) #colon; \n"
            indent += 1
            apply_indent()
        elif while_statement_child.type == "statement":
            for statement_child in while_statement_child.children:
                if statement_child.type == "block":
                    for block_child in statement_child.children:
                        if block_child.type == "statement":
                            print_statement(block_child, transition_state_name)
    indent -= 1
    apply_indent()


def print_for_statement(parent, transition_state_name):

    global mermaid_code
    global indent
    global indentation

    for for_statement_child in parent.children:
        if for_statement_child.type == "assignment_expression":
            initializer = for_statement_child.text.decode("utf-8")
            mermaid_code += (
                f"    {transition_state_name} : {indentation} for ({initializer}, "
            )
            indent += 1
            apply_indent()
        elif for_statement_child.type == "binary_expression":
            condition = for_statement_child.text.decode("utf-8")
            mermaid_code += f"{condition}, "
        elif for_statement_child.type == "update_expression":
            update = for_statement_child.text.decode("utf-8")
            mermaid_code += f"{update}) #colon; \n"
        elif for_statement_child.type == "statement":
            for statement_child in for_statement_child.children:
                if statement_child.type == "block":
                    for block_child in statement_child.children:
                        if block_child.type == "statement":
                            print_statement(block_child, transition_state_name)
    indent -= 1
    apply_indent()


def print_statement(parent, state_name):

    global mermaid_code
    global indent
    global indentation

    for statement_child in parent.children:
        # Looking for assignments
        if statement_child.type == "assignment_expression":
            consequence = statement_child.text.decode("utf-8")
            mermaid_code += f"    {state_name}: {indentation} {consequence}\n"
        # Looking for functions
        if statement_child.type == "call_expression":
            for call_expression_child in statement_child.children:
                if call_expression_child.type == "identifier":
                    function = call_expression_child.text.decode("utf-8")
                    if function == "delay":
                        consequence = statement_child.text.decode("utf-8")
                        mermaid_code += (
                            f"    {state_name}: {indentation} {consequence}\n"
                        )
        # Looking for if
        if statement_child.type == "if_statement":
            logging.debug("IF statement found")
            print_if_statement(statement_child, state_name)
        # Looking for while
        if statement_child.type == "while_statement":
            logging.debug("WHILE statement found")
            print_while_statement(statement_child, state_name)
        # Looking for for
        if statement_child.type == "for_statement":
            logging.debug("FOR statement found")
            print_for_statement(statement_child, state_name)


def apply_indent():

    global indent
    global indentation
    i = 0
    indentation = ""

    for i in range(indent):
        indentation += "#nbsp; #nbsp; "


def parse_snl(file_path):

    global mermaid_code
    global indent
    global indentation

    parserTree = Parser()
    parserTree.set_language(DB_LANGUAGE)

    try:

        with open(file_path, "r") as file:
            snl_content = file.read()

        tree = parserTree.parse(bytes(snl_content, "utf-8"))
        root_node = tree.root_node

        for child in root_node.children:
            # Looking for a new program
            if child.type == "program":
                logging.info("New program found")
                for program_child in child.children:
                    # Looking for a new state set
                    if program_child.type == "state_set":
                        logging.info("New state set found")
                        print_state_set(program_child)

    except FileNotFoundError:
        logging.exception("Error: File %s not found.", file_path)
    except Exception as e:
        logging.exception("Error: %s", e)


if __name__ == "__main__":

    Language.build_library(
        # Store the library in the `build` directory
        "build/my-languages.so",
        # Include one or more languages
        ["tree-sitter-epics/snl"],
    )

    DB_LANGUAGE = Language("build/my-languages.so", "snl")

    parser = argparse.ArgumentParser(
        prog="Plasma", description="PLAin State Machine Acquaintance"
    )
    parser = argparse.ArgumentParser(
        description="Script to create a stae diagram from a SNL state machine"
    )
    parser.add_argument("input_file", help="Input file, SNL format")
    parser.add_argument(
        "output_format",
        help="Output format, mermaid format or markdown format with Mermaid syntax. ",
        choices=["mmd", "md"],
    )
    parser.add_argument("output_file", help="Output file name")
    parser.add_argument(
        "-v",
        "--verbosity",
        type=int,
        choices=[0, 1, 2, 3, 4, 5],
        help="decrease output verbosity. 5 (Critical), 4 (Error), 3 (Warning, default), 2 (Info), 1 (Debug)",
    )

    args = parser.parse_args()
    arg_input = args.input_file
    arg_output = args.output_file
    arg_format = args.output_format

    if args.verbosity == None:
        arg_debug = logging.WARNING
    else:
        arg_debug = args.verbosity * 10

    logging.basicConfig(level=arg_debug)

    mermaid_code = ""

    if arg_format == "md":
        # Generate Mermaid diagram in markdown code
        mermaid_code += "```{mermaid}\n"

    mermaid_code += "stateDiagram\n"

    # Defining styling for diagram
    mermaid_code += (
        "    classDef state_set_style fill:#D3D3D3,stroke:black,color:black\n"
    )
    mermaid_code += "    classDef state_style fill:#FFFAAA,stroke:black,color:black\n"
    mermaid_code += (
        "    classDef transition_style fill:#CFFFA0,stroke:black,color:black\n"
    )

    indent = 0
    indentation = ""

    parse_snl(arg_input)

    if arg_format == "md":
        mermaid_code += "```\n"

    # Write Mermaid code to the specified output file
    with open(arg_output, "w") as output_file:
        output_file.write(mermaid_code)

    logging.info("Mermaid code written to %s", arg_output)
