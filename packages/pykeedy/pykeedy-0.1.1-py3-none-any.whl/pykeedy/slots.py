BASIC13 = [
    ["ch", "sh", "q", "y"],
    ["e"],
    ["o"],
    ["a"],
    ["l", "r", "s", "t", "p", "f", "s", "cth", "ckh", "cph", "cfh"],
    ["d", "k"],
    ["ch", "sh"],
    ["e", "ee", "eee"],
    ["o"],
    ["a"],
    ["i", "ii", "iii"],
    ["d", "k", "l", "r", "s", "t", "m", "n"],
    ["y"],
]

BASIC11 = BASIC13.copy()
BASIC11[1] = ["e", "o", "a"]  # Replace ["e"] with ["e", "o", "a"]
del BASIC11[2]  # Remove ["o"]
del BASIC11[2]  # Remove ["a"]

COMPACT7 = [
    ["ch", "sh", "q", "y"],
    ["e", "eo", "o", "a"],
    ["l", "r", "s", "t", "p", "f", "cth", "ckh", "cph", "cfh", "d", "k", "lk"],
    ["ch", "sh"],
    ["e", "eo", "ea", "ee", "eee", "o", "a", "oa"],
    ["i", "ii", "iii"],
    ["d", "dy", "k", "ky", "l", "ly", "r", "ry", "s", "sy", "t", "ty", "m", "n", "y"],
]

EXTENDED12 = [
    ["ch", "sh", "q", "y"],
    ["e", "eo", "o", "a"],
    ["d", "l", "r", "s", "k", "t", "p", "f", "ckh", "cth", "cph", "cfh", "lk", "ld"],
    ["ch", "sh", "q", "y"],
    ["e", "ee", "eee", "eo", "eeo", "o", "a", "oa"],
    ["i", "ii", "iii"],
    ["d", "l", "r", "s", "k", "t", "p", "f", "ckh", "cth", "cph", "cfh", "lk", "ld"],
    ["ch", "sh", "y", "e", "ee", "eee", "eo", "eeo", "o", "a", "oa"],
    ["i", "ii", "iii"],
    [
        "d",
        "l",
        "r",
        "s",
        "k",
        "t",
        "p",
        "f",
        "ckh",
        "cth",
        "cph",
        "cfh",
        "lk",
        "ld",
        "m",
        "n",
    ],
    ["y"],
]


def num_possible_words(slots: list[list[str]]) -> int:
    total = 1
    for slot in slots:
        total *= len(slot) + 1  # Slot can be empty
    return total - 1  # Subtract empty word


def count_generateable_words(
    words: list[str], slots: list[list[str]], unique_only: bool = True
) -> float:
    matches = 0
    if unique_only:
        words = list(set(words))
    for word in words:
        if can_generate_word(word, slots):
            matches += 1
    return matches


def score_slot_grammar(
    words: list[str], slots: list[list[str]], unique_only: bool = True
) -> dict[str, float]:
    if unique_only:
        words = list(set(words))
    matches = count_generateable_words(words, slots, unique_only=False)
    coverage = matches / len(words)
    efficiency = matches / num_possible_words(slots)
    f1 = (2 * coverage * efficiency) / (coverage + efficiency) if matches else 0
    return {"coverage": coverage, "efficiency": efficiency, "f1": f1}


def can_generate_word(word: str, slot_list: list[list[str]]) -> bool:
    memo = {}

    def dp(word_index: int, slot_index: int) -> bool:
        if (word_index, slot_index) in memo:
            return memo[(word_index, slot_index)]

        # Base cases
        if word_index == len(word):
            # Success if we've consumed all the word (regardless of remaining slots)
            result = True
        elif slot_index >= len(slot_list):
            # Failed if we have remaining word but no more slots
            result = False
        else:
            result = False

            # Option 1: Skip this slot (use 0 elements)
            if dp(word_index, slot_index + 1):
                result = True
            else:
                # Option 2: Try each element in current slot (use 1 element)
                for option in slot_list[slot_index]:
                    if word[word_index:].startswith(option):
                        if dp(word_index + len(option), slot_index + 1):
                            result = True
                            break

        memo[(word_index, slot_index)] = result
        return result

    return dp(0, 0)
