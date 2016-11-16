# Rescrypt
Rescrypt is a [Transcrypt](http://transcrypt.org/) implementation of the python re package.

## Regular expression syntax
With two exceptions, any valid re regex _should_ behave correctly. The exceptions:

  - Lookbehinds (not supported at all)

  - Backreferences to optional capture groups.  
    In re, such a backreference will always fail if the group is not included in the match.  
    In rescrypt, the backreference will never fail in that scenario.  
    Example: `(a)?\1` matches both `aa` and `b` in rescrypt, but only `aa` in re.

## Implemented API

  - Top level functions:
    - .compile()
    - .search()
    - .match()
    - .split()
    - .findall()
  - Regular expression objects:
    - .search()
    - .match()
    - .split()
    - .findall()
  - Match objects:
    Everything, except the optional argument to .start(), .end() and .span()