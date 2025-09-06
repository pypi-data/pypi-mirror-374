import itertools
import typing

import pytest

import pygambit as gbt

from . import games


def test_get_infoset():
    """Test to ensure that we can retrieve an infoset for a given node"""
    game = games.read_from_file("basic_extensive_game.efg")
    assert game.root.infoset is not None
    assert game.root.children[0].infoset is not None
    assert game.root.children[0].children[1].children[0].infoset is None


def test_get_outcome():
    """Test to ensure that we can retrieve an outcome for a given node"""
    game = games.read_from_file("basic_extensive_game.efg")
    assert game.root.children[0].children[1].children[0].outcome == game.outcomes[1]
    assert game.root.outcome is None


def test_get_player():
    """Test to ensure that we can retrieve a player for a given node"""
    game = games.read_from_file("basic_extensive_game.efg")
    assert game.root.player == game.players[0]
    assert game.root.children[0].children[1].children[0].player is None


def test_get_game():
    """Test to ensure that we can retrieve the game object from a given node"""
    game = games.read_from_file("basic_extensive_game.efg")
    assert game == game.root.game


def test_get_parent():
    """Test to ensure that we can retrieve a parent node for a given node"""
    game = games.read_from_file("basic_extensive_game.efg")
    assert game.root.children[0].parent == game.root
    assert game.root.parent is None


def test_get_prior_action():
    """Test to ensure that we can retrieve the prior action for a given node"""
    game = games.read_from_file("basic_extensive_game.efg")
    assert game.root.children[0].prior_action == game.root.infoset.actions[0]
    assert game.root.prior_action is None


def test_get_prior_sibling():
    """Test to ensure that we can retrieve a prior sibling of a given node"""
    game = games.read_from_file("basic_extensive_game.efg")
    assert game.root.children[1].prior_sibling == game.root.children[0]
    assert game.root.children[0].prior_sibling is None


def test_get_next_sibling():
    """Test to ensure that we can retrieve a next sibling of a given node"""
    game = games.read_from_file("basic_extensive_game.efg")
    assert game.root.children[0].next_sibling == game.root.children[1]
    assert game.root.children[1].next_sibling is None


def test_is_terminal():
    """Test to ensure that we can check if a given node is a terminal node"""
    game = games.read_from_file("basic_extensive_game.efg")
    assert game.root.is_terminal is False
    assert game.root.children[0].children[0].children[0].is_terminal is True


def test_is_successor_of():
    """Test to ensure that we can check if a given node is a
    successor of a supplied node
    """
    game = games.read_from_file("basic_extensive_game.efg")
    assert game.root.children[0].is_successor_of(game.root)
    assert not game.root.is_successor_of(game.root.children[0])
    with pytest.raises(TypeError):
        game.root.is_successor_of(9)
    with pytest.raises(TypeError):
        game.root.is_successor_of("Test")
    with pytest.raises(TypeError):
        game.root.is_successor_of(game.players[0])


def test_is_subgame_root():
    """Test whether nodes are correctly labeled as roots of proper subgames."""
    game = games.read_from_file("basic_extensive_game.efg")
    assert game.root.is_subgame_root
    assert not game.root.children[0].is_subgame_root


def test_append_move_error_player_actions():
    """Test to ensure there are actions when appending with a player"""
    game = games.read_from_file("basic_extensive_game.efg")
    with pytest.raises(gbt.UndefinedOperationError):
        game.append_move(game.root, game.players[0], [])


def test_append_move_error_player_mismatch():
    """Test to ensure the node and the player are from the same game"""
    game1 = gbt.Game.new_tree()
    game2 = games.read_from_file("basic_extensive_game.efg")
    with pytest.raises(gbt.MismatchError):
        game1.append_move(game1.root, game2.players[0], ["a"])


def test_append_move_error_infoset_mismatch():
    """Test to ensure the node and the player are from the same game"""
    game1 = gbt.Game.new_tree()
    game2 = games.read_from_file("basic_extensive_game.efg")
    with pytest.raises(gbt.MismatchError):
        game1.append_infoset(game1.root, game2.players[0].infosets[0])


