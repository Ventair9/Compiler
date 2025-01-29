import enum
import sys

#BASIC dialect compiler
#source code -> Lexer >tokens< -> Parser>program tree< -> Ermitter -> compiled code

class Lexer:
    def __init__(self, source):
        self.source = source + "\n"
        self.currentChar = ""
        self.currentPos = -1
        self.nextChar()
        
    
    #processing the next character.
    def nextChar(self):
        self.currentPos += 1
        if self.currentPos >= len(self.source):
            self.currentChar = "\0"
        else:
            self.currentChar = self.source[self.currentPos]
    
    #return lookahead character.
    def peek(self):
        if self.currentPos + 1 >= len(self.source):
            return "\0"
        return self.source[self.currentPos+1]
    
    #invalid token func
    def abort(self, message):
        sys.exit("Lexing error. " + message)
    
    #whitespace handling
    def skipWhitespace(self):
        while self.currentChar == " " or self.currentChar == "\t" or self.currentChar == "\r":
            self.nextChar()
    
    #skip comments
    def skipComment(self):
        pass
    
    #return token next
    def getToken(self):
        token = None
        
        if self.currentChar == "+":
            token = Token(self.currentChar, TokenType.PLUS)
        elif self.currentChar == "-":
            token = Token(self.currentChar, TokenType.MINUS)
        elif self.currentChar == "*":
            token = Token(self.currentChar, TokenType.ASTERISK)
        elif self.currentChar == "/":
            token = Token(self.currentChar, TokenType.SLASH)
        elif self.currentChar == "\n":
            token = Token(self.currentChar, TokenType.NEWLINE)
        elif self.currentChar == "\0":
            token = Token("", TokenType.EOF)
        else:
            # Unknown  token!
            self.abort("Unknown token: " + self.currentChar)
    
        self.nextChar()
        return token
        
class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText
        self.kind = tokenKind
        
class TokenType(enum.Enum):
        EOF = -1
        NEWLINE = 0
        NUMBER = 1
        IDENT = 2
        STRING = 3
        # Keywords.
        LABEL = 101
        GOTO = 102
        PRINT = 103
        INPUT = 104
        LET = 105
        IF = 106
        THEN = 107
        ENDIF = 108
        WHILE = 109
        REPEAT = 110
        ENDWHILE = 111
        # Operators.
        EQ = 201  
        PLUS = 202
        MINUS = 203
        ASTERISK = 204
        SLASH = 205
        EQEQ = 206
        NOTEQ = 207
        LT = 208
        LTEQ = 209
        GT = 210
        GTEQ = 211