import sqlparse
import re
from graphviz import Digraph
import os

def generate_er_diagram(sql_content, dot_file_path, output_image_path):
    # Initialize graph
    dot = Digraph(comment='ER Diagram')
    dot.attr(rankdir='LR')  # Left to right layout
    
    # Parse SQL content
    parsed = sqlparse.parse(sql_content)
    
    tables = {}
    foreign_keys = []

    # Extract tables and their foreign keys
    for statement in parsed:
        if statement.get_type() == 'CREATE':
            table_name = re.search(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?`?(\w+)`?', str(statement), re.IGNORECASE)
            if table_name:
                table_name = table_name.group(1)
                tables[table_name] = True

                # Extract foreign keys
                fks = re.findall(r'FOREIGN KEY\s*\(`?(\w+)`?\)\s*REFERENCES\s*`?(\w+)`?\s*\(`?(\w+)`?\)', str(statement), re.IGNORECASE)
                for fk in fks:
                    foreign_keys.append((table_name, fk[0], fk[1], fk[2]))

    # Add tables to the graph
    for table_name in tables:
        dot.node(table_name, label=table_name, shape='box')

    # Add foreign key relationships to the graph
    for (from_table, from_column, to_table, to_column) in foreign_keys:
        dot.edge(from_table, to_table, label=f"{from_column} -> {to_column}", fontsize='10')

    # Save DOT file
    dot.save(dot_file_path)

    # Render the DOT file to an image
    dot.render(filename=output_image_path, format='png', cleanup=True)

# Define the paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
public_diagrams_dir = os.path.join(project_root, 'public', 'diagrams')

# Ensure the public/diagrams directory exists
os.makedirs(public_diagrams_dir, exist_ok=True)

# Read SQL file content
sql_file_path = 'C:/Users/aarus/Downloads/Sample100rows.sql'
with open(sql_file_path, 'r', encoding='utf-8') as file:
    sql_content = file.read()

# Generate unique filenames based on the input SQL file name
sql_file_name = os.path.basename(sql_file_path)
base_name = os.path.splitext(sql_file_name)[0]

# Generate DOT file and ER diagram image
dot_file_path = os.path.join(public_diagrams_dir, f'{base_name}.dot')
output_image_path = os.path.join(public_diagrams_dir, base_name)

generate_er_diagram(sql_content, dot_file_path, output_image_path)

print(f"ER diagram saved as {output_image_path}.png")
print(f"DOT file saved as {dot_file_path}")