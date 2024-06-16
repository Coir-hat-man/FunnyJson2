from abc import ABC, abstractmethod

# 节点类
class Node(ABC):
    def __init__(self, name, icon=''):
        self.name = name
        self.icon = icon

    @abstractmethod
    def show(self, visitor, prefix="", is_last=True):
        pass

# 中间节点类
class IntermediateNode(Node):
    def __init__(self, name, icon=''):
        super().__init__(name, icon)
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def show(self, visitor, prefix="", is_last=True):
        visitor.visit_intermediate_node(self, prefix, is_last)

# 叶子节点类
class LeafNode(Node):
    def __init__(self, name, icon=''):
        super().__init__(name, icon)

    def show(self, visitor, prefix="", is_last=True):
        visitor.visit_leaf_node(self, prefix, is_last)

class IconFactory(ABC):
    # @abstractmethod
    # def create_node(self,name,node_kind,icons):
    #     pass

    @abstractmethod
    def create_intermediate_node(self, name, icons):
        pass

    @abstractmethod
    def create_leaf_node(self, name, icons):
        pass

# 具体图标族工厂
class SimpleIconFactory(IconFactory):
    def create_intermediate_node(self, name, icons=None):
        return IntermediateNode(name, '')

    def create_leaf_node(self, name, icons=None):
        return LeafNode(name,'')

class PokerFaceFactory(IconFactory):
    def create_intermediate_node(self, name, icons=None):
        return IntermediateNode(name, '♢')

    def create_leaf_node(self, name, icons=None):
        return LeafNode(name, '♤')


# 访问者接口
class Visitor(ABC):
    @abstractmethod
    def visit_intermediate_node(self, node, prefix, is_last):
        pass

    @abstractmethod
    def visit_leaf_node(self, node, prefix, is_last):
        pass

# 具体访问者类
class TreeVisitor(Visitor):
    def visit_intermediate_node(self, node, prefix, is_last):
        # print(is_last)
        print(prefix + ('└─ ' if is_last else '├─ ') + node.icon + ' ' + node.name)

    def visit_leaf_node(self, node, prefix, is_last):
        # print(is_last)
        print(prefix + ('└─ ' if is_last else '├─ ') + node.icon + ' ' + node.name)


class RectangleVisitor(Visitor):
    def __init__(self, max_width=50):
        self.max_width = max_width

    def visit_intermediate_node(self, node, prefix, is_last):
        # is_last==2表示第一行，
        if is_last==2:
            position = 0
        elif '├─' in prefix or '┌' in prefix:
            position = 1
        elif '└─' in prefix:
            position = 2
        else:
            position = 1

        if position == 0:
            line = prefix + '┌ ' + node.icon + ' ' + node.name
            if self.max_width > 0:
                line += ' ' + '─' * (self.max_width - len(line)) + '┐'
        else:
            line = prefix + '├─ ' + node.icon + ' ' + node.name
            if self.max_width > 0:
                line += ' ' + '─' * (self.max_width - len(line)) + '┤'
        # print(is_last)
        print(line)


    def visit_leaf_node(self, node, prefix, is_last):
        position=2 if is_last else 0
        if position == 2:
            new_prefix = '└' + '─' * (len(prefix) - len('└'))
            line = new_prefix + '┴ ' + node.icon + ' ' + node.name
            if self.max_width > 0:
                line += ' ' + '─' * (self.max_width - len(line)) + '┘'
        else:
            line = prefix + '├─ ' + node.icon + ' ' + node.name
            if self.max_width > 0:
                line += ' ' + '─' * (self.max_width - len(line)) + '┤'
        print(line)


# 迭代器接口
class Iterator(ABC):
    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def has_next(self):
        pass


class RectangleIterator(Iterator):
    def __init__(self, root):
        self.stack = [(root, "", 0)]  # Stack contains tuples of (node, prefix, is_last)
        self.root=root

    def next(self):
        if self.has_next():
            node, prefix, is_last = self.stack.pop()
            flag=False
            if(len(self.stack))==0:
                flag=True
            if isinstance(node, IntermediateNode):
                for i in range(len(node.children) - 1, -1, -1):
                    child = node.children[i]
                    is_kind=flag and (i == len(node.children) - 1)
                    if node==self.root and i==0:
                        is_kind=2
                    if node!=self.root:
                        new_prefix = prefix + ('│   ' if is_kind!=1 else '    ')
                    else:
                        new_prefix=prefix
                    self.stack.append((child, new_prefix, is_kind))
                    # print(child.name,new_prefix,is_kind)
            return node, prefix, is_last
        return None

    def has_next(self):
        return len(self.stack) > 0

# 树的具体迭代器类
class TreeIterator(RectangleIterator):
    def next(self):
        if self.has_next():
            node, prefix, is_last = self.stack.pop()
            if isinstance(node, IntermediateNode):
                for i in range(len(node.children) - 1, -1, -1):
                    child = node.children[i]
                    is_kind=(i == len(node.children) - 1)
                    if node!=self.root:
                        new_prefix = prefix + ('│   ' if is_last==False else '    ')
                    else:
                        new_prefix=prefix
                    self.stack.append((child, new_prefix, is_kind))

            return node, prefix, is_last
        return None


class Builder(ABC):
    @abstractmethod
    def build(self, json_data):
        pass

class TreeBuilder(Builder):
    def __init__(self, icon_factory):
        self.icon_factory = icon_factory
        self.root = None

    def build(self, json_data):
        self.root = self.icon_factory.create_intermediate_node('root')
        self.build_recursive(json_data, self.root)
        return self.root

    def build_recursive(self, json_data, parent_node):
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if value is None:
                    leaf_node = self.icon_factory.create_leaf_node(key)
                    parent_node.add_child(leaf_node)
                elif isinstance(value, (dict, list)):
                    child_node = self.icon_factory.create_intermediate_node(key)
                    parent_node.add_child(child_node)
                    self.build_recursive(value, child_node)
                else:
                    leaf_node = self.icon_factory.create_leaf_node(f'{key}: {str(value)}')
                    parent_node.add_child(leaf_node)
        elif isinstance(json_data, list):
            for i, item in enumerate(json_data):
                if item is None:
                    leaf_node = self.icon_factory.create_leaf_node(f'Item {i}')
                    parent_node.add_child(leaf_node)
                elif isinstance(item, (dict, list)):
                    child_node = self.icon_factory.create_intermediate_node(f'Item {i}')
                    parent_node.add_child(child_node)
                    self.build_recursive(item, child_node)
                else:
                    leaf_node = self.icon_factory.create_leaf_node(f'Item {i}: {str(item)}')
                    parent_node.add_child(leaf_node)
        else:
            if json_data is not None:
                leaf_node = self.icon_factory.create_leaf_node(str(json_data))
                parent_node.add_child(leaf_node)

    def show(self, visitor):
        iterator = TreeIterator(self.root)
        while iterator.has_next():
            node, prefix, is_last = iterator.next()
            # print(is_last)
            if node!=self.root:
                if (isinstance(node, IntermediateNode)):
                    visitor.visit_intermediate_node(node, prefix, is_last)
                else:
                    visitor.visit_leaf_node(node, prefix, is_last)


class RectangleBuilder(TreeBuilder):
    def show(self,visitor):
        iterator = RectangleIterator(self.root)
        while iterator.has_next():
            node, prefix, is_last = iterator.next()
            # print(is_last)
            if node != self.root:
                if(isinstance(node,IntermediateNode)):
                    visitor.visit_intermediate_node(node,prefix,is_last)
                else:
                    visitor.visit_leaf_node(node,prefix,is_last)