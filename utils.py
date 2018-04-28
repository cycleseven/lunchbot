def is_subsequence(short_list, long_list):
    """
    Return true if short_list is a subsequence of long_list.
    """
    print("is_subseq")
    print(short_list)
    print(long_list)

    if len(short_list) > len(long_list):
        return False

    for i, _ in enumerate(long_list):
        looks_good = True

        for j, item_from_short_list in enumerate(short_list):
            if len(long_list) - j == 0:
                break

            # In this case, we've reached the end of the long list and still only have
            # a partial match. So we're not going to get one.
            if i + j == len(long_list):
                looks_good = False
                break

            if item_from_short_list != long_list[i + j]:
                looks_good = False
                break

        if looks_good:
            return True

    return False

