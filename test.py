from pptree import *

class Node():
    def __init__(self, value=None):
        self.value = value
        self.left = None
        self.right = None

root = Node(1)
root.left = Node(2)
root.right = Node(3)



print_tree(root, horizontal=False)