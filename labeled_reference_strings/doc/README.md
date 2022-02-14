Annotations initially preserved as Python pickles in the format below.

```
{
    'input': [
        '<reference_string_0>',
        '<reference_string_1>',
        '<reference_string_2>',
        ...
    ]
    'target': [
        [<ref_0_label_int_0>, [<ref_0_label_int_1>], ...],
        [<ref_1_label_int_0>, [<ref_1_label_int_1>], ...],
        [<ref_2_label_int_0>, [<ref_2_label_int_1>], ...],
        ...
    ]
}
```

Python script `convert.py` recreates the tokenization of reference strings, converts integer labels to tag names, and stores the annotations in two more common formats; [CoNLL-U Plus](https://universaldependencies.org/ext-format.html) and JSON in the format below.

```
[
    {
        'text': '<reference_string_0>',
        'tokens': [
            {
                'offset': {
                    'start': <offset_start>,
                    'end': <offset_end>
                }
                'label': '<tag_name>'
            },
            ...
        ]
    },
    {
        'text': '<reference_string_1>',
    ...
]
```
