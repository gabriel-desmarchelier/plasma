#!/usr/bin/env python

from tree_sitter import Language, Parser
import argparse
import logging

def print_if_statement(parent, transition_state_name):

    global mermaid_code

    print(parent)
    for if_statement_child in parent.children:
        if if_statement_child.type == 'binary_expression':
            condition = if_statement_child.text.decode('utf-8')
            mermaid_code += f"    {transition_state_name} : if {condition} #colon; \n"
        elif if_statement_child.type == 'statement':
            for statement_child in if_statement_child.children :
                if statement_child.type == 'block' :
                    for block_child in statement_child.children :
                        if block_child.type == 'statement':
                            print_statement(block_child,transition_state_name)
        # Looking for an else
        elif if_statement_child.type == 'else_statement':
            for else_statement_child in if_statement_child.children :
                if else_statement_child.type == 'statement':
                    for statement_child in else_statement_child.children :
                        # Looking for "else if" statements
                        if statement_child.type == 'if_statement':
                            print_else_if_statement(statement_child,transition_state_name) 
                        elif statement_child.type == 'block' :
                            print ("that's just an else")
                            mermaid_code += f"    {transition_state_name} : else #colon; \n"
                            for block_child in statement_child.children :
                                if block_child.type == 'statement':
                                    print_statement(block_child,transition_state_name)


def print_else_if_statement(parent, transition_state_name):

    global mermaid_code

    print("thats an elif")
    for if_statement_child in parent.children:
        # Looking for condition of the if
        if if_statement_child.type == 'binary_expression':
            condition = if_statement_child.text.decode('utf-8')
            mermaid_code += f"    {transition_state_name} : else if {condition} #colon; \n"
        elif if_statement_child.type == 'statement':
            for statement_child in if_statement_child.children :
                if statement_child.type == 'block' :
                    for block_child in statement_child.children :
                        if block_child.type == 'statement':
                            print_statement(block_child,transition_state_name)
        # Looking for an else
        elif if_statement_child.type == 'else_statement':
            for else_statement_child in if_statement_child.children :
                if else_statement_child.type == 'statement':
                    for statement_child in else_statement_child.children :
                        # Looking for another if after the else
                        if statement_child.type == 'if_statement':
                            print_else_if_statement(statement_child,transition_state_name)
                        if statement_child.type == 'block' :
                            print ("that's just an else after an elif")
                            mermaid_code += f"    {transition_state_name} : else #colon; \n"
                            for block_child in statement_child.children :
                                if block_child.type == 'statement':
                                    print_statement(block_child,transition_state_name)

def print_while_statement(parent, transition_state_name):

    global mermaid_code

    for while_statement_child in parent.children:
        if while_statement_child.type == 'binary_expression':
            condition = while_statement_child.text.decode('utf-8')
            mermaid_code += f"    {transition_state_name} : while {condition} #colon; \n"
        elif while_statement_child.type == 'statement':
            for statement_child in while_statement_child.children :
                if statement_child.type == 'block' :
                    for block_child in statement_child.children :
                        if block_child.type == 'statement':
                            print_statement(block_child,transition_state_name)

def print_for_statement(parent, transition_state_name):

    global mermaid_code
    print("for!!")
    for for_statement_child in parent.children:
        print(for_statement_child)
        if for_statement_child.type == 'assignment_expression':
            initializer = for_statement_child.text.decode('utf-8')
            mermaid_code += f"    {transition_state_name} : for ({initializer}, "
        elif for_statement_child.type == 'binary_expression':
            condition = for_statement_child.text.decode('utf-8')
            mermaid_code += f"{condition}, "
        elif for_statement_child.type == 'update_expression':
            update = for_statement_child.text.decode('utf-8')
            mermaid_code += f"{update}) #colon; \n"
        elif for_statement_child.type == 'statement':
            for statement_child in for_statement_child.children :
                if statement_child.type == 'block' :
                    for block_child in statement_child.children :
                        if block_child.type == 'statement':
                            print_statement(block_child,transition_state_name)

def print_statement(parent, state_name):

    global mermaid_code

    #print ("printing actions")
    for statement_child in parent.children:
        print(statement_child.type)
        # Looking for assignments
        if statement_child.type == 'assignment_expression':
            consequence = statement_child.text.decode('utf-8')
            mermaid_code += f"    {state_name}: #nbsp; #nbsp; {consequence}\n"
        # Looking for functions
        if statement_child.type == 'call_expression':
            for call_expression_child in statement_child.children :
                if call_expression_child.type == 'identifier' :
                    function = call_expression_child.text.decode('utf-8')
                    if function == 'delay' :
                        consequence = statement_child.text.decode('utf-8')
                        mermaid_code += f"    {state_name}: #nbsp; #nbsp; {consequence}\n"
        # Looking for if
        if statement_child.type == 'if_statement':
            print_if_statement(statement_child,state_name)
        # Looking for while
        if statement_child.type == 'while_statement':
            print_while_statement(statement_child,state_name)
        # Looking for for
        if statement_child.type == 'for_statement':
            print("for in a statement")
            print_for_statement(statement_child,state_name)

