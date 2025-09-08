# AUTOSAR C++14 Rules Guide

## Rule A0-1-1:
Definition: A project shall not contain instances of non-volatile variables being given values that are not subsequently used (Since R2020b)

## Rule A0-1-2:
Definition: The value returned by a function having a non-void return type that is not an overloaded operator shall be used

## Rule A0-1-3:
Definition: Every function defined in an anonymous namespace, or static function with internal linkage, or private member function shall be used (Since R2020b)

## Rule A0-1-4:
Definition: There shall be no unused named parameters in non-virtual functions

## Rule A0-1-5:
Definition: There shall be no unused named parameters in the set of parameters for a virtual function and all the functions that override it

## Rule A0-1-6:
Definition: There should be no unused type declarations

## Rule A0-4-2:
Definition: Type long double shall not be used

## Rule A0-4-4:
Definition: Range, domain and pole errors shall be checked when using math functions (Since R2022a)

## Rule A1-1-1:
Definition: All code shall conform to ISO/IEC 14882:2014 - Programming Language C++ and shall not use deprecated features

## Rule A2-3-1:
Definition: Only those characters specified in the C++ Language Standard basic source character set shall be used in the source code

## Rule A2-5-1:
Definition: Trigraphs shall not be used

## Rule A2-5-2:
Definition: Digraphs shall not be used

## Rule A2-7-1:
Definition: The character \ shall not occur as a last character of a C++ comment

## Rule A2-7-2:
Definition: Sections of code shall not be "commented out" (Since R2020b)

## Rule A2-7-3:
Definition: All declarations of "user-defined" types, static and non-static data members, functions and methods shall be preceded by documentation (Since R2021a)

## Rule A2-8-1:
Definition: A header file name should reflect the logical entity for which it provides declarations (Since R2021a)

## Rule A2-8-2:
Definition: An implementation file name should reflect the logical entity for which it provides definitions (Since R2021a)

## Rule A2-10-1:
Definition: An identifier declared in an inner scope shall not hide an identifier declared in an outer scope

## Rule A2-10-4:
Definition: The identifier name of a non-member object with static storage duration or static function shall not be reused within a namespace (Since R2020b)

## Rule A2-10-5:
Definition: An identifier name of a function with static storage duration or a non-member object with external or internal linkage should not be reused (Since R2020b)

## Rule A2-10-6:
Definition: A class or enumeration name shall not be hidden by a variable, function or enumerator declaration in the same scope

## Rule A2-11-1:
Definition: Volatile keyword shall not be used

## Rule A2-13-1:
Definition: Only those escape sequences that are defined in ISO/IEC 14882:2014 shall be used

## Rule A2-13-2:
Definition: String literals with different encoding prefixes shall not be concatenated

## Rule A2-13-3:
Definition: Type wchar_t shall not be used

## Rule A2-13-4:
Definition: String literals shall not be assigned to non-constant pointers

## Rule A2-13-5:
Definition: Hexadecimal constants should be uppercase

## Rule A2-13-6:
Definition: Universal character names shall be used only inside character or string literals

## Rule A3-1-1:
Definition: It shall be possible to include any header file in multiple translation units without violating the One Definition Rule

## Rule A3-1-2:
Definition: Header files, that are defined locally in the project, shall have a file name extension of one of: .h, .hpp or .hxx

## Rule A3-1-3:
Definition: Implementation files, that are defined locally in the project, should have a file name extension of ".cpp"

## Rule A3-1-4:
Definition: When an array with external linkage is declared, its size shall be stated explicitly

## Rule A3-1-5:
Definition: A function definition shall only be placed in a class definition if (1) the function is intended to be inlined (2) it is a member function template (3) it is a member function of a class template (Since R2020b)

## Rule A3-1-6:
Definition: Trivial accessor and mutator functions should be inlined (Since R2020b)

## Rule A3-3-1:
Definition: Objects or functions with external linkage (including members of named namespaces) shall be declared in a header file

## Rule A3-3-2:
Definition: Static and thread-local objects shall be constant-initialized

## Rule A3-8-1:
Definition: An object shall not be accessed outside of its lifetime (Since R2020b)

## Rule A3-9-1:
Definition: Fixed width integer types from <cstdint>, indicating the size and signedness, shall be used in place of the basic numerical types

## Rule A4-5-1:
Definition: Expressions with type enum or enum class shall not be used as operands to built-in and overloaded operators other than the subscript operator [], the assignment operator =, the equality operators == and !=, the unary & operator, and the relational operators <, <=, >, >=

## Rule A4-7-1:
Definition: An integer expression shall not lead to data loss (Since R2021b)

## Rule A4-10-1:
Definition: Only nullptr literal shall be used as the null-pointer-constraint

## Rule A5-0-1:
Definition: The value of an expression shall be the same under any order of evaluation that the standard permits

## Rule A5-0-2:
Definition: The condition of an if-statement and the condition of an iteration statement shall have type bool

## Rule A5-0-3:
Definition: The declaration of objects shall contain no more than two levels of pointer indirection

## Rule A5-0-4:
Definition: Pointer arithmetic shall not be used with pointers to non-final classes

## Rule A5-1-1:
Definition: Literal values shall not be used apart from type initialization, otherwise symbolic names shall be used instead

## Rule A5-1-2:
Definition: Variables shall not be implicitly captured in a lambda expression