def test_insert_move_error_player_actions():
    """Test to ensure there are actions when inserting with a player"""
    game = games.read_from_file("basic_extensive_game.efg")
    with pytest.raises(gbt.UndefinedOperationError):
        game.insert_move(game.root, game.players[0], 0)


def test_insert_move_error_player_mismatch():
    """Test to ensure the node and the player are from the same game"""
    game1 = gbt.Game.new_tree()
    game2 = games.read_from_file("basic_extensive_game.efg")
    with pytest.raises(gbt.MismatchError):
        game1.insert_move(game1.root, game2.players[0], 1)


def test_node_leave_infoset():
    """Test to ensure it's possible to remove a node from an infoset"""
    game = games.read_from_file("basic_extensive_game.efg")
    assert len(game.infosets[1].members) == 2
    game.leave_infoset(game.root.children[0])
    assert len(game.infosets[1].members) == 1


def test_node_delete_parent():
    """Test to ensure deleting a parent node works"""
    game = games.read_from_file("basic_extensive_game.efg")
    node = game.root.children[0]
    game.delete_parent(node)
    assert game.root == node


def test_node_delete_tree():
    """Test to ensure deleting every child of a node works"""
    game = games.read_from_file("basic_extensive_game.efg")
    node = game.root.children[0]
    game.delete_tree(node)
    assert len(node.children) == 0


def test_node_copy_nonterminal():
    """Test on copying to a nonterminal node."""
    game = games.read_from_file("basic_extensive_game.efg")
    with pytest.raises(gbt.UndefinedOperationError):
        game.copy_tree(game.root, game.root)


def test_node_copy_across_games():
    """Test to ensure a gbt.MismatchError is raised when trying to copy a tree
    from a different game.
    """
    game1 = gbt.Game.new_tree()
    game2 = games.read_from_file("basic_extensive_game.efg")
    with pytest.raises(gbt.MismatchError):
        game1.copy_tree(game1.root, game2.root)
    with pytest.raises(gbt.MismatchError):
        game1.copy_tree(game2.root, game1.root)


def _subtrees_equal(
        n1: gbt.Node,
        n2: gbt.Node,
        recursion_stop_node: typing.Union[gbt.Node, None] = None
) -> bool:
    if n1 == recursion_stop_node:
        return n2.is_terminal
    if n1.is_terminal and n2.is_terminal:
        return n1.outcome == n2.outcome
    if n1.is_terminal is not n2.is_terminal:
        return False
    # now, both n1 and n2 are non-terminal
    # check that they are in the same infosets
    if n1.infoset != n2.infoset:
        return False
    # check that they have the same number of children
    if len(n1.children) != len(n2.children):
        return False

    return all(
        _subtrees_equal(c1, c2, recursion_stop_node) for (c1, c2) in zip(n1.children, n2.children)
    )


def test_copy_tree_onto_nondescendent_terminal_node():
    """Test copying a subtree to a non-descendent node."""
    g = games.read_from_file("e01.efg")
    list_nodes = list(g.nodes)
    src_node = list_nodes[3]   # path=[1, 0]
    dest_node = list_nodes[2]  # path=[0, 0]

    g.copy_tree(src_node, dest_node)

    assert _subtrees_equal(src_node, dest_node)


def test_copy_tree_onto_descendent_terminal_node():
    """Test copying a subtree to a node that's a descendent of the original."""
    g = games.read_from_file("e01.efg")
    list_nodes = list(g.nodes)
    src_node = list_nodes[1]   # path=[0]
    dest_node = list_nodes[4]  # path=[0, 1, 0]

    g.copy_tree(src_node, dest_node)

    assert _subtrees_equal(src_node, dest_node, dest_node)


def test_node_move_nonterminal():
    """Test on moving to a nonterminal node."""
    game = games.read_from_file("basic_extensive_game.efg")
    with pytest.raises(gbt.UndefinedOperationError):
        game.move_tree(game.root, game.root)


