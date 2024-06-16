import json
from utils import *

def load_icon_factories(config_file):
    with open(config_file, 'r', encoding='utf-8') as file:
        config = json.load(file)

    factories = {}
    map={}
    choices=[]
    for factory_name, icons  in config.items():
        choices.append(icons['name'])

        factories[factory_name] = type(
            factory_name,
            (IconFactory,),
            {
                'create_intermediate_node': lambda name, icons=icons: (
                    IntermediateNode(name, icons['inter'])
                ),
                'create_leaf_node': lambda name, icons=icons: (
                    LeafNode(name, icons['leaf'])
                )
            }
        )
        map[icons['name']] = factories[factory_name]
    return factories,map,choices


