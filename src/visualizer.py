import graphviz
from typing import List, Dict, Any

def create_graph(modules: List[Dict[str, Any]]) -> graphviz.Digraph:
    dot = graphviz.Digraph(comment='Module Hierarchy')
    dot.attr(rankdir='LR')
    
    for module in modules:
        module_name = module.get('module', 'Unknown Module')
        dot.node(module_name, module_name, shape='box', style='filled', fillcolor='lightblue')
        
        submodules = module.get('Submodules', {})
        for sub_name, sub_desc in submodules.items():
            dot.node(sub_name, sub_name, shape='ellipse')
            dot.edge(module_name, sub_name)
            
    return dot
