import re


def page_name_to_label(page_name):
    return re.sub(r"_+", " ", page_name)


def label_to_page_name(label):
    return re.sub(r"([ ]+_)|(_[ ]+)|([ ]+)", "_", label)
