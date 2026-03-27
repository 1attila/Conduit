from mconduit.utils.tree_printer import draw_tree


tree = {
    "hello": {
        "test": "ok",
            "nop": {"cde", "fgh"},
            "not_ok": "abc"
    }   ,
    "world": {}
}


for t in draw_tree(tree):
    print(t)