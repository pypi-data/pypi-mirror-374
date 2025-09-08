# LG Static Analysis Code Rules Guidelines (Impact: High)

## Rule ARRAY_VS_SINGLETON:
Definition: Do not treat a pointer to a single object as an array pointer. Always distinguish between pointer to one object and pointer to array of objects to avoid invalid memory access.

## Rule ATOMICITY:
Definition: Merge related critical sections into a single atomic block to prevent race conditions. Ensure the entire operation is protected, not just individual reads/writes.

## Rule BAD_ALLOC_ARITHMETIC:
Definition: When allocating memory, ensure correct arithmetic expressions. Use malloc(x+y) instead of malloc(x)+y to avoid under-allocation and memory corruption.

## Rule BAD_ALLOC_STRLEN:
Definition: Use strlen(p)+1 instead of strlen(p+1) when allocating memory for strings to include null terminator space.

## Rule BAD_FREE:
Definition: Only call free() on dynamically allocated pointers. Do not free stack variables, string literals, or already freed pointers.

## Rule BUFFER_SIZE:
Definition: When manipulating buffers, ensure the size argument does not exceed the buffer capacity. Always leave room for null terminator in string operations.

## Rule COM.ADDROF_LEAK:
Definition: Do not pass the address of CComBSTR or CComPtr internal pointers to functions that might overwrite them, causing memory leaks.

## Rule COM.BAD_FREE:
Definition: Use AddRef/Release methods for COM interface lifetime management. Do not explicitly free COM interface pointers.

## Rule MISMATCHED_ITERATOR:
Definition: Do not use iterators from one STL container with functions or comparisons from another container.

## Rule MISSING_COPY_OR_ASSIGN:
Definition: Classes that own resources must implement both copy constructor and assignment operator, or explicitly delete them to prevent shallow copying.

## Rule MISSING_RETURN:
Definition: Non-void functions must return a value on all code paths. Ensure every execution path has a return statement.

## Rule NEGATIVE_RETURNS:
Definition: Check function return values for negative values before using them as array indices, loop bounds, or size arguments.

## Rule NO_EFFECT:
Definition: Avoid statements or expressions that have no effect. Review code for typographical errors or incorrect operator precedence.

## Rule OVERLAPPING_COPY:
Definition: Do not copy data to overlapping memory locations using memcpy or similar functions. Use memmove for overlapping regions.

## Rule OVERRUN:
Definition: Do not access array or buffer elements beyond their bounds. Always validate indices before array access.

## Rule PATH_MANIPULATION:
Definition: Validate and sanitize file paths from external sources. Prevent directory traversal attacks by checking for "../" sequences.

## Rule PW.RETURN_PTR_TO_LOCAL_TEMP:
Definition: Do not return pointers to local variables or temporary objects. They become invalid when the function exits.

## Rule READLINK:
Definition: When using readlink(), manually add null terminator to the result buffer and check return value against buffer size.

## Rule RESOURCE_LEAK:
Definition: Release all acquired system resources (memory, files, mutexes, sockets) before function exit or program termination.

## Rule RETURN_LOCAL:
Definition: Do not return addresses of local stack variables. They become invalid when the function returns.

## Rule SIZECHECK:
Definition: Ensure allocated memory size matches the pointer's target type size. Avoid allocating smaller blocks than required.

## Rule SIZEOF_MISMATCH:
Definition: When using sizeof with pointers, ensure the sizeof expression matches the pointed-to memory size.

## Rule SQLI:
Definition: Do not construct SQL queries using untrusted user input. Use parameterized queries or proper input sanitization.

## Rule STRING_NULL:
Definition: Ensure strings are null-terminated before passing to string manipulation functions like strlen() or strcpy().

## Rule STRING_OVERFLOW:
Definition: When copying strings, ensure destination buffer is large enough. Use strncpy() instead of strcpy() for safer operations.

## Rule STRING_SIZE:
Definition: Check string lengths before copying into fixed-size buffers. Validate input size against buffer capacity.

## Rule UNINIT:
Definition: Initialize all variables before use. Do not use uninitialized stack variables or heap memory.

## Rule UNLOCKED_ACCESS:
Definition: Protect thread-shared data with proper locking mechanisms. Do not access shared variables without synchronization.

## Rule USE_AFTER_FREE:
Definition: Do not use memory or resources after they have been freed or closed. Set pointers to NULL after freeing.

## Rule USE_AFTER_MOVE:
Definition: Do not use objects after they have been moved unless they are reinitialized to a valid state.

## Rule VIRTUAL_DTOR:
Definition: Make destructors virtual in base classes that will be inherited and deleted through base class pointers.

