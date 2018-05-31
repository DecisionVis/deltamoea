# Packaging δMOEA

Have the `wheel` package installed, or this isn't going to work.

```
make
```

~~Upload from `dist` to Bitbucket using the web
interface.~~ We have switched to GitHub, which doesn't
host installers.

```
twine upload dist/deltamoea-x.y.tar.gz dist/deltamoea-x.y.py2.py3-none-any.whl
```

Where `x.y` is the current version number.
