# Implementation Notes

This is going to be a non-adaptive multi-operator search.  Like I've
said, I'm skeptical about auto-adaption and "rotated" search
operators.  Instead I'm going to break things down and have SBX, a
low-DI (big steps) PM, and a high-DI (little steps, but high
probability) PM.  Actually, maybe the same thing with SBX, have two
SBX, one with big steps and low probability and one with little
steps and high probability.


## PM (inner)

I've modified the formula a bit. I really don't understand why
they've needlessly complicated it.  It makes me doubt that they knew
what they were doing.  Either that or it's kind of a watermark to
see whehter people have been copying their code.

Anyhow, my gamma is the same as (1-delta) in the formula, since
that's all they use.

Also my "beta" is the second term in braces, which is actually the
same in both versions and hides a subtraction.

And my "alpha" is η+1, again since that's all they use.

The "exponand" is everything in brackets.