## Rule A5-1-3:
Definition: Parameter list (possibly empty) shall be included in every lambda expression

## Rule A5-1-4:
Definition: A lambda expression object shall not outlive any of its reference-captured objects

## Rule A5-1-6:
Definition: Return type of a non-void return type lambda expression should be explicitly specified (Since R2020b)

## Rule A5-1-7:
Definition: A lambda shall not be an operand to decltype or typeid

## Rule A5-1-8:
Definition: Lambda expressions should not be defined inside another lambda expression (Since R2020b)

## Rule A5-1-9:
Definition: Identical unnamed lambda expressions shall be replaced with a named function or a named lambda expression (Since R2020b)

## Rule A5-2-1:
Definition: dynamic_cast should not be used (Since R2020b)

## Rule A5-2-2:
Definition: Traditional C-style casts shall not be used

## Rule A5-2-3:
Definition: A cast shall not remove any const or volatile qualification from the type of a pointer or reference

## Rule A5-2-4:
Definition: reinterpret_cast shall not be used

## Rule A5-2-5:
Definition: An array or container shall not be accessed beyond its range (Since R2022a)

## Rule A5-2-6:
Definition: The operands of a logical && or || shall be parenthesized if the operands contain binary operators

## Rule A5-3-1:
Definition: Evaluation of the operand to the typeid operator shall not contain side effects (Since R2020b)

## Rule A5-3-2:
Definition: Null pointers shall not be dereferenced (Since R2020b)

## Rule A5-3-3:
Definition: Pointers to incomplete class types shall not be deleted

## Rule A5-5-1:
Definition: A pointer to member shall not access non-existent class members (Since R2022a)

## Rule A5-6-1:
Definition: The right hand operand of the integer division or remainder operators shall not be equal to zero

## Rule A5-10-1:
Definition: A pointer to member virtual function shall only be tested for equality with null-pointer-constant (Since R2020b)

## Rule A5-16-1:
Definition: The ternary conditional operator shall not be used as a sub-expression

## Rule A6-2-1:
Definition: Move and copy assignment operators shall either move or respectively copy base classes and data members of a class, without any side effects (Since R2020b)

## Rule A6-2-2:
Definition: Expression statements shall not be explicit calls to constructors of temporary objects only

## Rule A6-4-1:
Definition: A switch statement shall have at least two case-clauses, distinct from the default label

## Rule A6-5-1:
Definition: A for-loop that loops through all elements of the container and does not use its loop-counter shall not be used (Since R2022a)

## Rule A6-5-2:
Definition: A for loop shall contain a single loop-counter which shall not have floating-point type

## Rule A6-5-3:
Definition: Do statements should not be used (Since R2020b)

## Rule A6-5-4:
Definition: For-init-statement and expression should not perform actions other than loop-counter initialization and modification

## Rule A6-6-1:
Definition: The goto statement shall not be used

## Rule A7-1-1:
Definition: Constexpr or const specifiers shall be used for immutable data declaration (Since R2020b)

## Rule A7-1-2:
Definition: The constexpr specifier shall be used for values that can be determined at compile time (Since R2020b)

## Rule A7-1-3:
Definition: CV-qualifiers shall be placed on the right hand side of the type that is a typedef or a using name

## Rule A7-1-4:
Definition: The register keyword shall not be used

## Rule A7-1-5:
Definition: The auto specifier shall not be used apart from following cases: (1) to declare that a variable has the same type as return type of a function call, (2) to declare that a variable has the same type as initializer of non-fundamental type, (3) to declare parameters of a generic lambda expression, (4) to declare a function template using trailing return type syntax (Since R2020b)

## Rule A7-1-6:
Definition: The typedef specifier shall not be used

## Rule A7-1-7:
Definition: Each expression statement and identifier declaration shall be placed on a separate line

## Rule A7-1-8:
Definition: A non-type specifier shall be placed before a type specifier in a declaration

## Rule A7-1-9:
Definition: A class, structure, or enumeration shall not be declared in the definition of its type

## Rule A7-2-1:
Definition: An expression with enum underlying type shall only have values corresponding to the enumerators of the enumeration (Since R2022a)

## Rule A7-2-2:
Definition: Enumeration underlying type shall be explicitly defined

## Rule A7-2-3:
Definition: Enumerations shall be declared as scoped enum classes

## Rule A7-2-4:
Definition: In an enumeration, either (1) none, (2) the first or (3) all enumerators shall be initialized

## Rule A7-3-1:
Definition: All overloads of a function shall be visible from where it is called

## Rule A7-4-1:
Definition: The asm declaration shall not be used

## Rule A7-5-1:
Definition: A function shall not return a reference or a pointer to a parameter that is passed by reference to const

## Rule A7-5-2:
Definition: Functions shall not call themselves, either directly or indirectly

## Rule A7-6-1:
Definition: Functions declared with the [[noreturn]] attribute shall not return (Since R2020b)

## Rule A8-2-1:
Definition: When declaring function templates, the trailing return type syntax shall be used if the return type depends on the type of parameters

## Rule A8-4-1:
Definition: Functions shall not be defined using the ellipsis notation

## Rule A8-4-2:
Definition: All exit paths from a function with non-void return type shall have an explicit return statement with an expression

## Rule A8-4-3:
Definition: Common ways of passing parameters should be used (Since R2021b)

## Rule A8-4-4:
Definition: Multiple output values from a function should be returned as a struct or tuple (Since R2020b)

