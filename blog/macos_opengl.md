# MacOS and OpenGL

MacOS has a weird OpenGL situation.  PyQt seems to support profiles for OpenGL 2.0
(extremely obsolete) and OpenGL 4.1 (only sort-of obsolete) and nothing in between.
In particular, GLSL 1.3, which accompanied OpenGL 3.0, is the least common denominator
for Linux machines, since that's where software rendering tops out. 

Here's some example code that supposedly works on the Mac

https://github.com/openglsuperbible/sb6code/blob/master/src/gsculling/gsculling.cpp

It looks completely different, which make sense because we're looking at GLSL 4.1
versus GLSL 1.3.

I think we might need to write two rather different shaders, one for 1.3 and
the other for 4.1.  It's a bit of a duplication of effort, but I don't see
how else to do it.  When we load the 4.1 profile on MacOS, the #version 130
code won't compile.

Here's a [quote](http://gamedev.stackexchange.com/questions/33190/glsl-rewriting-geometry-shader-from-330-to-130-version?rq=1):

>  The proprietary Linux drivers support everything the Windows drivers do, with a few corner case exceptions. The FOSS drivers are only at GL 3.0, and then only if you compile in some patented features that are disabled by default. OSX might also be an issue - it supports GL 3.2, but only if you use Core Profile / forward compatibility when crating the GL context. If you don't, you might be limited to older versions of GL (not sure which off the top of my head). – Sean Middleditch Jul 29 '12 at 0:24 

It seems to indicate that we need to enable the forward compatibility profile.
But this also means that we can't use QPainter on MacOS, because QPainter uses
version 120 not 130.

Alternatively, I suck it up and downgrade to GLSL 120.

http://stackoverflow.com/questions/13039439/transforming-glsl-150-to-120
