"""Reads the configuration file and sets up the tools necessary to parse
the selected language."""

import ConfigParser

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

    The classes the options refer to are responsible for initializing the
    resources. Their parameters must also be specified in the configuration
    file.
    """
    def __init__(self, config_file, language='en'):
        self.config = self.read_config_file(config_file, language)
        self.pos_tagger = self.initialize_tool('pos_tagger')
        self.lemmatizer = self.initialize_tool('lemmatizer')
        self.sen_tokenizer = self.initialize_tool('sen_tokenizer')
        self.word_tokenizer = self.initialize_tool('word_tokenizer')

    def read_config_file(self, config_file, language):
        """Reads the section of the configuration file that corresponds to
        @p language to a dict."""
        config_parser = ConfigParser.SafeConfigParser()
        config_parser.read(config_file)
        config = {}
        try:
            config.update(dict(config_parser.items('tools')))
        except ConfigParser.NoSectionError:
            pass # TODO: log
        try:
            config.update(dict(config_parser.items(language)))
        except ConfigParser.NoSectionError:
            pass # TODO: log
        return config

    def initialize_tool(self, tool_name):
        """Instantiates the specified tool. The format of @p tool_name is
        package.Class."""
        try:
            tool_package, tool_class = self.config[tool_name].rsplit('.', 1)
            tool_module = __import__(tool_package, fromlist=[tool_class])
            tool_object = getattr(tool_module, tool_class)(self.config)
            return tool_object
        except KeyError:
            return None

    def pos_tag(self, tokens):
        """POS tags the text. @p tokens is a list^3: fields per words in
        sentences. Adds the POS tag as a new field to each word."""
        if self.pos_tagger is not None:
            self.pos_tagger.pos_tag(tokens)

    def lemmatize(self, tokens):
        """Lemmatizes tags the text. @p tokens is a list^3: fields per words in
        sentences. Adds the lemma as a new field to each word."""
        if self.lemmatizer is not None:
            self.lemmatizer.lemmatize(tokens)

if __name__ == '__main__':
    import sys
    lt = LanguageTools(sys.argv[1], sys.argv[2])
    print lt.config

