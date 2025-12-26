import graphviz
from typing import List, Dict, Any

def create_graph(modules: List[Dict[str, Any]]) -> graphviz.Digraph:
    dot = graphviz.Digraph(comment='Module Hierarchy')
    dot.attr(rankdir='LR', splines='ortho')
    dot.attr('node', shape='box', style='filled', fontname='Helvetica')
    
    for i, module in enumerate(modules):
        module_name = module.get('module', f'Module {i+1}')
        # Main Module Node
        dot.node(module_name, module_name, fillcolor='#4F8BF9', fontcolor='white', fontsize='12')
        
        submodules = module.get('Submodules', {})
        for sub_name, sub_desc in submodules.items():
            # Submodule Node
            # Create a unique ID for the node to avoid conflicts if names are same across modules
            sub_id = f"{module_name}_{sub_name}"
            label = f"{sub_name}\n({sub_desc[:30]}...)" if len(sub_desc) > 30 else sub_name
            
            dot.node(sub_id, label, shape='note', fillcolor='#e1e4e8', fontcolor='black', fontsize='10')
            dot.edge(module_name, sub_id, color='#666666')
            
    return dot