## Rule A8-4-5:
Definition: "consume" parameters declared as X && shall always be moved from (Since R2021a)

## Rule A8-4-6:
Definition: "forward" parameters declared as T && shall always be forwarded (Since R2021a)

## Rule A8-4-7:
Definition: "in" parameters for "cheap to copy" types shall be passed by value

## Rule A8-4-8:
Definition: Output parameters shall not be used (Since R2021a)

## Rule A8-4-9:
Definition: "in-out" parameters declared as T & shall be modified (Since R2021a)

## Rule A8-4-10:
Definition: A parameter shall be passed by reference if it can't be NULL (Since R2021a)

## Rule A8-4-11:
Definition: A smart pointer shall only be used as a parameter type if it expresses lifetime semantics (Since R2022b)

## Rule A8-4-12:
Definition: A std::unique_ptr shall be passed to a function as: (1) a copy to express the function assumes ownership (2) an lvalue reference to express that the function replaces the managed object (Since R2022b)

## Rule A8-4-13:
Definition: A std::shared_ptr shall be passed to a function as: (1) a copy to express the function shares ownership (2) an lvalue reference to express that the function replaces the managed object (3) a const lvalue reference to express that the function retains a reference count (Since R2022b)

## Rule A8-4-14:
Definition: Interfaces shall be precisely and strongly typed

## Rule A8-5-0:
Definition: All memory shall be initialized before it is read

## Rule A8-5-1:
Definition: In an initialization list, the order of initialization shall be following: (1) virtual base classes in depth and left to right order of the inheritance graph, (2) direct base classes in left to right order of inheritance list, (3) non-static data members in the order they were declared in the class definition

## Rule A8-5-2:
Definition: Braced-initialization {}, without equals sign, shall be used for variable initialization

## Rule A8-5-3:
Definition: A variable of type auto shall not be initialized using {} or ={} braced-initialization

## Rule A8-5-4:
Definition: If a class has a user-declared constructor that takes a parameter of type std::initializer_list, then it shall be the only constructor apart from special member function constructors (Since R2021a)

## Rule A9-3-1:
Definition: Member functions shall not return non-constant "raw" pointers or references to private or protected data owned by the class

## Rule A9-5-1:
Definition: Unions shall not be used

## Rule A9-6-1:
Definition: Data types used for interfacing with hardware or conforming to communication protocols shall be trivial, standard-layout and only contain members of types with defined sizes

## Rule A10-1-1:
Definition: Class shall not be derived from more than one base class which is not an interface class

## Rule A10-2-1:
Definition: Non-virtual public or protected member functions shall not be redefined in derived classes

## Rule A10-3-1:
Definition: Virtual function declaration shall contain exactly one of the three specifiers: (1) virtual, (2) override, (3) final

## Rule A10-3-2:
Definition: Each overriding virtual function shall be declared with the override or final specifier

## Rule A10-3-3:
Definition: Virtual functions shall not be introduced in a final class

## Rule A10-3-5:
Definition: A user-defined assignment operator shall not be virtual

## Rule A10-4-1:
Definition: Hierarchies should be based on interface classes (Since R2021b)

## Rule A11-0-1:
Definition: A non-POD type should be defined as class (Since R2020b)

## Rule A11-0-2:
Definition: A type defined as struct shall: (1) provide only public data members, (2) not provide any special member functions or methods, (3) not be a base of another struct or class, (4) not inherit from another struct or class

## Rule A11-3-1:
Definition: Friend declarations shall not be used

## Rule A12-0-1:
Definition: If a class declares a copy or move operation, or a destructor, either via "=default", "=delete", or via a user-provided declaration, then all others of these five special member functions shall be declared as well

## Rule A12-0-2:
Definition: Bitwise operations and operations that assume data representation in memory shall not be performed on objects (Since R2020b)

## Rule A12-1-1:
Definition: Constructors shall explicitly initialize all virtual base classes, all direct non-virtual base classes and all non-static data members

## Rule A12-1-2:
Definition: Both NSDMI and a non-static member initializer in a constructor shall not be used in the same type (Since R2020b)

## Rule A12-1-3:
Definition: If all user-defined constructors of a class initialize data members with constant values that are the same across all constructors, then data members shall be initialized using NSDMI instead (Since R2021b)

## Rule A12-1-4:
Definition: All constructors that are callable with a single argument of fundamental type shall be declared explicit

## Rule A12-1-5:
Definition: Common class initialization for non-constant members shall be done by a delegating constructor (Since R2021a)

## Rule A12-1-6:
Definition: Derived classes that do not need further explicit initialization and require all the constructors from the base class shall use inheriting constructors (Since R2020b)

## Rule A12-4-1:
Definition: Destructor of a base class shall be public virtual, public override or protected non-virtual

## Rule A12-4-2:
Definition: If a public destructor of a class is non-virtual, then the class should be declared final (Since R2020b)

## Rule A12-6-1:
Definition: All class data members that are initialized by the constructor shall be initialized using member initializers

## Rule A12-7-1:
Definition: If the behavior of a user-defined special member function is identical to implicitly defined special member function, then it shall be defined "=default" or be left undefined (Since R2021b)

## Rule A12-8-1:
Definition: Move and copy constructors shall move and respectively copy base classes and data members of a class, without any side effects (Since R2021a)