def parse_snl(file_path):

    global mermaid_code

    parserTree = Parser()
    parserTree.set_language(DB_LANGUAGE)

    try:
        #with open(file_path, 'r') as f:
        #    snl_content = f.readlines()

        with open(file_path, 'r') as file:
            snl_content = file.read()

        tree = parserTree.parse(bytes(snl_content, 'utf-8'))
        root_node = tree.root_node

        

        state_name=""
        entry=""
        entry_action=""
        transition=""
        transition_actions=""

        for child in root_node.children:
            # Looking for a new program
            if child.type == 'program':
                print("New program")
                for program_child in child.children:
                    # Looking for a new state set
                    if program_child.type == 'state_set':
                        print("New ss")
                        for state_set_child in program_child.children :
                            # Looking for a new state
                            if state_set_child.type == 'state':
                                for state_child in state_set_child.children:
                                    # Looking for the state name
                                    if state_child.type == 'identifier':
                                        state_name=state_child.text.decode('utf-8')
                                        mermaid_code += f"    {state_name}:::state_style\n"
                                        mermaid_code += f"    {state_name} : {state_name}\n"
                                    elif state_child.type == 'state_block':
                                        transition_state_id = 0
                                        for state_block_child in state_child.children:
                                            # Looking for the entry in the state
                                            if state_block_child.type == 'entry':
                                                for entry_child in state_block_child.children:
                                                    if entry_child.type == 'block':
                                                        for entry_block_child in entry_child.children:
                                                            # Looking for the statements in the entry block
                                                            if entry_block_child.type == 'statement':
                                                                print_statement(entry_block_child,state_name)
                                            # Looking for "when"
                                            elif state_block_child.type == 'transition':
                                                transition_state_id += 1
                                                transition_state_name = state_name+"_transition_"+str(transition_state_id)
                                                mermaid_code += f"    {transition_state_name}:::transition_style\n"
                                                mermaid_code += f"    {state_name} -->{transition_state_name}\n"
                                                for transition_child in state_block_child.children :
                                                    # Looking for transition condition
                                                    if transition_child.type == 'binary_expression':
                                                        condition=transition_child.text.decode('utf-8')
                                                        mermaid_code += f"    {transition_state_name} : when {condition}\n"
                                                    # Looking for transition actions
                                                    elif transition_child.type == 'block' :
                                                        for transition_block_child in transition_child.children :
                                                            if transition_block_child.type == 'statement':
                                                                for statement_child in transition_block_child.children:
                                                                    # Looking for assignments
                                                                    if statement_child.type == 'assignment_expression':
                                                                        consequence = statement_child.text.decode('utf-8')
                                                                        mermaid_code += f"    {transition_state_name}: {consequence}\n"
                                                                    # Looking for functions
                                                                    if statement_child.type == 'call_expression':
                                                                        for call_expression_child in statement_child.children :
                                                                            if call_expression_child.type == 'identifier' :
                                                                                function = call_expression_child.text.decode('utf-8')
                                                                                print(function)
                                                                                if function == 'delay' :
                                                                                    consequence = statement_child.text.decode('utf-8')
                                                                                    mermaid_code += f"    {transition_state_name}: {consequence}\n"
                                                                    # Looking for "if" statements
                                                                    elif statement_child.type == 'if_statement':
                                                                        print_if_statement(statement_child,transition_state_name)
                                                                    #    print(statement_child)
                                                                    #    for if_statement_child in statement_child.children:
                                                                    #        if if_statement_child.type == 'binary_expression':
                                                                    #            condition = if_statement_child.text.decode('utf-8')
                                                                    #            mermaid_code += f"    {transition_state_name} : if {condition} #colon; \n"
                                                                    #        elif if_statement_child.type == 'statement':
                                                                    #            for statement_child in if_statement_child.children :
                                                                    #                if statement_child.type == 'block' :
                                                                    #                    for block_child in statement_child.children :
                                                                    #                        if block_child.type == 'statement':
                                                                    #                            print_statement(block_child,transition_state_name)
                                                                    #        # Looking for an else
                                                                    #        elif if_statement_child.type == 'else_statement':
                                                                    #            for else_statement_child in if_statement_child.children :
                                                                    #                if else_statement_child.type == 'statement':
                                                                    #                    for statement_child in else_statement_child.children :
                                                                    #                        # Looking for "else if" statements
                                                                    #                        if statement_child.type == 'if_statement':
                                                                    #                            print_else_if_statement(statement_child,transition_state_name) 
                                                                    #                        elif statement_child.type == 'block' :
                                                                    #                            print ("that's just an else")
                                                                    #                            mermaid_code += f"    {transition_state_name} : else #colon; \n"
                                                                    #                            for block_child in statement_child.children :
                                                                    #                                if block_child.type == 'statement':
                                                                    #                                    print_statement(block_child,transition_state_name)

                                                                    # Looking for "while" statements
                                                                    elif statement_child.type == 'while_statement':
                                                                        print_while_statement(statement_child,transition_state_name)
                                                                    #    for while_statement_child in statement_child.children:
                                                                    #        print()
                                                                    #        if while_statement_child.type == 'binary_expression':
                                                                    #            condition = while_statement_child.text.decode('utf-8')
                                                                    #            mermaid_code += f"    {transition_state_name} : while {condition} #colon; \n"
                                                                    #        elif while_statement_child.type == 'statement':
                                                                    #            for statement_child in while_statement_child.children :
                                                                    #                if statement_child.type == 'block' :
                                                                    #                    for block_child in statement_child.children :
                                                                    #                        if block_child.type == 'statement':
                                                                    #                            print_statement(block_child,transition_state_name)
                                                                            ## Looking for "if" statements
                                                                            #elif while_statement_child.type == 'if_statement':
                                                                            #    print("there's an if in a wile !")
                                                                            #    print_if_statement(while_statement_child,statement_child,transition_state_name)

                                                                    # Looking for "for" statements
                                                                    elif statement_child.type == 'for_statement':
                                                                        print_for_statement(statement_child,transition_state_name)
                                                                    #    for for_statement_child in statement_child.children:
                                                                    #        if for_statement_child.type == 'assignment_expression':
                                                                    #            initializer = for_statement_child.text.decode('utf-8')
                                                                    #            mermaid_code += f"    {transition_state_name} : for ({initializer}, "
                                                                    #        elif for_statement_child.type == 'binary_expression':
                                                                    #            condition = for_statement_child.text.decode('utf-8')
                                                                    #            mermaid_code += f"{condition}, "
                                                                    #        elif for_statement_child.type == 'update_expression':
                                                                    #            update = for_statement_child.text.decode('utf-8')
                                                                    #            mermaid_code += f"{update}) #colon; \n"
                                                                    #        elif for_statement_child.type == 'statement':
                                                                    #            for statement_child in for_statement_child.children :
                                                                    #                if statement_child.type == 'block' :
                                                                    #                    for block_child in statement_child.children :
                                                                    #                        if block_child.type == 'statement':
                                                                    #                            print_statement(block_child,transition_state_name)


                                                    elif transition_child.type == 'identifier' :
                                                        link_name = transition_child.text.decode('utf-8')
                                                        mermaid_code += f"    {transition_state_name} -->{link_name}\n"
                                                        transition_actions=""

        

    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":

    Language.build_library(
    # Store the library in the `build` directory
    "build/my-languages.so",
    # Include one or more languages
    ["tree-sitter-epics/snl"]
    )

    DB_LANGUAGE = Language("build/my-languages.so", "snl")


    parser = argparse.ArgumentParser(prog='Plasma',
                                 description='PLAin State Machine Acquaintance')
    parser = argparse.ArgumentParser(
        description='Script to create a stae diagram from a SNL state machine')
    parser.add_argument('input_file', help='Input file, SNL format')
    parser.add_argument('output_file', help='Output file, markdown format with Mermaid syntax')
    parser.add_argument("-v",
                        "--verbosity",
                        type=int,
                        choices=[0, 1, 2, 3, 4, 5],
                        help="decrease output verbosity. 5 (Critical), 4 (Error), 3 (Warning, default), 2 (Info), 1 (Debug)")

    args = parser.parse_args()
    arg_input = args.input_file
    arg_output = args.output_file

    if (args.verbosity == None):
        arg_debug = logging.WARNING
    else:
        arg_debug = args.verbosity * 10

    logging.basicConfig(level=arg_debug)

    # Generate Mermaid diagram code
    mermaid_code = "```mermaid\n"
    mermaid_code += "stateDiagram\n"
    
    # Defining styling for diagram
    mermaid_code += "    classDef state_style fill:#FFFAAA,stroke:black,color:black\n"
    mermaid_code += "    classDef transition_style fill:#CFFFA0,stroke:black,color:black\n"

    parse_snl(arg_input)

    mermaid_code += "```\n"

    # Write Mermaid code to the specified output file
    with open(arg_output, 'w') as output_file:
        output_file.write(mermaid_code)

    print(f"Mermaid code written to {arg_output}")
    