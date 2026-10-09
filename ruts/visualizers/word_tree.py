from anyts.visualizers.word_tree import wordtree as core_wordtree

from ..utils import with_stripped_marks

wordtree = with_stripped_marks(core_wordtree, "keyword")