## Rule A12-8-2:
Definition: User-defined copy and move assignment operators should use user-defined no-throw swap function (Since R2021a)

## Rule A12-8-3:
Definition: Moved-from object shall not be read-accessed (Since R2021a)

## Rule A12-8-4:
Definition: Move constructor shall not initialize its class members and base classes using copy semantics (Since R2020b)

## Rule A12-8-5:
Definition: A copy assignment and a move assignment operators shall handle self-assignment

## Rule A12-8-6:
Definition: Copy and move constructors and copy assignment and move assignment operators shall be declared protected or defined "=delete" in base class

## Rule A12-8-7:
Definition: Assignment operators should be declared with the ref-qualifier & (Since R2020b)

## Rule A13-1-2:
Definition: User defined suffixes of the user defined literal operators shall start with underscore followed by one or more letters

## Rule A13-1-3:
Definition: User defined literals operators shall only perform conversion of passed parameters (Since R2021a)

## Rule A13-2-1:
Definition: An assignment operator shall return a reference to "this"

## Rule A13-2-2:
Definition: A binary arithmetic operator and a bitwise operator shall return a "prvalue" (Since R2021a)

## Rule A13-2-3:
Definition: A relational operator shall return a boolean value

## Rule A13-3-1:
Definition: A function that contains "forwarding reference" as its argument shall not be overloaded (Since R2021a)

## Rule A13-5-1:
Definition: If "operator[]" is to be overloaded with a non-const version, const version shall also be implemented

## Rule A13-5-2:
Definition: All user-defined conversion operators shall be defined explicit

## Rule A13-5-3:
Definition: User-defined conversion operators should not be used (Since R2021a)

## Rule A13-5-4:
Definition: If two opposite operators are defined, one shall be defined in terms of the other (Since R2022a)

## Rule A13-5-5:
Definition: Comparison operators shall be non-member functions with identical parameter types and noexcept (Since R2020b)

## Rule A13-6-1:
Definition: Digit sequences separators ' shall only be used as follows: (1) for decimal, every 3 digits, (2) for hexadecimal, every 2 digits, (3) for binary, every 4 digits (Since R2021a)

## Rule A14-1-1:
Definition: A template should check if a specific template argument is suitable for this template (Since R2021b)

## Rule A14-5-1:
Definition: A template constructor shall not participate in overload resolution for a single argument of the enclosing class type (Since R2021a)

## Rule A14-5-2:
Definition: Class members that are not dependent on template class parameters should be defined in a separate base class

## Rule A14-5-3:
Definition: A non-member generic operator shall only be declared in a namespace that does not contain class (struct) type, enum type or union type declarations

## Rule A14-7-1:
Definition: A type used as a template argument shall provide all members that are used by the template (Since R2021b)

## Rule A14-7-2:
Definition: Template specialization shall be declared in the same file (1) as the primary template (2) as a user-defined type, for which the specialization is declared

## Rule A14-8-2:
Definition: Explicit specializations of function templates shall not be used

## Rule A15-0-2:
Definition: At least the basic guarantee for exception safety shall be provided for all operations. In addition, each function may offer either the strong guarantee or the nothrow guarantee (Since R2022a)

## Rule A15-0-3:
Definition: Exception safety guarantee of a called function shall be considered (Since R2022a)

## Rule A15-0-7:
Definition: Exception handling mechanism shall guarantee a deterministic worst-case time execution time (Since R2022a)

## Rule A15-1-1:
Definition: Only instances of types derived from std::exception should be thrown (Since R2020b)

## Rule A15-1-2:
Definition: An exception object shall not be a pointer

## Rule A15-1-3:
Definition: All thrown exceptions should be unique (Since R2020b)

## Rule A15-1-4:
Definition: If a function exits with an exception, then before a throw, the function shall place all objects/resources that the function constructed in valid states or it shall delete them (Since R2021b)

## Rule A15-1-5:
Definition: Exceptions shall not be thrown across execution boundaries (Since R2022b)

## Rule A15-2-1:
Definition: Constructors that are not noexcept shall not be invoked before program startup

## Rule A15-2-2:
Definition: If a constructor is not noexcept and the constructor cannot finish object initialization, then it shall deallocate the object's resources and it shall throw an exception (Since R2021a)

## Rule A15-3-3:
Definition: Main function and a task main function shall catch at least: base class exceptions from all third-party libraries used, std::exception and all otherwise unhandled exceptions (Since R2020b)

## Rule A15-3-4:
Definition: Catch-all (ellipsis and std::exception) handlers shall be used only in (a) main, (b) task main functions, (c) in functions that are supposed to isolate independent components and (d) when calling third-party code that uses exceptions not according to guidelines (Since R2020b)

## Rule A15-3-5:
Definition: A class type exception shall be caught by reference or const reference

## Rule A15-4-1:
Definition: Dynamic exception-specification shall not be used (Since R2021a)

## Rule A15-4-2:
Definition: If a function is declared to be noexcept, noexcept(true) or noexcept(<true condition>), then it shall not exit with an exception

## Rule A15-4-3:
Definition: The noexcept specification of a function shall either be identical across all translation units, or identical or more restrictive between a virtual member function and an overrider (Since R2020b)

## Rule A15-4-4:
Definition: A declaration of non-throwing function shall contain noexcept specification (Since R2021a)

