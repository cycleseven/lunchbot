from strings import is_subsequence


def test_should_return_true_for_subsequence_at_end_of_long_list():
    assert is_subsequence(["y", "e", "s"], ["hello", "and", "y", "e", "s"])


def test_should_return_true_for_subsequence_in_middle_of_long_list():
    assert is_subsequence(["y", "e", "s"], ["actually", "y", "e", "s", "haha"])


def test_should_return_true_for_subsequence_at_start_of_long_list():
    assert is_subsequence(["y", "e", "s"], ["y", "e", "s", "haha"])


def test_should_return_true_if_lists_are_equal():
    assert is_subsequence(["y", "e", "s"], ["y", "e", "s"])


def test_should_return_true_if_both_lists_are_empty():
    assert not is_subsequence([], [])


def test_should_return_false_if_short_list_is_not_subsequence_of_long_list():
    assert not is_subsequence(['l', 'o', 'l'], ['d', 'i', 'f', 'f', 'e', 'r', 'e', 'n', 't'])


def test_should_return_false_if_first_argument_is_actually_the_longer_list():
    assert not is_subsequence(["l", "o", "n", "g"], ["l", "o"])


def test_should_return_false_for_partial_match_at_end_of_long_list():
    assert not is_subsequence(['a', 'b', 'c'], ['1', '2', 'a', 'b'])


def test_should_return_false_for_partial_match_in_middle_of_long_list():
    assert not is_subsequence(['a', 'b'], ['1', 'a', '3'])
