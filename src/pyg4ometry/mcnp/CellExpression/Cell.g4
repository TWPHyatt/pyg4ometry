grammar Cell;

// Lexer rules

COMPLEMENT_CELLNUM   : '#' [1-9]+ ;
UNION                : ':' ;
INTERSECTION         : ' ' ;
LParen               : '(' ;
RParen               : ')' ;
COMPLEMENT           : '#' ;
SENSE                : '-' ;
SURFACENUM           : [0-9]+ ;


// Parser rules
// default order of operations: complements -> intersections -> unions
// lower precedence of the tree first: unions -> intersections -> complements

expr: expressionUnion ;

expressionUnion : expressionIntersection (( UNION ) expressionIntersection)* ;

expressionIntersection : expressionAtom (( INTERSECTION ) expressionAtom)* ;

expressionAtom
    : SURFACENUM
    | LParen expr RParen
    | SENSE SURFACENUM
    | COMPLEMENT_CELLNUM
    | COMPLEMENT LParen expr RParen ;
