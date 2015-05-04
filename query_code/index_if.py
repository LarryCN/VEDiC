import config
import index_op
import cindex

""" open term 
    input term
    output termobj 
"""
def openlist(term):
    info = index_op.get_term_info(term)
    return cindex.openlist(info)
