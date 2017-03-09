# UDMOEA.c

2017-03-09 16:55

The time has come.  UDMOEA in C.

I've been almost two weeks on the measurement side, now
it's time to jump back into the MOEA development.

Let's make a plan.

*   Parallel Development: I intend to work on trying out
    other problems and tuning the MOEA parameters in parallel
    with developing the C version.
*   Structures First: This means Headers first.  This will
    drive my thinking when it comes to the structure of
    helper code that has to initialize everything.
*   Follow a similar path: The initial version was
    bootstrapped with functions that didn't really do
    anything useful.  This really helped me get things
    going in a hurry.  It means I can start at the high
    level and work down.

## Specifics

1. Write some header files defining structs and constants.
2. Write the topdown template.
3. Write stubs so that it compiles.
4. Breadth-first, replace stubs with working code.
