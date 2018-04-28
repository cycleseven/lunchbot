from utils import is_subsequence


def test_should_return_true_if_short_list_is_subsequence_of_long_list():
    assert is_subsequence(["y", "e", "s"], ["hello", "and", "y", "e", "s"])


def test_should_return_true_if_lists_are_equal():
    assert is_subsequence(["y", "e", "s"], ["y", "e", "s"])


def test_should_return_false_if_first_argument_is_actually_the_longer_list():
    assert not is_subsequence(["l", "o", "n", "g"], ["l", "o"])


def test_should_return_true_if_both_lists_are_empty():
    assert not is_subsequence([], [])


def test_should_handle_subsequence_in_middle_of_list():
    assert not is_subsequence(["actually", "y", "e", "s", "haha"], ["y", "e", "s"])


def test_should_handle_subsequence_at_start_of_list():
    assert not is_subsequence(["y", "e", "s", "haha"], ["y", "e", "s"])
