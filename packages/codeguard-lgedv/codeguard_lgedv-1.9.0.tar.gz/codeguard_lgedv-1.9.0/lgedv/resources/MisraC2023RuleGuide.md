# MISRA C:2023 Rules Guide

## Directive Dir 1.1:
Definition: Any implementation-defined behavior on which the output of the program depends shall be documented and understood (Since R2024a)

## Directive Dir 2.1:
Definition: All source files shall compile without any compilation errors (Since R2024a)

## Directive Dir 4.1:
Definition: Run-time failures shall be minimized (Since R2024a)

## Directive Dir 4.3:
Definition: Assembly language shall be encapsulated and isolated (Since R2024a)

## Directive Dir 4.4:
Definition: Sections of code should not be "commented out" (Since R2024a)

## Directive Dir 4.5:
Definition: Identifiers in the same name space with overlapping visibility should be typographically unambiguous (Since R2024a)

## Directive Dir 4.6:
Definition: typedefs that indicate size and signedness should be used in place of the basic numerical types (Since R2024a)

## Directive Dir 4.7:
Definition: If a function returns error information, then that error information shall be tested (Since R2024a)

## Directive Dir 4.8:
Definition: If a pointer to a structure or union is never dereferenced within a translation unit, then the implementation of the object should be hidden (Since R2024a)

## Directive Dir 4.9:
Definition: A function should be used in preference to a function-like macro where they are interchangeable (Since R2024a)

## Directive Dir 4.10:
Definition: Precautions shall be taken in order to prevent the contents of a header file being included more than once (Since R2024a)

## Directive Dir 4.11:
Definition: The validity of values passed to library functions shall be checked (Since R2024a)

## Directive Dir 4.12:
Definition: Dynamic memory allocation shall not be used (Since R2024a)

## Directive Dir 4.13:
Definition: Functions which are designed to provide operations on a resource should be called in an appropriate sequence (Since R2024a)

## Directive Dir 4.14:
Definition: The validity of values received from external sources shall be checked (Since R2024a)

## Directive Dir 4.15:
Definition: Evaluation of floating-point expressions shall not lead to the undetected generation of infinities and NaNs (Since R2024a)

## Directive Dir 5.1:
Definition: There shall be no data races between threads (Since R2024b)

## Directive Dir 5.2:
Definition: There shall be no deadlocks between threads (Since R2024b)

## Rule 1.1:
Definition: The program shall contain no violations of the standard C syntax and constraints, and shall not exceed the implementation's translation limits (Since R2024a)

## Rule 1.2:
Definition: Language extensions should not be used (Since R2024a)

## Rule 1.3:
Definition: There shall be no occurrence of undefined or critical unspecified behaviour (Since R2024a)

## Rule 1.4:
Definition: Emergent language features shall not be used (Since R2024a)

## Rule 1.5:
Definition: Obsolescent language features shall not be used (Since R2024a)

## Rule 2.1:
Definition: A project shall not contain unreachable code (Since R2024a)

## Rule 2.2:
Definition: A project shall not contain dead code (Since R2024a)

## Rule 2.3:
Definition: A project should not contain unused type declarations (Since R2024a)

## Rule 2.4:
Definition: A project should not contain unused tag declarations (Since R2024a)

## Rule 2.5:
Definition: A project should not contain unused macro definitions (Since R2024a)

## Rule 2.6:
Definition: A function should not contain unused label declarations (Since R2024a)

## Rule 2.7:
Definition: A function should not contain unused parameters (Since R2024a)

## Rule 2.8:
Definition: A project should not contain unused object definitions (Since R2024b)