def test_node_move_successor():
    """Test on moving a node to one of its successors."""
    game = games.read_from_file("basic_extensive_game.efg")
    with pytest.raises(gbt.UndefinedOperationError):
        game.move_tree(game.root, game.root.children[0].children[0].children[0])


def test_node_move_across_games():
    """Test to ensure a gbt.MismatchError is raised when trying to move a tree
    between different games.
    """
    game1 = gbt.Game.new_tree()
    game2 = games.read_from_file("basic_extensive_game.efg")
    with pytest.raises(gbt.MismatchError):
        game1.move_tree(game1.root, game2.root)
    with pytest.raises(gbt.MismatchError):
        game1.move_tree(game2.root, game1.root)


def test_append_move_creates_single_infoset_list_of_nodes():
    """Test that appending a list of nodes creates a single infoset."""
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    nodes = [game.root.children[1].children[0],
             game.root.children[0].children[0],
             game.root.children[0].children[1]]
    game.append_move(nodes, "Player 3", ["B", "F"])
    assert len(game.players["Player 3"].infosets) == 1


def test_append_move_same_infoset_list_of_nodes():
    """Test that nodes from a list of nodes are resolved in the same infoset."""
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    nodes = [game.root.children[1].children[0], game.root.children[0].children[0]]
    game.append_move(nodes, "Player 3", ["B", "F"])
    assert nodes[0].infoset == nodes[1].infoset


def test_append_move_actions_list_of_nodes():
    """Test that nodes from a list of nodes that resolved in the same infoset
    have the same actions.
    """
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    nodes = [game.root.children[1].children[0], game.root.children[0].children[0]]
    game.append_move(nodes, "Player 3", ["B", "F", "S"])
    action_list = list(game.players["Player 3"].infosets[0].actions)
    for node in nodes:
        assert list(node.infoset.actions) == action_list


def test_append_move_actions_list_of_node_labels():
    """Test that nodes from a list of node labels are resolved correctly."""
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    game.root.children[1].children[0].label = "0"
    game.root.children[0].children[0].label = "00"
    game.append_move(["0", "00"], "Player 3", ["B", "F", "S"])

    assert game.root.children[1].children[0].children[0].parent.label == "0"
    assert game.root.children[0].children[0].children[0].parent.label == "00"
    assert len(game.root.children[1].children[0].children) == 3
    assert len(game.root.children[0].children[0].children) == 3


def test_append_move_actions_list_of_mixed_node_references():
    """Test that nodes from a list of nodes with either 'node' or str references
    are resolved correctly.
    """
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")

    game.root.children[1].children[0].label = " 000"
    node_references = [" 000", game.root.children[0].children[0]]
    game.append_move(node_references, "Player 3", ["B", "F", "S"])

    assert game.root.children[1].children[0].children[0].parent.label == " 000"
    assert len(game.root.children[1].children[0].children) == 3
    assert len(game.root.children[0].children[0].children) == 3


def test_append_move_labels_list_of_nodes():
    """Test that nodes from a list of nodes that resolved in the same infoset
    have the same labels per action.
    """
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    nodes = [game.root.children[1].children[0], game.root.children[0].children[0]]
    game.append_move(nodes, "Player 3", ["B", "F", "S"])

    action_list = game.players["Player 3"].infosets[0].actions
    tmp1 = game.root.children[1].children[0].infoset.actions
    tmp2 = game.root.children[0].children[0].infoset.actions

    for (action, action1, action2) in zip(action_list, tmp1, tmp2):
        assert action.label == action1.label
        assert action.label == action2.label


def test_append_move_node_list_with_non_terminal_node():
    """Test that we get an UndefinedOperationError when we import in append_move a list
    of nodes that has a non-terminal node.
    """
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    with pytest.raises(gbt.UndefinedOperationError):
        game.append_move(
            [game.root.children[1], game.root.children[0].children[1]],
            "Player 3",
            ["B", "F"]
        )


