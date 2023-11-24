#!/usr/bin/env python

import re
import sys

def parse_snl(file_path, output_file_path):
    try:
        with open(file_path, 'r') as f:
            snl_content = f.readlines()

        # Generate Mermaid diagram code
        mermaid_code = "```mermaid\n"
        mermaid_code += "stateDiagram\n"

        state_name=""
        entry=""
        entry_action=""
        transition=""
        transition_actions=""
        for line in snl_content:
            print(line)
            # Looking for new state
            m = re.search(r'^(\s)*state(\s)+(?P<state_name>.*)', line)
            if m is not None:
                state_name=m.group('state_name')
                mermaid_code += f"    {state_name} : {state_name}\n"
                continue
            # Looking for entry actions of the state
            m = re.search(r'^(\s)*entry.*', line)
            if m is not None:
                entry=True
                print("entry starts")
                continue
            # If entry has been found, entry actions need to be written into the diagram
            if entry is True:
                # Do not do anything for lines starting with opening brace
                m = re.search(r'^(\s)*{.*', line)
                if m is not None:
                    print(line)
                    continue
                # Do not write entry actions including "pvPut"
                m = re.search(r'^(\s)*pvPut(.)*', line)
                if m is not None:
                    print(line)
                    continue
                # Do not write anything for lines starting with closing brace
                m = re.search(r'^(\s)*}.*', line)
                if m is not None:
                    print(line)
                    # The closing brace marks the end of the entry actions
                    entry=False
                    print("entry ends")
                    continue
                # If none of the above conditions is matched, then we have an entry action to be written in the diagram
                m = re.search(r'^(\s)*(?P<entry_action>.*);', line)
                if m is not None:
                    print(line)
                    print("entry action found")
                    entry_action = m.group("entry_action")
                    mermaid_code += f"    {state_name} : {entry_action}\n"
                    continue
                # Do not do anything for other lines (e.g. blank lines)
                else:
                    continue
            # Looking for "when" conditions
            m = re.search(r'^(\s)*when(\s)+(?P<condition>.*)', line)
            if m is not None:
                condition=m.group('condition')
                transition=True
                print("transiton starts")
                continue
            if transition is True:
                # If the "state" statement appears, it marks the end of the transition actions
                m = re.search(r'^(.)*}(\s)state+(?P<link_name>.*)', line)
                if m is not None:
                    print(line)
                    link_name=m.group('link_name')
                    mermaid_code += f"    {state_name} -->{link_name}: when {condition} "
                    if (len(transition_actions) != 0):
                        mermaid_code += f"do {transition_actions}\n"
                    else:
                        mermaid_code += f"\n"
                    transition_actions=""
                    transition=False
                    print("transition ends")
                    continue
                # Do not do anything for lines starting with only opening brace
                m = re.search(r'^(\s)*{(\s)*$', line)
                if m is not None:
                    print(line)
                    continue
                # Do not write transition actions including "pvPut"
                m = re.search(r'^(\s)*pvPut(.)*', line)
                if m is not None:
                    print(line)
                    continue
                # Do not write anything for lines starting with closing brace
                m = re.search(r'^(\s)*}.*', line)
                if m is not None:
                    print(line)
                    # The closing brace marks the end of the transition actions
                    continue
                # If none of the above conditions is matched, then we have an transition action to be written in the diagram
                m = re.search(r'^(\s)*(?P<transition_action>.*);', line)
                if m is not None:
                    print(line)
                    print("transition action found")
                    transition_actions += m.group("transition_action") + " "
                    print(transition_actions)
                    continue
                # Do not do anything for other lines (e.g. blank lines)
                else:
                    continue

        mermaid_code += "```\n"

        # Write Mermaid code to the specified output file
        with open(output_file_path, 'w') as output_file:
            output_file.write(mermaid_code)

        print(f"Mermaid code written to {output_file_path}")

    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./script.py path/to/your_file.st path/to/output_diagram.md")
        sys.exit(1)

    snl_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    parse_snl(snl_file_path, output_file_path)

