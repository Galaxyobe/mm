

def deep_combine(dict1, dict2):
    """
    Deep combine two dict

    Combine

    Args:
        @param dict1: a dict
        @param dict2: a dict

    Returns:
        dict:the combine dict
    """

    for key in dict2.keys():
        if key not in dict1.keys():
            dict1[key] = dict2[key]
        else:
            if isinstance(dict2[key], dict):
                deep_combine(dict1[key], dict2[key])
    return dict1