def test_append_move_node_list_with_duplicate_node_references():
    """Test that we get a ValueError when we import in append_move a list
    nodes with non-unique node references.
    """
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    game.root.children[0].children[1].label = "00"
    with pytest.raises(ValueError):
        game.append_move(
            ["00", game.root.children[1].children[0], game.root.children[0].children[1]],
            "Player 3",
            ["B", "F"]
        )


def test_append_move_node_list_is_empty():
    """Test that we get a ValueError when we import in append_move an
    empty list of nodes.
    """
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    with pytest.raises(ValueError):
        game.append_move([], "Player 3", ["B", "F"])


def test_append_infoset_node_list_with_non_terminal_node():
    """Test that we get an UndefinedOperationError when we import in append_infoset
    a list of nodes that has a non-terminal node.
    """
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    game.append_move(game.root.children[0].children[0], "Player 3", ["B", "F"])
    with pytest.raises(gbt.UndefinedOperationError):
        game.append_infoset(
            [game.root.children[1], game.root.children[0].children[1]],
            game.root.children[0].children[0].infoset
        )


def test_append_infoset_node_list_with_duplicate_node():
    """Test that we get a ValueError when we import in append_infoset a list
    with non-unique elements.
    """
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    game.append_move(game.root.children[0].children[0], "Player 3", ["B", "F"])
    with pytest.raises(ValueError):
        game.append_infoset(
            [game.root.children[0].children[1],
             game.root.children[1].children[0],
             game.root.children[0].children[1]],
            game.root.children[0].children[0].infoset
        )


def test_append_infoset_node_list_is_empty():
    """Test that we get a ValueError when we import in append_infoset an
    empty list of nodes.
    """
    game = games.read_from_file("sample_extensive_game.efg")
    game.add_player("Player 3")
    game.append_move(game.root.children[0].children[0], "Player 3", ["B", "F"])
    with pytest.raises(ValueError):
        game.append_infoset([], game.root.children[0].children[0].infoset)


def _get_members(action: gbt.Action) -> set[gbt.Node]:
    """Calculates the set of nodes resulting from taking a specific action
    at all nodes within its information set.
    """
    infoset = action.infoset
    action_index = action.number

    return [member_node.children[action_index] for member_node in infoset.members]


def _count_subtree_nodes(start_node: gbt.Node, count_terminal: bool) -> int:
    """Counts nodes in the subtree rooted at `start_node` (including `start_node`).

    Parameters
    ----------
    start_node: Node
        The root of the subtree
    count_terminal: bool
        Include or exclude terminal nodes from count
    """
    count = 1 if count_terminal or not start_node.is_terminal else 0

    for child in start_node.children:
        count += _count_subtree_nodes(child, count_terminal)
    return count


def test_len_matches_expected_node_count():
    """Verify `len(game.nodes)` matches expected node count
    """
    game = games.read_from_file("e01.efg")
    expected_node_count = 9

    direct_len = len(game.nodes)
    assert direct_len == expected_node_count

    assert direct_len == _count_subtree_nodes(game.root, True)


def test_len_after_delete_tree():
    """Verify `len(game.nodes)` is correct after `delete_tree`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nodes = len(game.nodes)
    list_nodes = list(game.nodes)

    root_of_the_deleted_subtree = list_nodes[3]
    number_of_deleted_nodes = _count_subtree_nodes(root_of_the_deleted_subtree, True) - 1

    game.delete_tree(root_of_the_deleted_subtree)

    assert len(game.nodes) == initial_number_of_nodes - number_of_deleted_nodes


def test_len_after_delete_parent():
    """Verify `len(game.nodes)` is correct after `delete_parent`.
    """
    game = games.read_from_file("e02.efg")
    initial_number_of_nodes = len(game.nodes)
    list_nodes = list(game.nodes)

    node_parent_to_delete = list_nodes[4]

    number_of_node_ancestors = _count_subtree_nodes(node_parent_to_delete, True)
    number_of_parent_ancestors = _count_subtree_nodes(node_parent_to_delete.parent, True)
    diff = number_of_parent_ancestors - number_of_node_ancestors

    game.delete_parent(node_parent_to_delete)

    assert len(game.nodes) == initial_number_of_nodes - diff


def test_len_after_append_move():
    """Verify `len(game.nodes)` is correct after `append_move`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nodes = len(game.nodes)
    list_nodes = list(game.nodes)

    terminal_node = list_nodes[5]         # path=[1, 1, 0]
    player = game.players[0]
    actions_to_add = ["T", "M", "B"]

    game.append_move(terminal_node, player, actions_to_add)

    assert len(game.nodes) == initial_number_of_nodes + len(actions_to_add)


