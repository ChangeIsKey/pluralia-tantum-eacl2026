import json
from anytree import Node, RenderTree
from anytree.search import findall

def get_sense_tree(senses, tree):
    senses_names = senses.keys()
    try:
        senses_names = [int(s) for s in senses_names]
    except:
        pass
    for sense_name in sorted(senses_names):
        sense = senses[str(sense_name)]
        node = Node(sense_name, sense_id=sense['sense_label'], parent=tree)
        if 'sub-senses' in sense:
            get_sense_tree(sense['sub-senses'], node)
    return tree

def assign_ids(node, prefix=""):
    # Assign a number to each child at this level
    for idx, child in enumerate(node.children, 1):
        # Top level: just numbers (1, 2, 3, ...)
        if not prefix:
            child.name = f"{idx}"
        else:
            # Deeper levels: prefix with parent id and format with leading zeros
            child.name = f"{prefix}.{idx:02d}"
        # Recurse
        assign_ids(child, child.name)

form2tree = {}
form2lemma = {}
lemma2forms = {}
with open('english/sing2plur.jsonl') as f:
    for line in f:
        line = json.loads(line)
        lemma = '_'.join(line['lemma_id'].split('_')[:-1])
        for form in line['singular_forms']:
            if not lemma in lemma2forms:
                lemma2forms[lemma] = set()
            lemma2forms[lemma].add(form)
            form2tree[form] = None
            form2lemma[form] = lemma
        for form in line['plural_forms']:
            if not lemma in lemma2forms:
                lemma2forms[lemma] = set()
            lemma2forms[lemma].add(form)
            form2tree[form] = None
            form2lemma[form] = lemma

with open('/mimer/NOBACKUP/groups/cik_data/cassotti/oed_data/lemma2senses.txt') as f:
        for line in f:
            line = json.loads(line)
            lemma = line['lemma'].split('_')
            lemma_pos = lemma[-1].lower()
            if lemma_pos == 'nn':
                lemma = '_'.join(lemma[:-1])
                if lemma in form2tree:
                    root = Node(lemma+'_'+lemma_pos, sense_id="")
                    tree = get_sense_tree(line['senses'], root)
                    form2tree[lemma] = tree


with open('temp_en_dict.txt','w+') as g:
    for lemma in lemma2forms:
        trees = [form2tree[l] for l in lemma2forms[lemma] if not form2tree[l] == None]
        
        # Create a new common root for all
        new_root = Node(lemma, sense_id="")

        for tree in trees:
            tree.parent = new_root


        # Assign hierarchical IDs
        assign_ids(new_root)

        g.write(lemma+'\n')
    
        # First assign IDs starting from root
        root.my_id = "0"  # Root gets a base id; will not be printed if undesired
        assign_ids(root)

        for pre, fill, node in RenderTree(new_root):
            if not node.__dict__['sense_id'] == '':      
                lemma_id = node.__dict__['sense_id'].split('-')[0]
                g.write(f"{node.name}\t{node.__dict__['sense_id']}\n")

        g.write('\n\n')