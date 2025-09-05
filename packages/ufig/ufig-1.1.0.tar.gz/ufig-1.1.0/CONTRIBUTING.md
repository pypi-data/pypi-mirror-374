# Contributing to ufig

First off, thanks for taking the time to contribute! ❤️

All types of contributions are encouraged and valued. See the
[Table of Contents](#table-of-contents) for different ways to help and
details about how this project handles them. Please make sure to read
the relevant section before making your contribution. It will make it a
lot easier for us maintainers and smooth out the experience for all
involved. The community looks forward to your contributions. 🎉

> And if you like the project, but just don't have time to contribute,
> that's fine. There are other easy ways to support the project and show
> your appreciation, which we would also be very happy about:
> - Star the project
> - Tweet about it
> - Refer this project in your project's readme
> - Mention the project at local meetups and tell your friends/colleagues

<!-- omit in toc -->
## Table of Contents

- [I Have a Question](#i-have-a-question)
- [I Want To Contribute](#i-want-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## I Have a Question

> If you want to ask a question, we assume that you have read the
> available [Documentation](https://cosmo-docs.phys.ethz.ch/ufig/).

Before you ask a question, it is best to search for existing
[Issues](https://https://gitlab.com/cosmology-ethz/ufig/issues) that might
help you. In case you have found a suitable issue and still need
clarification, you can write your question in this issue. It is also
advisable to search the internet for answers first.

If you then still feel the need to ask a question and need
clarification, we recommend the following:

- Open an [Issue](https://gitlab.com/cosmology-ethz/ufig/issues/new).
- Provide as much context as you can about what you're running into.
- Provide project and platform versions (nodejs, npm, etc), depending on
  what seems relevant.

We will then take care of the issue as soon as possible.

## I Want To Contribute

### Testing

UFig uses pytest for automated testing with two test categories:

**Fast Tests**: The majority of tests that provide quick feedback and ensure code
coverage. Most tests are identical between fast and slow categories.

**Slow Tests**: Include all fast tests plus a few additional computationally intensive
tests that validate rendered images against reference simulations. These tests are not
run by default due to significantly longer execution times. This is particularly
important for code coverage analysis, where we must disable Numba JIT compilation so
that pytest-cov can accurately measure coverage. To ensure the slow test functionality
is still covered in our coverage reports, we created equivalent fast tests that execute
the same code paths with reduced precision. This approach ensures code coverage is
validated through fast tests while full functionality is verified when running slow
tests (with JIT compilation enabled).

To run tests locally, we recommend using uv to set up the development environment.
For Python 3.12:

```bash
# Set up virtual environment
uv venv --python 3.12

# Install dependencies including development packages
uv sync --dev
```

You can then run different types of checks:

```bash
# Style check
make style-check

# Fast tests only
make tests

# All tests (includes slow tests)
make tests ARGS=--runslow

# Coverage analysis (fast tests with Numba disabled)
make coverage
```

Alternatively, you can use `pytest` directly:

```bash
# Run fast tests
pytest tests/

# Run all tests including slow ones
pytest tests/ --runslow

# Run coverage analysis
NUMBA_DISABLE_JIT=1 pytest tests/ --cov=src/
```

After pushing a commit, the CI runs fast tests on multiple Python versions (3.9-3.12),
while slow tests, coverage analysis, and style checks run on a single Python version.

### Reporting Bugs

<!-- omit in toc -->
#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for
more information. Therefore, we ask you to investigate carefully,
collect information and describe the issue in detail in your report.
Please complete the following steps in advance to help us fix any
potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug and not an error on your side
  e.g. using incompatible environment components/versions (Make sure that
  you have read the
  [documentation](https://cosmo-docs.phys.ethz.ch/ufig/). If you are
  looking for support, you might want to check [this
  section](#i-have-a-question)).
- To see if other users have experienced (and potentially already
  solved) the same issue you are having, check if there is not already a
  bug report existing for your bug or error in the [bug
  tracker](https://gitlab.com/cosmology-ethz/ufig/issues?q=label%3Abug).
- Also make sure to search the internet (including Stack Overflow) to
  see if users outside of the Gitlab community have discussed the issue.
- Collect information about the bug:
  - Stack trace (Traceback)
  - OS, Platform and Version (Windows, Linux, macOS, x86, ARM)
  - Version of the interpreter, environment,
    package manager, depending on what seems relevant.
  - Possibly your input and the output
  - Can you reliably reproduce the issue? And can you also reproduce it
    with older versions?

<!-- omit in toc -->
#### How Do I Submit a Good Bug Report?

We use Gitlab issues to track bugs and errors. If you run into an issue
with the project:

- Open an
  [Issue](https://gitlab.com/cosmology-ethz/ufig/issues/new). (Since
  we can't be sure at this point whether it is a bug or not, we ask you
  not to talk about a bug yet and not to label the issue.)
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the
  *reproduction steps* that someone else can follow to recreate the issue
  on their own. This usually includes your code. For good bug reports you
  should isolate the problem and create a reduced test case.
- Provide the information you collected in the previous section.


### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for
pytest-regtest, **including completely new features and minor
improvements to existing functionality**. Following these guidelines
will help maintainers and the community to understand your suggestion
and find related suggestions.

<!-- omit in toc -->
#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the [documentation](https://cosmo-docs.phys.ethz.ch/ufig/) to see if the
  carefully and find out if the functionality is already covered, maybe by
  an individual configuration.
- Perform a
  [search](https://gitlab.com/cosmology-ethz/ufig/issues) to see if
  the enhancement has already been suggested. If it has, add a comment to
  the existing issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the
  project. It's up to you to make a strong case to convince the project's
  developers of the merits of this feature. Keep in mind that we want
  features that will be useful to the majority of our users and not just a
  small subset. If you're just targeting a minority of users, consider
  writing an add-on/plugin library.

<!-- omit in toc -->
#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as
[Gitlab issues](https://gitlab.com/cosmology-ethz/ufig/issues).

- Use a **clear and descriptive title** for the issue to identify the
  suggestion.
- Provide a **step-by-step description of the suggested enhancement** in
  as many details as possible.
- **Describe the current behavior** and **explain which behavior you
  expected to see instead** and why. At this point you can also tell which
  alternatives do not work for you.
- You may want to **include screenshots or screen recordings** which
- **Explain why this enhancement would be useful** to most
  pytest-regtest users. You may also want to point out the other projects
  that solved it better and which could serve as inspiration.


## Attribution
This guide is based on the **contributing-gen**.
[Make your own](https://github.com/bttger/contributing-gen)!