def test_len_after_append_infoset():
    """Verify `len(game.nodes)` is correct after `append_infoset`.
    """
    game = games.read_from_file("e02.efg")
    initial_number_of_nodes = len(game.nodes)
    list_nodes = list(game.nodes)

    member_node = list_nodes[2]           # path=[1]
    infoset_to_modify = member_node.infoset
    number_of_infoset_actions = len(infoset_to_modify.actions)
    terminal_node_to_add = list_nodes[6]  # path=[1, 1, 1]

    game.append_infoset(terminal_node_to_add, infoset_to_modify)

    assert len(game.nodes) == initial_number_of_nodes + number_of_infoset_actions


def test_len_after_add_action():
    """Verify `len(game.nodes)` is correct after `add_action`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nodes = len(game.nodes)

    infoset_to_modify = game.infosets[1]

    num_nodes_in_infoset = len(infoset_to_modify.members)

    game.add_action(infoset_to_modify)

    assert len(game.nodes) == initial_number_of_nodes + num_nodes_in_infoset


def test_len_after_delete_action():
    """Verify `len(game.nodes)` is correct after `delete_action`.
    """
    game = games.read_from_file("e02.efg")
    initial_number_of_nodes = len(game.nodes)

    action_to_delete = game.infosets[0].actions[1]

    # Calculate the total number of nodes within all subtrees
    # that begin immediately after taking the specified action.
    nodes_to_delete = 0
    action_nodes = _get_members(action_to_delete)

    for subtree_root in action_nodes:
        nodes_to_delete += _count_subtree_nodes(subtree_root, True)

    game.delete_action(action_to_delete)

    assert len(game.nodes) == initial_number_of_nodes - nodes_to_delete


def test_len_after_insert_move():
    """Verify `len(game.nodes)` is correct after `insert_move`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nodes = len(game.nodes)
    list_nodes = list(game.nodes)

    node_to_insert_above = list_nodes[3]

    player = game.players[1]
    num_actions_to_add = 3

    game.insert_move(node_to_insert_above, player, num_actions_to_add)

    assert len(game.nodes) == initial_number_of_nodes + num_actions_to_add


def test_len_after_insert_infoset():
    """Verify `len(game.nodes)` is correct after `insert_infoset`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nodes = len(game.nodes)
    list_nodes = list(game.nodes)

    member_node = list_nodes[6]           # path=[1]
    infoset_to_modify = member_node.infoset
    node_to_insert_above = list_nodes[7]  # path=[0, 1]
    number_of_infoset_actions = len(infoset_to_modify.actions)

    game.insert_infoset(node_to_insert_above, infoset_to_modify)

    assert len(game.nodes) == initial_number_of_nodes + number_of_infoset_actions


def test_len_after_copy_tree():
    """Verify `len(game.nodes)` is correct after `copy_tree`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nodes = len(game.nodes)
    list_nodes = list(game.nodes)
    src_node = list_nodes[3]              # path=[1, 0]
    dest_node = list_nodes[2]             # path=[0, 0]
    number_of_src_ancestors = _count_subtree_nodes(src_node, True)

    game.copy_tree(src_node, dest_node)

    assert len(game.nodes) == initial_number_of_nodes + number_of_src_ancestors - 1