## Rule WRAPPER_ESCAPE:
Definition: Do not let internal pointers from string wrapper classes escape the current function scope.

## Rule FORWARD_NULL:
Definition: Do not dereference pointers after checking them for null or assigning null to them.

## Rule NULL_RETURNS:
Definition: Check function return values for null before dereferencing. Handle null pointer returns appropriately.

## Rule REVERSE_INULL:
Definition: Check pointers for null before using them, not after. Avoid checking null after already dereferencing.

## Rule ORDER_REVERSAL:
Definition: Always acquire multiple locks in the same order across all code paths to prevent deadlocks.

## Rule LOCK:
Definition: Every acquired lock must be released. Ensure locks are released on all exit paths, including error conditions.

## Rule INFINITE_LOOP:
Definition: Ensure all loops and recursive functions have proper termination conditions that can be reached.

## Rule CHECKED_RETURN:
Definition: Check return values of functions that indicate success/failure, especially system calls and library functions.

## Rule INCOMPATIBLE_CAST:
Definition: Do not cast pointers to incompatible types. Ensure type compatibility when casting between pointer types.

## Rule INTEGER_OVERFLOW:
Definition: Check for integer overflow in arithmetic operations, especially when the result is used for memory allocation.

## Rule REVERSE_NEGATIVE:
Definition: Check integers for negative values before using them as array indices or in other contexts where negative values are invalid.

## Rule AUDIT.SPECULATIVE_EXECUTION_DATA_LEAK:
Definition: Avoid code patterns that could be exploited by speculative execution attacks like Spectre.

## Rule BAD_CHECK_OF_WAIT_COND:
Definition: Properly check wait conditions in loops when using thread synchronization primitives like condition variables.

## Rule MULTIPLE_INIT_SMART_PTRS:
Definition: Do not initialize multiple smart pointers with the same raw pointer to avoid double deletion.

## Rule OS_CMD_INJECTION:
Definition: Do not execute OS commands with user-controlled input. Sanitize and validate all external input before command execution.

## Rule SENSITIVE_DATA_LEAK:
Definition: Protect sensitive data with encryption. Do not log, transmit, or store sensitive information in plain text.

## Rule UNENCRYPTED_SENSITIVE_DATA:
Definition: Encrypt sensitive data (passwords, keys) during transmission and storage. Do not handle sensitive data in plain text.

## Rule WEAK_GUARD:
Definition: Do not rely on easily spoofed data (hostnames, IP addresses) for security decisions. Use proper authentication mechanisms.

## Rule WEAK_PASSWORD_HASH:
Definition: Use strong password hashing algorithms (bcrypt, scrypt, PBKDF2) with proper salting and iteration counts.

## Rule WRITE_CONST_FIELD:
Definition: Do not modify const-qualified fields in structures or classes.

## Rule Y2K38_SAFETY:
Definition: Use 64-bit time_t types to handle dates beyond 2038. Avoid storing time_t values in 32-bit integers.

## Rule LOCK_EVASION:
Definition: Do not check thread-shared data without holding the appropriate lock. Acquire locks before accessing shared variables.

## Rule INEFFICIENT_RESERVE:
Definition: Use resize() instead of reserve() in loops when adding elements to std::vector to avoid performance degradation.

## Rule BAD_SHIFT:
Definition: Ensure bit shift amounts are valid. Shift amount must be less than the type size and non-negative.

## Rule CONSTANT_EXPRESSION_RESULT:
Definition: Review expressions that always evaluate to the same value. Ensure the logic matches the intended behavior.

## Rule DC.STREAM_BUFFER:
Definition: Do not use unsafe I/O functions (scanf, fscanf, gets) that can cause buffer overflow.

## Rule DC.STRING_BUFFER:
Definition: Do not use unsafe string functions (sprintf, strcpy, strcat) that can cause buffer overflow.

## Rule DC.WEAK_CRYPTO:
Definition: Do not use weak pseudorandom number generators for cryptographic purposes. Use cryptographically secure random functions.

## Rule DIVIDE_BY_ZERO:
Definition: Check divisor values for zero before performing division or modulus operations.

## Rule FORMAT_STRING_INJECTION:
Definition: Do not use untrusted input in format strings. Use fixed format strings and pass user data as arguments.

## Rule OVERFLOW_BEFORE_WIDEN:
Definition: Cast operands to wider types before arithmetic operations to prevent overflow in intermediate calculations.

## Rule PRINTF_ARGS:
Definition: Ensure printf format strings match the number and types of arguments provided.

## Rule SIGN_EXTENSION:
Definition: Explicitly cast to unsigned types when needed to prevent unintended sign extension during type promotions.