## Rule A15-4-5:
Definition: Checked exceptions that could be thrown from a function shall be specified together with the function declaration and they shall be identical in all function declarations and for all its overriders (Since R2021a)

## Rule A15-5-1:
Definition: All user-provided class destructors, deallocation functions, move constructors, move assignment operators and swap functions shall not exit with an exception. A noexcept exception specification shall be added to these functions as appropriate (Since R2020b)

## Rule A15-5-2:
Definition: Program shall not be abruptly terminated. In particular, an implicit or explicit invocation of std::abort(), std::quick_exit(), std::_Exit(), std::terminate() shall not be done (Since R2021b)

## Rule A15-5-3:
Definition: The std::terminate() function shall not be called implicitly

## Rule A16-0-1:
Definition: The preprocessor shall only be used for unconditional and conditional file inclusion and include guards, and using specific directives

## Rule A16-2-1:
Definition: The ', ", /*, //, \ characters shall not occur in a header file name or in #include directive

## Rule A16-2-2:
Definition: There shall be no unused include directives (Since R2021b)

## Rule A16-2-3:
Definition: An include directive shall be added explicitly for every symbol used in a file (Since R2021b)

## Rule A16-6-1:
Definition: #error directive shall not be used

## Rule A16-7-1:
Definition: The #pragma directive shall not be used

## Rule A17-0-1:
Definition: Reserved identifiers, macros and functions in the C++ standard library shall not be defined, redefined or undefined

## Rule A17-1-1:
Definition: Use of the C Standard Library shall be encapsulated and isolated (Since R2021a)

## Rule A17-6-1:
Definition: Non-standard entities shall not be added to standard namespaces

## Rule A18-0-1:
Definition: The C library facilities shall only be accessed through C++ library headers

## Rule A18-0-2:
Definition: The error state of a conversion from string to a numeric value shall be checked

## Rule A18-0-3:
Definition: The library <clocale> (locale.h) and the setlocale function shall not be used

## Rule A18-1-1:
Definition: C-style arrays shall not be used

## Rule A18-1-2:
Definition: The std::vector<bool> specialization shall not be used

## Rule A18-1-3:
Definition: The std::auto_ptr shall not be used

## Rule A18-1-4:
Definition: A pointer pointing to an element of an array of objects shall not be passed to a smart pointer of single object type (Since R2022a)

## Rule A18-1-6:
Definition: All std::hash specializations for user-defined types shall have a noexcept function call operator

## Rule A18-5-1:
Definition: Functions malloc, calloc, realloc and free shall not be used

## Rule A18-5-2:
Definition: Non-placement new or delete expressions shall not be used

## Rule A18-5-3:
Definition: The form of delete operator shall match the form of new operator used to allocate the memory

## Rule A18-5-4:
Definition: If a project has sized or unsized version of operator 'delete' globally defined, then both sized and unsized versions shall be defined

## Rule A18-5-5:
Definition: Memory management functions shall ensure the following: (a) deterministic behavior resulting with the existence of worst-case execution time, (b) avoiding memory fragmentation, (c) avoid running out of memory, (d) avoiding mismatched allocations or deallocations, (e) no dependence on non-deterministic calls to kernel (Since R2021b)

## Rule A18-5-7:
Definition: If non-real-time implementation of dynamic memory management functions is used in the project, then memory shall only be allocated and deallocated during non-real-time program phases (Since R2022a)

## Rule A18-5-8:
Definition: Objects that do not outlive a function shall have automatic storage duration (Since R2021b)

## Rule A18-5-9:
Definition: Custom implementations of dynamic memory allocation and deallocation functions shall meet the semantic requirements specified in the corresponding "Required behaviour" clause from the C++ Standard (Since R2020b)

## Rule A18-5-10:
Definition: Placement new shall be used only with properly aligned pointers to sufficient storage capacity (Since R2020b)

## Rule A18-5-11:
Definition: "operator new" and "operator delete" shall be defined together (Since R2020b)

## Rule A18-9-1:
Definition: The std::bind shall not be used

## Rule A18-9-2:
Definition: Forwarding values to other functions shall be done via: (1) std::move if the value is an rvalue reference, (2) std::forward if the value is forwarding reference (Since R2020b)

## Rule A18-9-3:
Definition: The std::move shall not be used on objects declared const or const&

## Rule A18-9-4:
Definition: An argument to std::forward shall not be subsequently used (Since R2020b)

## Rule A20-8-1:
Definition: An already-owned pointer value shall not be stored in an unrelated smart pointer (Since R2021a)

## Rule A20-8-2:
Definition: A std::unique_ptr shall be used to represent exclusive ownership (Since R2020b)

## Rule A20-8-3:
Definition: A std::shared_ptr shall be used to represent shared ownership (Since R2020b)

## Rule A20-8-4:
Definition: A std::unique_ptr shall be used over std::shared_ptr if ownership sharing is not required (Since R2022b)

## Rule A20-8-5:
Definition: std::make_unique shall be used to construct objects owned by std::unique_ptr (Since R2020b)

## Rule A20-8-6:
Definition: std::make_shared shall be used to construct objects owned by std::shared_ptr (Since R2020b)

## Rule A20-8-7:
Definition: A std::weak_ptr shall be used to represent temporary shared ownership (Since R2022a)

## Rule A21-8-1:
Definition: Arguments to character-handling functions shall be representable as an unsigned char

## Rule A23-0-1:
Definition: An iterator shall not be implicitly converted to const_iterator