def test_nonterminal_len_matches_expected_count():
    """Verify `len(game._nonterminal_nodes)` matches expected count
    """
    game = games.read_from_file("e01.efg")
    expected_nonterminal_node_count = 4

    direct_nonterminal_len = len(game._nonterminal_nodes)
    assert direct_nonterminal_len == expected_nonterminal_node_count


def test_nonterminal_len_after_delete_tree():
    """Verify `len(game._nonterminal_nodes)` is correct after `delete_tree`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nonterminal_nodes = len(game._nonterminal_nodes)
    list_nodes = list(game.nodes)

    root_of_the_deleted_subtree = list_nodes[1]
    number_of_deleted_nonterminal_nodes = _count_subtree_nodes(root_of_the_deleted_subtree, False)

    game.delete_tree(root_of_the_deleted_subtree)

    assert len(game._nonterminal_nodes) == initial_number_of_nonterminal_nodes \
        - number_of_deleted_nonterminal_nodes


def test_nonterminal_len_after_delete_parent_of_nonterminal_node():
    """Verify `len(game._nonterminal_nodes)` is correct after `delete_parent`.
    """
    game = games.read_from_file("e02.efg")
    list_nodes = list(game.nodes)
    node_parent_to_delete = list_nodes[4]  # path=[1, 1]

    initial_number_of_nonterminal_nodes = len(game._nonterminal_nodes)
    diff = _count_subtree_nodes(node_parent_to_delete.parent, False) \
        - _count_subtree_nodes(node_parent_to_delete, False)

    game.delete_parent(node_parent_to_delete)

    assert len(game._nonterminal_nodes) == initial_number_of_nonterminal_nodes - diff


def test_nonterminal_len_after_delete_parent_of_terminal_node():
    """Verify `len(game._nonterminal_nodes)` is correct after `delete_parent`.
    """
    game = games.read_from_file("e02.efg")
    list_nodes = list(game.nodes)
    node_parent_to_delete = list_nodes[5]  # path=[0, 1, 1]

    initial_number_of_nonterminal_nodes = len(game._nonterminal_nodes)
    diff = _count_subtree_nodes(node_parent_to_delete.parent, False) \
        - _count_subtree_nodes(node_parent_to_delete, False)

    game.delete_parent(node_parent_to_delete)

    assert len(game._nonterminal_nodes) == initial_number_of_nonterminal_nodes - diff


def test_nonterminal_len_after_append_move():
    """Verify `len(game._nonterminal_nodes)` is correct after `append_move`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nonterminal_nodes = len(game._nonterminal_nodes)
    list_nodes = list(game.nodes)

    terminal_node = list_nodes[5]         # path=[1, 1, 0]
    player = game.players[0]
    actions_to_add = ["T", "M", "B"]

    game.append_move(terminal_node, player, actions_to_add)

    assert len(game._nonterminal_nodes) == initial_number_of_nonterminal_nodes \
        + _count_subtree_nodes(terminal_node, False)


def test_nonterminal_len_after_append_infoset():
    """Verify `len(game._nonterminal_nodes)` is correct after `append_infoset`.
    """
    game = games.read_from_file("e02.efg")
    initial_number_of_nonterminal_nodes = len(game._nonterminal_nodes)
    list_nodes = list(game.nodes)

    member_node = list_nodes[2]           # path=[1]
    infoset_to_modify = member_node.infoset
    terminal_node_to_add = list_nodes[6]  # path=[1, 1, 1]

    game.append_infoset(terminal_node_to_add, infoset_to_modify)

    assert len(game._nonterminal_nodes) == initial_number_of_nonterminal_nodes \
        + _count_subtree_nodes(terminal_node_to_add, False)


