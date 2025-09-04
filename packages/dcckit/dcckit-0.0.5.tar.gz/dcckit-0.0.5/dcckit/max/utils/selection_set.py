from pymxs import runtime as rt


class SelectionSet(object):
    def __init__(self, name, create_if_invalid=False):
        """
        Wrapper for working with selection sets.

        Args:
            name (str): The name of the selection set to work with
        Kwargs:
            create_if_invalid (bool): Should a selection set be created if it does not exist?
        """
        self._name = name

        # MAXScript has various perf issues when accessing and working
        # with selection sets, so cache where possible
        self.native_ss = None
        if len(rt.selectionSets):
            for i in rt.selectionSets:
                if i.name == name:
                    self.native_ss = i
                    break

    def __new__(cls, name, create_if_invalid=False, *args, **kwargs):
        """
        Creates a new instance of the SelectionSet wrapper.

        Note: See `__init__` for input args/kwargs
        """
        output = None
        exists = False
        for i in rt.selectionSets:
            if name == i.name:
                exists = True
                break

        # Create a new selection set if it does not exist
        if not exists and create_if_invalid:
            rt.selectionSets[name] = rt.array()
            exists = True

        if exists:
            output = super(SelectionSet, cls).__new__(cls, *args, **kwargs)

        return output

    @property
    def name(self) -> str:
        """
        Returns:
            str: The name of this selection set
        """
        return self.native_ss.name

    @name.setter
    def name(self, new_name: str):
        """
        Sets the name of this selection set and reinitializes this object reference

        Args:
            new_name (str): The new name to set
        """
        self.native_ss.name = new_name
        self._name = new_name

    @property
    def nodes(self) -> list:
        """
        Gets all nodes contained in this set

        Returns:
            list: All nodes in this set
        """
        output = []
        if self.native_ss:
            for i in self.native_ss:
                output.append(i)
        return output

    def add_node(self, node: rt.Node):
        """
        Add a node to this selection set

        Args:
            node (Node): The node to add
        """
        current_nodes = self.nodes
        current_nodes.append(node)
        current_nodes_ms = rt.array()
        [rt.append(current_nodes_ms, x) for x in current_nodes]
        rt.selectionSets[self.name] = current_nodes_ms

    def add_nodes(self, nodes: list):
        """
        Add a list of nodes to this selection set

        Args:
            nodes (List[Node]): The nodes to add
        """
        for i in nodes:
            self.add_node(i)

    def remove_node(self, node: rt.Node):
        """
        Removes a node from this selection set

        Args:
            node (Node): The node
        """
        current_nodes = self.nodes
        if node in current_nodes:
            current_nodes.remove(node)
            current_nodes_ms = rt.array()
            [rt.append(current_nodes_ms, x) for x in current_nodes]
            rt.selectionSets[self.name] = current_nodes_ms

    def remove_nodes(self, nodes: list):
        """
        Remove a list of nodes from this selection set

        Args:
            nodes (List[Node]): The nodes to remove
        """
        for i in nodes:
            self.remove_node(i)

    # -----------------------------------------------------------------------

    def as_json(self) -> dict:
        """
        Attempts to convert the name of this selection set to a valid json dict.

        Useful for storing parameters or metadata within the selection set name.

        Returns:
            dict: The name as a json dict - else None
        """
        try:
            output = eval(self.name)
            if type(output) is dict:
                return output
        except Exception:
            pass
        return None

    @property
    def is_valid_json(self) -> bool:
        """
        Gets whether this selection set name is a valid json dictionary.

        Returns:
            bool: True if valid - else False
        """
        return self.as_json() is not None


def get_selection_set_names() -> list:
    """
    Gets the names of all selection sets in the current scene.

    Returns:
        list: The names of all selection sets
    """
    output = []
    if len(rt.SelectionSets):
        for i in rt.selectionSets:
            output.append(i.name)
    return output
