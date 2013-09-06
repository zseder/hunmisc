"""
Copyright 2011-13 Attila Zseder
Email: zseder@gmail.com

This file is part of hunmisc project
url: https://github.com/zseder/hunmisc

hunmisc is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""


"""Reads the configuration file and sets up the tools necessary to parse
the selected language."""

import logging
from langtools.utils.cascading_config import CascadingConfigParser

class LanguageTools(object):
    """Instantiates the tools necessary to handle a language.
    
    The configuration file should contain a section for each language used.
    Optionally, a section called 'tools' can be defined, where the default
    values for the configuration options may be specified.
    
    The options are:
        - pos_tagger: the POS tagger class;
        - lemmatizer: the lemmatizer class.
        - sen_tokenizer: the sentence tokenizer.
        - word_tokenizer: the word tokenizer.
        - tokenizer: word and sentence tokenizer.

    The classes the options refer to are responsible for initializing the
    resources. Their parameters must also be specified in the configuration
    file.
    """
    def __init__(self, config_file, lang_config ='en'):
        """
        @param lang_config a section in the configuration file. Must either
                           be valid as a language code, or be a language code
                           followed by a '.' and an arbitrary string.
        """                   
        self.lang_config = lang_config
        self.language = lang_config.split('.', 1)[0]
        self.config = self.read_config_file(config_file)
        self.pos_tagger = self.initialize_tool('pos_tagger')
        self.lemmatizer = self.initialize_tool('lemmatizer')
        tokenizer = self.initialize_tool('tokenizer')
        if tokenizer is not None:
            self.sen_tokenizer = tokenizer
            self.word_tokenizer = tokenizer
        else:
            self.sen_tokenizer = self.initialize_tool('sen_tokenizer')
            self.word_tokenizer = self.initialize_tool('word_tokenizer')

    def read_config_file(self, config_file):
        """Reads the section of the configuration file that corresponds to
        @p language to a dict."""
        config_parser = CascadingConfigParser(config_file)
        config = config_parser.items(self.lang_config)
        return dict(config)

    def initialize_tool(self, tool_name):
        """Instantiates the specified tool. The format of @p tool_name is
        package.Class."""
        logging.debug("Initializing " + tool_name)
        try:
            tool_package, tool_class = self.config[tool_name].rsplit('.', 1)
            logging.debug("Class" + tool_package + '.' + tool_class)
            tool_module = __import__(tool_package, fromlist=[tool_class])
            tool_object = getattr(tool_module, tool_class)(self.config)
            return tool_object
        except KeyError, ke:
            logging.warn("KeyError: {0}".format(ke))
            return None

    def pos_tag(self, tokens):
        """@sa langtools.utils.tools.PosTaggerWrapper.pos_tag()."""
        if self.pos_tagger is not None:
            self.pos_tagger.pos_tag(tokens)

    def lemmatize(self, tokens):
        """@sa langtools.utils.tools.LemmatizerWrapper.lemmatize()."""
        if self.lemmatizer is not None:
            self.lemmatizer.lemmatize(tokens)

    def sen_tokenize(self, raw):
        """@sa langtools.utils.tools.SentenceTokenizerWrapper.sen_tokenize()."""
        if self.sen_tokenizer is not None:
            return self.sen_tokenizer.sen_tokenize(raw)

    def word_tokenize(self, sen):
        """@sa langtools.utils.tools.WordTokenizerWrapper.word_tokenize()."""
        if self.word_tokenizer is not None:
            return self.word_tokenizer.word_tokenize(sen)

    def tokenize(self, raw):
        """Runs sen_tokenize and the word_tokenize on the text."""
        return [self.word_tokenize(sen) for sen in self.sen_tokenize(raw)]

if __name__ == '__main__':
    import sys
    lt = LanguageTools(sys.argv[1], sys.argv[2])
    print lt.config

