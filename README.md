# Rescrypt
Rescrypt is a [Transcrypt](http://transcrypt.org/) implementation of the python re package.

Regular expression features in standard re __not__ supported in rescrypt:

  - Look-behinds
  - Conditionals
  - Backreferences to groups that did not participate in the match attempt fail to match  
    Example: `(a)?\1` matches `aa` but fails to match `b`

API's implemented:

  - Top level functions:
    - .compile()
  - Regular expression objects:
    - .search()
    - .match()
    - .split()
  - Match objects:
    Everything, except the optional argument to .start(), .end() and .span()