## Rule A23-0-2:
Definition: Elements of a container shall only be accessed via valid references, iterators, and pointers (Since R2022a)

## Rule A25-1-1:
Definition: Non-static data members or captured values of predicate function objects that are state related to this object's identity shall not be copied (Since R2022a)

## Rule A25-4-1:
Definition: Ordering predicates used with associative containers and STL sorting and related algorithms shall adhere to a strict weak ordering relation (Since R2022a)

## Rule A26-5-1:
Definition: Pseudorandom numbers shall not be generated using std::rand()

## Rule A26-5-2:
Definition: Random number engines shall not be default-initialized (Since R2020b)

## Rule A27-0-1:
Definition: Inputs from independent components shall be validated (Since R2021b)

## Rule A27-0-2:
Definition: A C-style string shall guarantee sufficient space for data and the null terminator (Since R2020b)

## Rule A27-0-3:
Definition: Alternate input and output operations on a file stream shall not be used without an intervening flush or positioning call (Since R2020b)

## Rule A27-0-4:
Definition: C-style strings shall not be used (Since R2021a)

## Rule M0-1-1:
Definition: A project shall not contain unreachable code

## Rule M0-1-2:
Definition: A project shall not contain infeasible paths

## Rule M0-1-3:
Definition: A project shall not contain unused variables

## Rule M0-1-4:
Definition: A project shall not contain non-volatile POD variables having only one use (Since R2020b)

## Rule M0-1-8:
Definition: All functions with void return type shall have external side effect(s) (Since R2022a)

## Rule M0-1-9:
Definition: There shall be no dead code

## Rule M0-1-10:
Definition: Every defined function should be called at least once

## Rule M0-2-1:
Definition: An object shall not be assigned to an overlapping object

## Rule M0-3-2:
Definition: If a function generates error information, then that error information shall be tested (Since R2020b)

