""" Main file for running Muzny quote attribution
@author Michael Miller Yoder (though this reimplementation of Muzny's quote attribution is from Sims+Bamman 2020)
@year 2021
"""

import os
import itertools
from multiprocessing import Pool
import pdb

from tqdm import tqdm

from input_format import AnnotatorInput
from quote_annotator import QuoteAnnotator
from output import AnnotatorOutput


def attribute_quotes(fic_dirpath, coref_dirpath, quote_dirpath, threads):
    """ Attribute quotes """
    if not os.path.exists(quote_dirpath):
        os.mkdir(quote_dirpath)
    fnames = []
    #for fname in sorted(os.listdir(fic_dirpath)):
    for fname in sorted(os.listdir(coref_dirpath)):
        name = fname.split('.')[0]
        if not os.path.exists(os.path.join(
            quote_dirpath, f'{name}.quote.json')):
            #fpaths.append(os.path.join(fic_dirpath, fname))
            fnames.append(name)
    params = sorted(zip(
        fnames,
        itertools.repeat(fic_dirpath),
        itertools.repeat(coref_dirpath),
        itertools.repeat(quote_dirpath),
        ))
    
    if threads > 1:
        with Pool(threads) as p:
            list(tqdm(p.imap(attribute_quotes_file, params), total=len(fnames), 
                ncols=70))
    else:
        # for debugging
        list(tqdm(map(attribute_quotes_file, params), total=len(fnames), ncols=70))

def attribute_quotes_file(fname, fic_dirpath, coref_dirpath, quote_dirpath):
    if not os.path.exists(quote_dirpath):
        os.makedirs(quote_dirpath)
    inp = AnnotatorInput(fname, fic_dirpath, coref_dirpath)
    if not inp.load_input():
        tqdm.write('skipping file (no coref or fic file)')
        return
    annotator = QuoteAnnotator(inp, quote_dirpath)
    out = annotator.annotate()
    out.transform() # transform to pipeline output format
    
    # Remove tmp files
    tmp_dirpath = 'tmp'
    out_dirpath = os.path.join(tmp_dirpath, 'formatted_input')
    os.remove(os.path.join(out_dirpath, f'{fname}.tokens'))
    os.remove(os.path.join(out_dirpath, f'{fname}.ents'))
    os.remove(os.path.join(tmp_dirpath, 'out', f'{fname}.out'))