def test_nonterminal_len_after_add_action():
    """Verify `len(game._nonterminal_nodes)` does not change after `add_action` to an infoset.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nonterminal_nodes = len(game._nonterminal_nodes)

    infoset_to_modify = game.infosets[1]

    game.add_action(infoset_to_modify)

    assert len(game._nonterminal_nodes) == initial_number_of_nonterminal_nodes


def test_nonterminal_len_after_delete_action():
    """Verify `len(game._nonterminal_nodes)` is correct after `delete_action`.
    """
    game = games.read_from_file("e02.efg")
    initial_number_of_nonterminal_nodes = len(game._nonterminal_nodes)

    action_to_delete = game.infosets[0].actions[1]

    # Calculate the total number of nodes within all subtrees
    # that begin immediately after taking the specified action.
    nonterminal_nodes_to_delete = 0
    action_nodes = _get_members(action_to_delete)

    for subtree_root in action_nodes:
        nonterminal_nodes_to_delete += _count_subtree_nodes(subtree_root, False)

    game.delete_action(action_to_delete)

    assert len(game._nonterminal_nodes) == initial_number_of_nonterminal_nodes \
        - nonterminal_nodes_to_delete


def test_nonterminal_len_after_insert_move():
    """Verify `len(game._nonterminal_nodes)` correctly increaces by 1 after `insert_move`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nonterminal_nodes = len(game._nonterminal_nodes)
    list_nodes = list(game.nodes)

    node_to_insert_above = list_nodes[3]

    player = game.players[1]
    num_actions_to_add = 3

    game.insert_move(node_to_insert_above, player, num_actions_to_add)

    assert len(game._nonterminal_nodes) == initial_number_of_nonterminal_nodes + 1


def test_nonterminal_len_after_insert_infoset():
    """Verify `len(game._nonterminal_nodes)` correctly increaces by 1 after `insert_infoset`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nonterminal_nodes = len(game._nonterminal_nodes)
    list_nodes = list(game.nodes)

    member_node = list_nodes[6]           # path=[1]
    infoset_to_modify = member_node.infoset
    node_to_insert_above = list_nodes[7]  # path=[0, 1]

    game.insert_infoset(node_to_insert_above, infoset_to_modify)

    assert len(game._nonterminal_nodes) == initial_number_of_nonterminal_nodes + 1


def test_nonterminal_len_after_copy_tree():
    """Verify `len(game._nonterminal_nodes)` is correct after `copy_tree`.
    """
    game = games.read_from_file("e01.efg")
    initial_number_of_nodes = len(game._nonterminal_nodes)
    list_nodes = list(game.nodes)
    src_node = list_nodes[3]              # path=[1, 0]
    dest_node = list_nodes[2]             # path=[0, 0]
    number_of_nonterminal_src_ancestors = _count_subtree_nodes(src_node, False)

    game.copy_tree(src_node, dest_node)

    assert len(game._nonterminal_nodes) == initial_number_of_nodes \
        + number_of_nonterminal_src_ancestors


def test_node_plays():
    """Verify `node.plays` returns plays reachable from a given node.
    """
    game = games.read_from_file("e02.efg")
    list_nodes = list(game.nodes)

    test_node = list_nodes[2]  # path=[1]

    expected_set_of_plays = {
        list_nodes[3], list_nodes[5], list_nodes[6]
    }  # paths=[0, 1], [0, 1, 1], [1, 1, 1]

    assert set(test_node.plays) == expected_set_of_plays


@pytest.mark.parametrize(
    "game_obj",
    [
        pytest.param(games.read_from_file("basic_extensive_game.efg")),
        pytest.param(games.read_from_file("binary_3_levels_generic_payoffs.efg")),
        pytest.param(games.read_from_file("cent3.efg")),
        pytest.param(games.read_from_file("e01.efg")),
        pytest.param(games.read_from_file("e02.efg")),
        pytest.param(games.read_from_file("poker.efg")),
        pytest.param(gbt.Game.new_tree()),
    ],
)
def test_nodes_iteration_order(game_obj: gbt.Game):
    """Verify that the C++ `game.nodes` iterator produces the DFS traversal.
    """
    def dfs(node: gbt.Node) -> typing.Iterator[gbt.Node]:
        yield node
        for child in node.children:
            yield from dfs(child)

    assert all(a == b for a, b in itertools.zip_longest(game_obj.nodes, dfs(game_obj.root)))
