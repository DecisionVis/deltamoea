# Computing Metrics

2017-02-26 20:14

Hypervolume.  That means I should pull down my hyppy repo.
If I recall correctly, I was working on a pretty solid
Python wrapper for it when I ran out of time to work on it.

2017-02-26 21:09

So I dusted off the hyppy repo.  It appears to be pretty
sound.  I'm going to want to check the results before use.
Fortunately the WFG website has copious test sets.  I hope
they still have them...

2017-02-26 21:23

Ah yes, yes they do.  And they've revised the wfg
algorithm.  Twice.

I'd rather that than have the resources disappear from the
internet, but this does throw a bit of a wrench in the
works.  My shiny frontend to WFG isn't going to work with
the changes they've made.  And I imagine they didn't focus
on fixing memory leaks and enabling continuous runs like
I did.

Probably the best option here is to take their new code,
run it against some sample data sets, and check that the
outcome is the same as with my old code.  Then use the old
code.

Or, I take their new code, leaky or not, on the assumption
that it's likely either faster or more correct, and
probably both.

Going back to the first hand, no, I want to use
metricsystem.py.  I shudder at how much less userfriendly
the C version is.  In the long run, it would be a service
to everybody involved if I got the Python code running with
an up-to-date verison of the C code.  It even takes "-" as
a filename argument!  Of course I could import it and not
even use the cli.
