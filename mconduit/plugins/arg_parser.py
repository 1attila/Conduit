from typing import Tuple, Union, List


class QuoteNotClosedError(Exception):
    ...

class WrongArguments(Exception):
    ...


class Quote(str):
    """
    Utility class used to represent quotes
    """


class Parser:
    """
    Command argument parser

    Input pipeline:

    1. separate_strings
    2. Reserved (dict syntax parsing)
    3. split_spaces
    4. separate_flags (optional)
    """

    QUOTES = ["'", '"']


    def parse_args(self, input: str) -> Tuple[List[str], List[str]]:
        """
        Parses command arguments and flags.

        Supports dict syntaxt
        """

        processed = self.separate_strings(input)

        if self.has_dict_syntax(processed):
            processed = self.parse_dict_syntax(processed)

        processed = self.split_spaces(processed)
        args, flags = self.separate_flags(processed)

        return args, flags

    
    def separate_strings(self, input: str) -> List[str | Quote]:
        """
        Return a list with all the quotes characters joint.

        Empty strings are discarded
        """

        temp_param: str = ""
        args: List[str | Quote] = []
        in_quote = False
        quote = ""

        for item in input:
            
            if in_quote and item == quote:
                
                if len(temp_param) > 0:
                    args.append(Quote(temp_param))
                temp_param = ""
                quote = ""
                in_quote = False
            
            elif item in self.QUOTES:
                
                if len(temp_param) > 0:
                    args.append(temp_param)
                temp_param = ""
                quote = item
                in_quote = True

            else:
                temp_param += item

        if len(temp_param) > 0:
            
            if in_quote:
                raise QuoteNotClosedError()
            else:
                args.append(temp_param)
            
        return args
    

    def has_dict_syntax(self, text_chunks: List[str | Quote]) -> bool:
        """
        Returns True if the string has the ":" character in it's chunks that are not quotes
        """

        for chunk in text_chunks:

            if not isinstance(chunk, Quote) and ":" in chunk:
                return True

        return False

    
    def parse_dict_syntax(self, text_chunks: List[str | Quote]) -> List[str]:
        raise NotImplementedError

    
    def split_spaces(self, text_chunks: List[str | Quote]) -> List[str]:

        new_chunks = []

        for chunk in text_chunks:
            
            if not isinstance(chunk, Quote):

                words = chunk.split(" ")
                
                for word in words:
                    
                    word = word.strip()

                    if len(word) > 0:
                        new_chunks.append(word)
            else:
                new_chunks.append(chunk)
        
        return new_chunks
    
    
    def separate_flags(self, text_chunks: List[str]) -> Tuple[List[str], List[str]]:
        
        new_chunks = []
        flags = []
        raise_flag = False

        for chunk in text_chunks:
            
            if chunk.startswith("--"):
                flags.append(chunk)
                raise_flag = True
            else:
                if raise_flag:
                    raise WrongArguments("Flags can be placed only at the end!")
                
                new_chunks.append(chunk)

        return new_chunks, flags