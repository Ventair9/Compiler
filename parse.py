import sys
from main import *

class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter
        
        self.symbols = set() # Variables declared so far.
        self.labeIsDeclared = set() # Labels declares so far.
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
    
    def abort(self, message):
        sys.exit("Error" +  message)
        
    #Production rules.
    
    #Program ::= {statement}
    def program(self):
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void){")
        
        # Since some newlines are required in our grammar, we need to skip the excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
            
        # Parse all the statements in the program.
        while not self.checkToken(TokenType.EOF):
            self.statement()
            
        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")
        
        for label in self.labelIsGotoed:
            if label not in self.labeIsDeclared:
                self.abort("Attempting to GOTO to undeclared label" + label)

    def statement(self):
        # Check the first token to see what kind of statement it is.
        
        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            self.nextToken()
            
            if self.checkToken(TokenType.STRING):
                # Simple String
                self.emitter.emitLine("printf(\"" + self.currentToken.text + "\\n\");")
                self.nextToken()
            else:
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emitLine("));")
        # "IF " comparison "THEN" {statement} "ENDIF"
        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.emitter.emit("if(")
            self.comparison()
            
            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")
            
            while not self.checkToken(TokenType.ENDIF):
                self.statement()
            
            self.match(TokenType.ENDIF)
            self.emitter.emitLine("}")
            
        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            self.emitter.emit("while(")
            self.comparison()
            
            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")
        # Zero or more statements in the loop body
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()
                
            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("}")
                
        # "LABEL" indent
        elif self.checkToken(TokenType.LABEL):
            self.nextToken()
            if self.currentToken.text in self.labelIsDeclared:
                self.abort("Label already exists: " + self.currentToken.text)
            self.labeIsDeclared.add(self.currentToken.text)
            
            self.emitter.emitLine(self.currentToken.text + ":")
            self.match(TokenType.IDENT)
            
        # "GOTO" ident
        elif self.checkToken(TokenType.GOTO):
            self.nextToken()
            self.labelIsGotoed.add(self.currentToken.text)
            self.emitter.emitLine("goto " + self.currentToken.text + ";")
            self.match(TokenType.IDENT)
            
        # "LET" ident "=" expression
        elif self.checkToken(TokenType.LET):
            
            self.nextToken()
            if self.currentToken.text not in self.symbols:
                self.symbols.add(self.currentToken.text)
                self.emitter.headerLine("float " + self.currentToken.text + ";")
                
            self.emitter.emit(self.currentToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            
            self.expression()
            self.emitter.emitLine(";")
            
        # "INPUT" ident
        elif self.checkToken(TokenType.INPUT):
            
            self.nextToken()
            if self.currentToken.text not in self.symbols:
                self.symbols.add(self.currentToken.text)
                self.emitter.headerLine("float" + self.currentToken.text + ";")
            self.emitter.emitLine("if(0 == scanf(\"%" + "f\", &" + self.currentToken.text + ")) {")
            self.emitter.emitLine(self.currentToken.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)
       # else:
       #     self.abort("Invalid Statement at " + self.currentToken.text + " (" + self.currentToken.kind.name + ")")

        self.nl()
        
    # nl ::= "\n"+
    def nl(self):
        
        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
            
    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        
        self.expression()
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.currentToken.text)
            
        while self.isComparisonOperator():
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
            self.expression()
            
            
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)
    
    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
            
            self.term()
            # Can have 0 or more +/- and expression.
            while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
                self.emitter.emit(self.currentToken.text)
                self.nextToken()
                self.term()
                
    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        
        self.unary()
        # Can have 0 or more *// and expression.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
            self.unary()
            
    # unary ::= ["+" | "-"] primary
    def unary(self):
        
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
        self.primary()
        
    # primary ::= number | ident
    def primary(self):
        
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure the variable already exists
            if self.currentToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.currentToken.text)
            self.emitter.emit(self.currentToken.text)
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.currentToken.text)
            
            