## Rule 3.1:
Definition: The character sequences /* and // shall not be used within a comment (Since R2024a)

## Rule 3.2:
Definition: Line-splicing shall not be used in // comments (Since R2024a)

## Rule 4.1:
Definition: Octal and hexadecimal escape sequences shall be terminated (Since R2024a)

## Rule 4.2:
Definition: Trigraphs should not be used (Since R2024a)

## Rule 5.1:
Definition: External identifiers shall be distinct (Since R2024a)

## Rule 5.2:
Definition: Identifiers declared in the same scope and name space shall be distinct (Since R2024a)

## Rule 5.3:
Definition: An identifier declared in an inner scope shall not hide an identifier declared in an outer scope (Since R2024a)

## Rule 5.4:
Definition: Macro identifiers shall be distinct (Since R2024a)

## Rule 5.5:
Definition: Identifiers shall be distinct from macro names (Since R2024a)

## Rule 5.6:
Definition: A typedef name shall be a unique identifier (Since R2024a)

## Rule 5.7:
Definition: A tag name shall be a unique identifier (Since R2024a)

## Rule 5.8:
Definition: Identifiers that define objects or functions with external linkage shall be unique (Since R2024a)

## Rule 5.9:
Definition: Identifiers that define objects or functions with internal linkage should be unique (Since R2024a)

## Rule 6.1:
Definition: Bit-fields shall only be declared with an appropriate type (Since R2024a)

## Rule 6.2:
Definition: Single-bit named bit-fields shall not be of a signed type (Since R2024a)

## Rule 6.3:
Definition: A bit field shall not be declared as a member of a union (Since R2024a)

## Rule 7.1:
Definition: Octal constants shall not be used (Since R2024a)

## Rule 7.2:
Definition: A "u" or "U" suffix shall be applied to all integer constants that are represented in an unsigned type (Since R2024a)

## Rule 7.3:
Definition: The lowercase character "l" shall not be used in a literal suffix (Since R2024a)

## Rule 7.4:
Definition: A string literal shall not be assigned to an object unless the object's type is "pointer to const-qualified char" (Since R2024a)

## Rule 7.5:
Definition: The argument of an integer constant macro shall have an appropriate form (Since R2024a)

## Rule 7.6:
Definition: The small integer variants of the minimum-width integer constant macros shall not be used (Since R2025a)

## Rule 8.1:
Definition: Types shall be explicitly specified (Since R2024a)

## Rule 8.2:
Definition: Function types shall be in prototype form with named parameters (Since R2024a)

## Rule 8.3:
Definition: All declarations of an object or function shall use the same names and type qualifiers (Since R2024a)

## Rule 8.4:
Definition: A compatible declaration shall be visible when an object or function with external linkage is defined (Since R2024a)

## Rule 8.5:
Definition: An external object or function shall be declared once in one and only one file (Since R2024a)

## Rule 8.6:
Definition: An identifier with external linkage shall have exactly one external definition (Since R2024a)

## Rule 8.7:
Definition: Functions and objects should not be defined with external linkage if they are referenced in only one translation unit (Since R2024a)

## Rule 8.8:
Definition: The static storage class specifier shall be used in all declarations of objects and functions that have internal linkage (Since R2024a)

## Rule 8.9:
Definition: An object should be declared at block scope if its identifier only appears in a single function (Since R2024a)

## Rule 8.10:
Definition: An inline function shall be declared with the static storage class (Since R2024a)

## Rule 8.11:
Definition: When an array with external linkage is declared, its size should be explicitly specified (Since R2024a)

## Rule 8.12:
Definition: Within an enumerator list, the value of an implicitly-specified enumeration constant shall be unique (Since R2024a)

## Rule 8.13:
Definition: A pointer should point to a const-qualified type whenever possible (Since R2024a)

## Rule 8.14:
Definition: The restrict type qualifier shall not be used (Since R2024a)

## Rule 8.15:
Definition: The argument of an integer constant macro shall have an appropriate form (Since R2024a)

## Rule 8.16:
Definition: The alignment specification of zero should not appear in an object declaration (Since R2024a)

## Rule 8.17:
Definition: At most one explicit alignment specifier should appear in an object declaration (Since R2024a)

## Rule 9.1:
Definition: The value of an object with automatic storage duration shall not be read before it has been set (Since R2024a)

## Rule 9.2:
Definition: The initializer for an aggregate or union shall be enclosed in braces (Since R2024a)

## Rule 9.3:
Definition: Arrays shall not be partially initialized (Since R2024a)

## Rule 9.4:
Definition: An element of an object shall not be initialized more than once (Since R2024a)

## Rule 9.5:
Definition: Where designated initializers are used to initialize an array object the size of the array shall be specified explicitly (Since R2024a)

## Rule 9.6:
Definition: An initializer using chained designators shall not contain initializers without designators (Since R2025a)

## Rule 10.1:
Definition: Operands shall not be of an inappropriate essential type (Since R2024a)

## Rule 10.2:
Definition: Expressions of essentially character type shall not be used inappropriately in addition and subtraction operations (Since R2024a)

## Rule 10.3:
Definition: The value of an expression shall not be assigned to an object with a narrower essential type or of a different essential type category (Since R2024a)

## Rule 10.4:
Definition: Both operands of an operator in which the usual arithmetic conversions are performed shall have the same essential type category (Since R2024a)

## Rule 10.5:
Definition: The value of an expression should not be cast to an inappropriate essential type (Since R2024a)

## Rule 10.6:
Definition: The value of a composite expression shall not be assigned to an object with wider essential type (Since R2024a)

## Rule 10.7:
Definition: If a composite expression is used as one operand of an operator in which the usual arithmetic conversions are performed then the other operand shall not have wider essential type (Since R2024a)

## Rule 10.8:
Definition: The value of a composite expression shall not be cast to a different essential type category or a wider essential type (Since R2024a)

## Rule 11.1:
Definition: Conversions shall not be performed between a pointer to a function and any other type (Since R2024a)

## Rule 11.2:
Definition: Conversions shall not be performed between a pointer to an incomplete type and any other type (Since R2024a)

## Rule 11.3:
Definition: A conversion shall not be performed between a pointer to object type and a pointer to a different object type (Since R2024a)

## Rule 11.4:
Definition: A conversion should not be performed between a pointer to object and an integer type (Since R2024a)

## Rule 11.5:
Definition: A conversion should not be performed from pointer to void into pointer to object (Since R2024a)

## Rule 11.6:
Definition: A cast shall not be performed between pointer to void and an arithmetic type (Since R2024a)

## Rule 11.7:
Definition: A cast shall not be performed between pointer to object and a non-integer arithmetic type (Since R2024a)

## Rule 11.8:
Definition: A conversion shall not remove any const, volatile, or _Atomic qualification from the type pointed to by a pointer (Since R2024a)

## Rule 11.9:
Definition: The macro NULL shall be the only permitted form of integer null pointer constant (Since R2024a)

## Rule 11.10:
Definition: The _Atomic qualifier shall not be applied to the incomplete type void (Since R2024b)

## Rule 12.1:
Definition: The precedence of operators within expressions should be made explicit (Since R2024a)

## Rule 12.2:
Definition: The right hand operand of a shift operator shall lie in the range zero to one less than the width in bits of the essential type of the left hand operand (Since R2024a)

## Rule 12.3:
Definition: The comma operator should not be used (Since R2024a)

## Rule 12.4:
Definition: Evaluation of constant expressions should not lead to unsigned integer wrap-around (Since R2024a)

## Rule 12.5:
Definition: The sizeof operator shall not have an operand which is a function parameter declared as "array of type" (Since R2024a)

## Rule 12.6:
Definition: Structure and union members of atomic objects shall not be directly accessed (Since R2025a)

## Rule 13.1:
Definition: Initializer lists shall not contain persistent side effects (Since R2024a)

## Rule 13.2:
Definition: The value of an expression and its persistent side effects shall be the same under all permitted evaluation orders and shall be independent from thread interleaving (Since R2024a)

## Rule 13.3:
Definition: A full expression containing an increment (++) or decrement (--) operator should have no other potential side effects other than that caused by the increment or decrement operator (Since R2024a)

## Rule 13.4:
Definition: The result of an assignment operator should not be used (Since R2024a)

## Rule 13.5:
Definition: The right hand operand of a logical && or || operator shall not contain persistent side effects (Since R2024a)

## Rule 13.6:
Definition: The operand of the sizeof operator shall not contain any expression which has potential side effects (Since R2024a)

## Rule 14.1:
Definition: A loop counter shall not have essentially floating type (Since R2024a)

## Rule 14.2:
Definition: A for loop shall be well-formed (Since R2024a)

## Rule 14.3:
Definition: Controlling expressions shall not be invariant (Since R2024a)

## Rule 14.4:
Definition: The controlling expression of an if statement and the controlling expression of an iteration-statement shall have essentially Boolean type (Since R2024a)

## Rule 15.1:
Definition: The goto statement should not be used (Since R2024a)

## Rule 15.2:
Definition: The goto statement shall jump to a label declared later in the same function (Since R2024a)

## Rule 15.3:
Definition: Any label referenced by a goto statement shall be declared in the same block, or in any block enclosing the goto statement (Since R2024a)

## Rule 15.4:
Definition: There should be no more than one break or goto statement used to terminate any iteration statement (Since R2024a)

## Rule 15.5:
Definition: A function should have a single point of exit at the end (Since R2024a)

## Rule 15.6:
Definition: The body of an iteration-statement or a selection-statement shall be a compound statement (Since R2024a)

## Rule 15.7:
Definition: All if … else if constructs shall be terminated with an else statement (Since R2024a)

## Rule 16.1:
Definition: All switch statements shall be well-formed (Since R2024a)

## Rule 16.2:
Definition: A switch label shall only be used when the most closely-enclosing compound statement is the body of a switch statement (Since R2024a)

## Rule 16.3:
Definition: An unconditional break statement shall terminate every switch-clause (Since R2024a)

## Rule 16.4:
Definition: Every switch statement shall have a default label (Since R2024a)

## Rule 16.5:
Definition: A default label shall appear as either the first or the last switch label of a switch statement (Since R2024a)

## Rule 16.6:
Definition: Every switch statement shall have at least two switch-clauses (Since R2024a)

## Rule 16.7:
Definition: A switch-expression shall not have essentially Boolean type (Since R2024a)

## Rule 17.1:
Definition: The standard header file <stdarg.h> shall not be used (Since R2024a)

## Rule 17.2:
Definition: Functions shall not call themselves, either directly or indirectly (Since R2024a)

## Rule 17.3:
Definition: A function shall not be declared implicitly (Since R2024a)

## Rule 17.4:
Definition: All exit paths from a function with non-void return type shall have an explicit return statement with an expression (Since R2024a)

## Rule 17.5:
Definition: The function argument corresponding to a parameter declared to have an array type shall have an appropriate number of elements (Since R2024a)

## Rule 17.6:
Definition: The declaration of an array parameter shall not contain the static keyword between the [ ] (Since R2024a)

## Rule 17.7:
Definition: The value returned by a function having non-void return type shall be used (Since R2024a)

## Rule 17.8:
Definition: A function parameter should not be modified (Since R2024a)

## Rule 17.9:
Definition: A function declared with a _Noreturn function specifier shall not return to its caller (Since R2024a)

## Rule 17.10:
Definition: A function declared with a _Noreturn function specifier shall have void return type (Since R2024a)

## Rule 17.11:
Definition: A function that never returns should be declared with a _Noreturn function specifier (Since R2024a)

## Rule 17.12:
Definition: A function identifier should only be used with either a preceding &, or with a parenthesized parameter list (Since R2024a)

## Rule 17.13:
Definition: A function type shall not be type qualified (Since R2024a)

## Rule 18.1:
Definition: A pointer resulting from arithmetic on a pointer operand shall address an element of the same array as that pointer operand (Since R2024a)

## Rule 18.2:
Definition: Subtraction between pointers shall only be applied to pointers that address elements of the same array (Since R2024a)

## Rule 18.3:
Definition: The relational operators >, >=, < and <= shall not be applied to expressions of pointer type except where they point into the same object (Since R2024a)

## Rule 18.4:
Definition: The +, -, += and -= operators should not be applied to an expression of pointer type (Since R2024a)

## Rule 18.5:
Definition: Declarations should contain no more than two levels of pointer nesting (Since R2024a)

## Rule 18.6:
Definition: The address of an object with automatic or thread-local storage shall not be copied to another object that persists after the first object has ceased to exist (Since R2024a)

## Rule 18.7:
Definition: Flexible array members shall not be declared (Since R2024a)

## Rule 18.8:
Definition: Variable-length arrays shall not be used (Since R2024a)

## Rule 18.9:
Definition: An object with temporary lifetime shall not undergo array-to-pointer conversion (Since R2024a)

## Rule 18.10:
Definition: Pointers to variably-modified array types shall not be used (Since R2025a)

## Rule 19.1:
Definition: An object shall not be assigned or copied to an overlapping object (Since R2024a)

## Rule 19.2:
Definition: The union keyword should not be used (Since R2024a)

## Rule 20.1:
Definition: #include directives should only be preceded by preprocessor directives or comments (Since R2024a)

## Rule 20.2:
Definition: The ', " or \ characters and the /* or // character sequences shall not occur in a header file name (Since R2024a)

## Rule 20.3:
Definition: The #include directive shall be followed by either a <filename> or "filename" sequence (Since R2024a)

## Rule 20.4:
Definition: A macro shall not be defined with the same name as a keyword (Since R2024a)

## Rule 20.5:
Definition: #undef should not be used (Since R2024a)

## Rule 20.6:
Definition: Tokens that look like a preprocessing directive shall not occur within a macro argument (Since R2024a)

## Rule 20.7:
Definition: Expressions resulting from the expansion of macro parameters shall be enclosed in parentheses (Since R2024a)

## Rule 20.8:
Definition: The controlling expression of a #if or #elif preprocessing directive shall evaluate to 0 or 1 (Since R2024a)

## Rule 20.9:
Definition: All identifiers used in the controlling expression of #if or #elif preprocessing directives shall be #define'd before evaluation (Since R2024a)

## Rule 20.10:
Definition: The # and ## preprocessor operators should not be used (Since R2024a)

## Rule 20.11:
Definition: A macro parameter immediately following a # operator shall not immediately be followed by a ## operator (Since R2024a)

## Rule 20.12:
Definition: A macro parameter used as an operand to the # or ## operators, which is itself subject to further macro replacement, shall only be used as an operand to these operators (Since R2024a)

## Rule 20.13:
Definition: A line whose first token is # shall be a valid preprocessing directive (Since R2024a)

## Rule 20.14:
Definition: All #else, #elif and #endif preprocessor directives shall reside in the same file as the #if, #ifdef or #ifndef directive to which they are related (Since R2024a)

## Rule 21.1:
Definition: #define and #undef shall not be used on a reserved identifier or reserved macro name (Since R2024a)

## Rule 21.2:
Definition: A reserved identifier or reserved macro name shall not be declared (Since R2024a)

## Rule 21.3:
Definition: The memory allocation and deallocation functions of <stdlib.h> shall not be used (Since R2024a)

## Rule 21.4:
Definition: The standard header file <setjmp.h> shall not be used (Since R2024a)

## Rule 21.5:
Definition: The standard header file <signal.h> shall not be used (Since R2024a)

## Rule 21.6:
Definition: The Standard Library input/output functions shall not be used (Since R2024a)

## Rule 21.7:
Definition: The Standard Library functions atof, atoi, atol, and atoll functions of <stdlib.h> shall not be used (Since R2024a)

## Rule 21.8:
Definition: The Standard Library termination functions of <stdlib.h> shall not be used (Since R2024a)

## Rule 21.9:
Definition: The Standard Library library functions bsearch and qsort of <stdlib.h> shall not be used (Since R2024a)

## Rule 21.10:
Definition: The Standard Library time and date functions shall not be used (Since R2024a)

## Rule 21.11:
Definition: The standard header file <tgmath.h> should not be used (Since R2024a)

## Rule 21.12:
Definition: The standard header file <fenv.h> shall not be used (Since R2024a)

## Rule 21.13:
Definition: Any value passed to a function in <ctype.h> shall be representable as an unsigned char or be the value EOF (Since R2024a)

## Rule 21.14:
Definition: The Standard Library function memcmp shall not be used to compare null terminated strings (Since R2024a)

## Rule 21.15:
Definition: The pointer arguments to the Standard Library functions memcpy, memmove and memcmp shall be pointers to qualified or unqualified versions of compatible types (Since R2024a)

## Rule 21.16:
Definition: The pointer arguments to the Standard Library function memcmp shall point to either a pointer type, an essentially signed type, an essentially unsigned type, an essentially Boolean type or an essentially enum type (Since R2024a)

## Rule 21.17:
Definition: Use of the string handling function from <string.h> shall not result in accesses beyond the bounds of the objects referenced by their pointer parameters (Since R2024a)

## Rule 21.18:
Definition: The size_t argument passed to any function in <string.h> shall have an appropriate value (Since R2024a)

## Rule 21.19:
Definition: The pointers returned by the Standard Library functions localeconv, getenv, setlocale or strerror shall only be used as if they have pointer to const-qualified type (Since R2024a)

## Rule 21.20:
Definition: The pointer returned by the Standard Library functions asctime, ctime, gmtime, localtime, localeconv, getenv, setlocale or strerror shall not be used following a subsequent call to the same function (Since R2024a)

## Rule 21.21:
Definition: The Standard Library function system of <stdlib.h> shall not be used (Since R2024a)

## Rule 21.22:
Definition: All operand arguments to any type-generic macros declared in <tgmath.h> shall have an appropriate essential type (Since R2024a)

## Rule 21.23:
Definition: All operand arguments to any multi-argument type-generic macros declared in <tgmath.h> shall have the same standard type (Since R2024a)

## Rule 21.24:
Definition: The random number generator functions of <stdlib.h> shall not be used (Since R2024a)

## Rule 21.25:
Definition: All memory synchronization operations shall be executed in sequentially consistent order (Since R2025a)

## Rule 22.1:
Definition: All resources obtained dynamically by means of Standard Library functions shall be explicitly released (Since R2024a)

## Rule 22.2:
Definition: A block of memory shall only be freed if it was allocated by means of a Standard Library function (Since R2024a)

## Rule 22.3:
Definition: The same file shall not be open for read and write access at the same time on different streams (Since R2024a)

## Rule 22.4:
Definition: There shall be no attempt to write to a stream which has been opened as read-only (Since R2024a)

## Rule 22.5:
Definition: A pointer to a FILE object shall not be dereferenced (Since R2024a)

## Rule 22.6:
Definition: The value of a pointer to a FILE shall not be used after the associated stream has been closed (Since R2024a)

## Rule 22.7:
Definition: The macro EOF shall only be compared with the unmodified return value from any Standard Library function capable of returning EOF (Since R2024a)

## Rule 22.8:
Definition: The value of errno shall be set to zero prior to a call to an errno-setting-function (Since R2024a)

## Rule 22.9:
Definition: The value of errno shall be tested against zero after calling an errno-setting function (Since R2024a)

## Rule 22.10:
Definition: The value of errno shall only be tested when the last function to be called was an errno-setting function (Since R2024a)

## Rule 22.11:
Definition: A thread that was previously either joined or detached shall not be subsequently joined nor detached (Since R2024b)

## Rule 22.13:
Definition: Thread objects, thread synchronization objects and thread-specific storage pointers shall have appropriate storage duration (Since R2025a)

## Rule 22.15:
Definition: Thread synchronization objects and thread-specific storage pointers shall not be destroyed until after all threads accessing them have terminated (Since R2024b)

## Rule 22.16:
Definition: All mutex objects locked by a thread shall be explicitly unlocked by the same thread (Since R2024b)

## Rule 22.17:
Definition: No thread shall unlock a mutex or call cnd_wait() or cnd_timedwait() for a mutex it has not locked before (Since R2024b)

## Rule 22.18:
Definition: Non-recursive mutexes shall not be recursively locked (Since R2025a)

## Rule 23.1:
Definition: A generic selection should only be expanded from a macro (Since R2024a)

## Rule 23.2:
Definition: A generic selection that is not expanded from a macro shall not contain potential side effects in the controlling expression (Since R2024a)

## Rule 23.3:
Definition: A generic selection should contain at least one non-default association (Since R2024a)

## Rule 23.4:
Definition: A generic association shall list an appropriate type (Since R2024a)

## Rule 23.5:
Definition: A generic selection should not depend on implicit pointer type conversion (Since R2024a)

## Rule 23.6:
Definition: The controlling expression of a generic selection shall have an essential type that matches its standard type (Since R2024a)

## Rule 23.7:
Definition: A generic selection that is expanded from a macro should evaluate its argument only once (Since R2024a)

## Rule 23.8:
Definition: A default association shall appear as either the first or the last association of a generic selection (Since R2024a)