## Rule M2-7-1:
Definition: The character sequence /* shall not be used within a C-style comment

## Rule M2-10-1:
Definition: Different identifiers shall be typographically unambiguous

## Rule M2-13-2:
Definition: Octal constants (other than zero) and octal escape sequences (other than "\0" ) shall not be used

## Rule M2-13-3:
Definition: A "U" suffix shall be applied to all octal or hexadecimal integer literals of unsigned type

## Rule M2-13-4:
Definition: Literal suffixes shall be upper case

## Rule M3-1-2:
Definition: Functions shall not be declared at block scope

## Rule M3-2-1:
Definition: All declarations of an object or function shall have compatible types

## Rule M3-2-2:
Definition: The One Definition Rule shall not be violated

## Rule M3-2-3:
Definition: A type, object or function that is used in multiple translation units shall be declared in one and only one file

## Rule M3-2-4:
Definition: An identifier with external linkage shall have exactly one definition

## Rule M3-3-2:
Definition: If a function has internal linkage then all re-declarations shall include the static storage class specifier

## Rule M3-4-1:
Definition: An identifier declared to be an object or type shall be defined in a block that minimizes its visibility

## Rule M3-9-1:
Definition: The types used for an object, a function return type, or a function parameter shall be token-for-token identical in all declarations and re-declarations

## Rule M3-9-3:
Definition: The underlying bit representations of floating-point values shall not be used

## Rule M4-5-1:
Definition: Expressions with type bool shall not be used as operands to built-in operators other than the assignment operator =, the logical operators &&, ||, !, the equality operators == and ! =, the unary & operator, and the conditional operator

## Rule M4-5-3:
Definition: Expressions with type (plain) char and wchar_t shall not be used as operands to built-in operators other than the assignment operator =, the equality operators == and ! =, and the unary & operator

## Rule M4-10-1:
Definition: NULL shall not be used as an integer value

## Rule M4-10-2:
Definition: Literal zero (0) shall not be used as the null-pointer-constant

## Rule M5-0-2:
Definition: Limited dependence should be placed on C++ operator precedence rules in expressions

## Rule M5-0-3:
Definition: A cvalue expression shall not be implicitly converted to a different underlying type

## Rule M5-0-4:
Definition: An implicit integral conversion shall not change the signedness of the underlying type

## Rule M5-0-5:
Definition: There shall be no implicit floating-integral conversions

## Rule M5-0-6:
Definition: An implicit integral or floating-point conversion shall not reduce the size of the underlying type

## Rule M5-0-7:
Definition: There shall be no explicit floating-integral conversions of a cvalue expression

## Rule M5-0-8:
Definition: An explicit integral or floating-point conversion shall not increase the size of the underlying type of a cvalue expression

## Rule M5-0-9:
Definition: An explicit integral conversion shall not change the signedness of the underlying type of a cvalue expression

## Rule M5-0-10:
Definition: If the bitwise operators ~and << are applied to an operand with an underlying type of unsigned char or unsigned short, the result shall be immediately cast to the underlying type of the operand

## Rule M5-0-11:
Definition: The plain char type shall only be used for the storage and use of character values

## Rule M5-0-12:
Definition: Signed char and unsigned char type shall only be used for the storage and use of numeric values

## Rule M5-0-14:
Definition: The first operand of a conditional-operator shall have type bool

## Rule M5-0-15:
Definition: Array indexing shall be the only form of pointer arithmetic

## Rule M5-0-16:
Definition: A pointer operand and any pointer resulting from pointer arithmetic using that operand shall both address elements of the same array (Since R2021a)

## Rule M5-0-17:
Definition: Subtraction between pointers shall only be applied to pointers that address elements of the same array

## Rule M5-0-18:
Definition: >, >=, <, <= shall not be applied to objects of pointer type, except where they point to the same array

## Rule M5-0-20:
Definition: Non-constant operands to a binary bitwise operator shall have the same underlying type

## Rule M5-0-21:
Definition: Bitwise operators shall only be applied to operands of unsigned underlying type

## Rule M5-2-2:
Definition: A pointer to a virtual base class shall only be cast to a pointer to a derived class by means of dynamic_cast

## Rule M5-2-3:
Definition: Casts from a base class to a derived class should not be performed on polymorphic types

## Rule M5-2-6:
Definition: A cast shall not convert a pointer to a function to any other pointer type, including a pointer to function type

## Rule M5-2-8:
Definition: An object with integer type or pointer to void type shall not be converted to an object with pointer type

## Rule M5-2-9:
Definition: A cast shall not convert a pointer type to an integral type

## Rule M5-2-10:
Definition: The increment (++) and decrement (--) operators shall not be mixed with other operators in an expression

## Rule M5-2-11:
Definition: The comma operator, && operator and the || operator shall not be overloaded

## Rule M5-2-12:
Definition: An identifier with array type passed as a function argument shall not decay to a pointer

## Rule M5-3-1:
Definition: Each operand of the ! operator, the logical && or the logical || operators shall have type bool

## Rule M5-3-2:
Definition: The unary minus operator shall not be applied to an expression whose underlying type is unsigned

## Rule M5-3-3:
Definition: The unary & operator shall not be overloaded

## Rule M5-3-4:
Definition: Evaluation of the operand to the sizeof operator shall not contain side effects

## Rule M5-8-1:
Definition: The right hand operand of a shift operator shall lie between zero and one less than the width in bits of the underlying type of the left hand operand

## Rule M5-14-1:
Definition: The right hand operand of a logical &&, || operators shall not contain side effects

## Rule M5-18-1:
Definition: The comma operator shall not be used

## Rule M5-19-1:
Definition: Evaluation of constant unsigned integer expressions shall not lead to wrap-around

## Rule M6-2-1:
Definition: Assignment operators shall not be used in sub-expressions

## Rule M6-2-2:
Definition: Floating-point expressions shall not be directly or indirectly tested for equality or inequality

## Rule M6-2-3:
Definition: Before preprocessing, a null statement shall only occur on a line by itself; it may be followed by a comment, provided that the first character following the null statement is a white-space character

## Rule M6-3-1:
Definition: The statement forming the body of a switch, while, do ... while or for statement shall be a compound statement

## Rule M6-4-1:
Definition: An if ( condition ) construct shall be followed by a compound statement. The else keyword shall be followed by either a compound statement, or another if statement

## Rule M6-4-2:
Definition: All if ... else if constructs shall be terminated with an else clause

## Rule M6-4-3:
Definition: A switch statement shall be a well-formed switch statement

## Rule M6-4-4:
Definition: A switch-label shall only be used when the most closely-enclosing compound statement is the body of a switch statement

## Rule M6-4-5:
Definition: An unconditional throw or break statement shall terminate every non-empty switch-clause

## Rule M6-4-6:
Definition: The final clause of a switch statement shall be the default-clause

## Rule M6-4-7:
Definition: The condition of a switch statement shall not have bool type

## Rule M6-5-2:
Definition: If loop-counter is not modified by -- or ++, then, within condition, the loop-counter shall only be used as an operand to <=, <, > or >=

## Rule M6-5-3:
Definition: The loop-counter shall not be modified within condition or statement

## Rule M6-5-4:
Definition: The loop-counter shall be modified by one of: --, ++, -=n, or +=n; where n remains constant for the duration of the loop

## Rule M6-5-5:
Definition: A loop-control-variable other than the loop-counter shall not be modified within condition or expression

## Rule M6-5-6:
Definition: A loop-control-variable other than the loop-counter which is modified in statement shall have type bool

## Rule M6-6-1:
Definition: Any label referenced by a goto statement shall be declared in the same block, or in a block enclosing the goto statement

## Rule M6-6-2:
Definition: The goto statement shall jump to a label declared later in the same function body

## Rule M6-6-3:
Definition: The continue statement shall only be used within a well-formed for loop

## Rule M7-1-2:
Definition: A pointer or reference parameter in a function shall be declared as pointer to const or reference to const if the corresponding object is not modified

## Rule M7-3-1:
Definition: The global namespace shall only contain main, namespace declarations and extern "C" declarations

## Rule M7-3-2:
Definition: The identifier main shall not be used for a function other than the global function main

## Rule M7-3-3:
Definition: There shall be no unnamed namespaces in header files

## Rule M7-3-4:
Definition: Using-directives shall not be used

## Rule M7-3-6:
Definition: Using-directives and using-declarations (excluding class scope or function scope using-declarations) shall not be used in header files

## Rule M7-4-2:
Definition: Assembler instructions shall only be introduced using the asm declaration

## Rule M7-4-3:
Definition: Assembly language shall be encapsulated and isolated

## Rule M7-5-1:
Definition: A function shall not return a reference or a pointer to an automatic variable (including parameters), defined within the function

## Rule M7-5-2:
Definition: The address of an object with automatic storage shall not be assigned to another object that may persist after the first object has ceased to exist (Since R2020b)

## Rule M8-0-1:
Definition: An init-declarator-list or a member-declarator-list shall consist of a single init-declarator or member-declarator respectively

## Rule M8-3-1:
Definition: Parameters in an overriding virtual function shall either use the same default arguments as the function they override, or else shall not specify any default arguments

## Rule M8-4-2:
Definition: The identifiers used for the parameters in a re-declaration of a function shall be identical to those in the declaration

## Rule M8-4-4:
Definition: A function identifier shall either be used to call the function or it shall be preceded by &

## Rule M8-5-2:
Definition: Braces shall be used to indicate and match the structure in the non-zero initialization of arrays and structures

## Rule M9-3-1:
Definition: Const member functions shall not return non-const pointers or references to class-data

## Rule M9-3-3:
Definition: If a member function can be made static then it shall be made static, otherwise if it can be made const then it shall be made const

## Rule M9-6-4:
Definition: Named bit-fields with signed integer type shall have a length of more than one bit (Since R2020b)

## Rule M10-1-1:
Definition: Classes should not be derived from virtual bases

## Rule M10-1-2:
Definition: A base class shall only be declared virtual if it is used in a diamond hierarchy

## Rule M10-1-3:
Definition: An accessible base class shall not be both virtual and non-virtual in the same hierarchy

## Rule M10-2-1:
Definition: All accessible entity names within a multiple inheritance hierarchy should be unique

## Rule M10-3-3:
Definition: A virtual function shall only be overridden by a pure virtual function if it is itself declared as pure virtual

## Rule M11-0-1:
Definition: Member data in non-POD class types shall be private

## Rule M12-1-1:
Definition: An object's dynamic type shall not be used from the body of its constructor or destructor

## Rule M14-5-3:
Definition: A copy assignment operator shall be declared when there is a template assignment operator with a parameter that is a generic parameter

## Rule M14-6-1:
Definition: In a class template with a dependent base, any name that may be found in that dependent base shall be referred to using a qualified-id or this->

## Rule M15-0-3:
Definition: Control shall not be transferred into a try or catch block using a goto or a switch statement

## Rule M15-1-1:
Definition: The assignment-expression of a throw statement shall not itself cause an exception to be thrown (Since R2020b)

## Rule M15-1-2:
Definition: NULL shall not be thrown explicitly

## Rule M15-1-3:
Definition: An empty throw (throw;) shall only be used in the compound statement of a catch handler

## Rule M15-3-1:
Definition: Exceptions shall be raised only after startup and before termination

## Rule M15-3-3:
Definition: Handlers of a function-try-block implementation of a class constructor or destructor shall not reference non-static members from this class or its bases

## Rule M15-3-4:
Definition: Each exception explicitly thrown in the code shall have a handler of a compatible type in all call paths that could lead to that point (Since R2020b)

## Rule M15-3-6:
Definition: Where multiple handlers are provided in a single try-catch statement or function-try-block for a derived class and some or all of its bases, the handlers shall be ordered most-derived to base class

## Rule M15-3-7:
Definition: Where multiple handlers are provided in a single try-catch statement or function-try-block, any ellipsis (catch-all) handler shall occur last

## Rule M16-0-1:
Definition: #include directives in a file shall only be preceded by other preprocessor directives or comments

## Rule M16-0-2:
Definition: Macros shall only be #define'd or #undef'd in the global namespace

## Rule M16-0-5:
Definition: Arguments to a function-like macro shall not contain tokens that look like pre-processing directives

## Rule M16-0-6:
Definition: In the definition of a function-like macro, each instance of a parameter shall be enclosed in parentheses, unless it is used as the operand of # or ##

## Rule M16-0-7:
Definition: Undefined macro identifiers shall not be used in #if or #elif pre-processor directives, except as operands to the defined operator

## Rule M16-0-8:
Definition: If the # token appears as the first token on a line, then it shall be immediately followed by a preprocessing token

## Rule M16-1-1:
Definition: The defined pre-processor operator shall only be used in one of the two standard forms

## Rule M16-1-2:
Definition: All #else, #elif and #endif pre-processor directives shall reside in the same file as the #if or #ifdef directive to which they are related

## Rule M16-2-3:
Definition: Include guards shall be provided

## Rule M16-3-1:
Definition: There shall be at most one occurrence of the # or ## operators in a single macro definition

## Rule M16-3-2:
Definition: The # and ## operators should not be used

## Rule M17-0-2:
Definition: The names of standard library macros and objects shall not be reused

## Rule M17-0-3:
Definition: The names of standard library functions shall not be overridden

## Rule M17-0-5:
Definition: The setjmp macro and the longjmp function shall not be used

## Rule M18-0-3:
Definition: The library functions abort, exit, getenv and system from library <cstdlib> shall not be used

## Rule M18-0-4:
Definition: The time handling functions of library <ctime> shall not be used

## Rule M18-0-5:
Definition: The unbounded functions of library <cstring> shall not be used

## Rule M18-2-1:
Definition: The macro offsetof shall not be used

## Rule M18-7-1:
Definition: The signal handling facilities of <csignal> shall not be used

## Rule M19-3-1:
Definition: The error indicator errno shall not be used

## Rule M27-0-1:
Definition: The stream input/output library <cstdio> shall not be used