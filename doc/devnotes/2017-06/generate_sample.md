# Generating a Sample

Historically we've called these "solutions" and elsewhere I've 
called them "population members".  But neither exactly captures the 
idea.  I also like "sample" because it expresses what it is: a
sample from the decision space.  Another alternative might be 
"individual," which emphasizes that the size of the sample is one.
But it rather anthropomorphizes them.

At any rate, generating a sample involves selection and the 
application of variation operators.  Here's how I intend it to work:

1. Selection: use binary tournament selection to choose two parents.
2. Mating and mutation.
    a.  Stack up our SBX and PM operators and choose a variable that 
will get changed, and how.  Because we want there to be no chance 
that we just return one of the parents.
    b.  Choose from among the remaining variables with some 
sparsity of effects assumptions in place.
3. 
