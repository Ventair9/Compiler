import sys
from main import *

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        
        self.symbols = set() # Variables declared so far.
        self.labelsDeclared = set() # Labels declares so far.
        self.labelIsGotoed = set() # Labels goto'ed so far.
        
        self.currentToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()
    
    def checkToken(self, kind):
        return kind == self.currentToken.kind
    
    def checkPeek(self, kind):
        return kind == self.peekToken.kind
    
    def match(self, kind):
        # Tries to match the current token. If not current token, advances the current token.
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.currentToken.kind.name)
        self.nextToken()

    def nextToken(self):
        self.currentToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        
    def __init__(self, lexer):
        self.lexer = lexer
        
        self.currentToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()
    
    def abort(self, message):
        sys.exit("Error" +  message)
        
    #Production rules.
    
    #Program ::= {statement}
    def program(self):
        print("PROGRAM")
        
        # Since some newlines are required in our grammar, need to skip the excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        # Parse all the statements in the program.
        while not self.checkToken(TokenType.EOF):
            self.statement()
            
            
    def statement(self):
        # Check the first token to see what kind of statement it is.
        
        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.nextToken()
            
            if self.checkToken(TokenType.STRING):
                # Simple String
                self.nextToken()
            else:
                self.expression()
        # "IF " comparison "THEN" {statement} "ENDIF"
        elif self.checkToken(TokenType.IF):
            print("STATEMENT-IF")
            self.nextToken()
            self.comparison()
            
            self.match(TokenType.THEN)
            self.nl()
        # Zero or more statements in the body
            while not self.checkToken(TokenType.ENDIF):
                self.statement()
                
            self.match(TokenType.ENDIF)
            
        elif self.checkToken(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.nextToken()
            self.comparison()
            
            self.match(TokenType.REPEAT)
            self.nl()
            
            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()
                
            self.match(TokenType.ENDWHILE)
        # "LABEL" indent
        elif self.checkToken(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.nextToken()
            self.match(TokenType.IDENT)
            
        # "GOTO" indent
        elif self.checkToken(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.nextToken()
            self.match(TokenType.IDENT)
            
        # "LET" ident "=" expression
        elif self.checkToken(TokenType.LET):
            print("STATEMENT-LET")
            self.nextToken()
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            
        # "INPUT" ident
        elif self.checkToken(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.nextToken()
            self.match(TokenType.IDENT)
        else:
            self.abort("Invalid Statement at " + self.currentToken.text + " (" + self.currentToken.kind.name + ")")
            
        self.nl()
        
    # nl ::= "\n"+
    def nl(self):
        print("NEWLINE")
        
        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
            
    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        print("COMPARISON")
        
        self.expression()
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.currentToken.text)
            
        while self.isComparisonOperator():
            self.nextToken()
            self.expression()
            
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)
    
    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
            print("EXPRESSION")
            
            self.term()
            # Can have 0 or more +/- and expression.
            while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
                self.nextToken()
                self.term()
                
    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        print("TERM")
        
        self.unary()
        # Can have 0 or more *// and expression.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.nextToken()
            self.unary()
            
    # unary ::= ["+" | "-"] primary
    def unary(self):
        print("UNARY")
        
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.nextToken()
        self.primary()
        
    # primary ::= number | ident
    def primary(self):
        print("PRIMARY (" + self.currentToken.text + ")")
        
        if self.checkToken(TokenType.NUMBER):
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.currentToken.text)
            
            