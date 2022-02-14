import json
import os
import pickle
import re
import sys
from transformers import PreTrainedTokenizerFast

tokenizer = PreTrainedTokenizerFast.from_pretrained('bert-base-uncased')
fns = ['val_data.pkl', 'test_data.pkl', 'train_data.pkl']

tags = [
    '<note>',
    '<volume>',
    '<date>',
    '<title>',
    '<contexts>',
    '<journal>',
    '<publisher>',
    '<tech>',
    '<institution>',
    '<pages>',
    '<location>',
    '<booktitle>',
    '<editor>',
    '<author>',
    '<conference>'
]


def simplify_labeling(offsets, token_labels):
    """ Merges adjacent labels.
    """

    # prevent modifying parameters
    ofs = offsets.copy()
    lls = token_labels.copy()
    # prepare output
    offsets_simple = []
    token_labels_simple = []
    # as long as there are tokens left
    while len(lls) > 0:
        # start with one label
        ofs_out = ofs.pop(0)  # insert first offset
        lls_out = lls.pop(0)  # insert label
        # extend as long as connected
        while (len(lls) > 0 and  # skip when list empty
               ofs_out[1] == ofs[0][0] and  # no gap to next offset
               lls_out == lls[0]):  # and same label
            ofs_out = (ofs_out[0], ofs.pop(0)[1])  # extend to next offset end
            lls.pop(0)  # keep offset and label list in sync
        # then add to output
        offsets_simple.append(ofs_out)
        token_labels_simple.append(lls_out)
    return offsets_simple, token_labels_simple


def to_conllu(refstr, offsets, token_labels, first=False):
    """ Create a str in CoNLL-U Plus format based on
        a reference string, offets, and token labels

        https://universaldependencies.org/ext-format.html
    """

    if first:
        meta_head = '# global.columns = ID TOKEN LABEL\n'
    else:
        meta_head = ''
    meta_text = '{head}# text = {refstr}\n'.format(
        head=meta_head,
        refstr=refstr
    )
    conllu_str = meta_text
    for i, (start, end) in enumerate(offsets):
        conllu_str += '{tid}\t{form}\t{label}\n'.format(
            tid=i+1,
            form=refstr[start:end],
            label=tags[token_labels_simple[i]]
        )
    return conllu_str


# for each file
for fn in fns:
    with open(fn, 'rb') as f:
        data = pickle.load(f)
        conllu_out = ''
        json_out = []
        # for each reference string
        for i in range(len(data['input'])):
            # tokenize
            refstr = data['input'][i]
            token_labels = data['target'][i]
            tok_dict = tokenizer(
                refstr,
                return_offsets_mapping=True,
                add_special_tokens=False
            )
            encoding = tok_dict['input_ids']
            offsets = tok_dict['offset_mapping']
            assert(len(encoding) == len(token_labels))

            # convert from BERT tokenization to space delimited
            offsets_simple, token_labels_simple = simplify_labeling(
                offsets,
                token_labels
            )
            reconstrcuted_refstr = ' '.join(
                [refstr[start:end] for (start, end) in offsets_simple]
            )
            try:
                assert(len(reconstrcuted_refstr) == len(refstr))
            except AssertionError:
                # assume there is superfluous whitespace in refstr and recheck
                refstr_clean = re.sub(r'\s+', ' ', refstr)
                try:
                    assert(len(reconstrcuted_refstr) == len(refstr_clean))
                except AssertionError:
                    print(refstr)
                    print(len(refstr))
                    print(reconstrcuted_refstr)
                    print(len(reconstrcuted_refstr))
                    sys.exit()

            # JSON output
            json_dict = {
                'text': refstr,
                'tokens': []
            }
            for i in range(len(offsets_simple)):
                json_dict['tokens'].append({
                    'offset': offsets_simple[i],
                    'label': token_labels_simple[i]
                })
            json_out.append(json_dict.copy())

            # CoNLL-U Plus output
            conllu_str = to_conllu(
                refstr,
                offsets_simple,
                token_labels_simple,
                first=True)
            conllu_out += f'{conllu_str}\n'

    fn_base = os.path.splitext(fn)[0]
    conllu_fn = f'{fn_base}.conllup'
    json_fn = f'{fn_base}.json'
    with open(conllu_fn, 'w') as fc, open(json_fn, 'w') as fj:
        fc.write(conllu_out.strip())
        json.dump(json_out, fj)
