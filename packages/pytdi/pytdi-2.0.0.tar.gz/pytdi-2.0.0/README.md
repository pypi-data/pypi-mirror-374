# PyTDI

PyTDI is a Python package that provides a toolset to perform symbolical and
numerical time-delay interferometry (TDI) calculations. It can be used to define
arbitrary linear combination of time-shifted signals (i.e., combinations),
symbolically handle these combinations, and numerically evaluate these
combinations against data.

PyTDI also provides ready-to-use standard TDI combinations for the LISA mission.

## Contributing

### Report an issue

We use the issue-tracking management system associated with the project provided
by Gitlab. If you want to report a bug or request a feature, open an issue at
<https://gitlab.in2p3.fr/LISA/LDPG/wg6_inrep/pytdi/-/issues>. You may also
thumb-up or comment on existing issues.

### Development environment

We use [uv](https://docs.astral.sh/uv) as a package and dependency manager.

To setup your development environment, first clone the repository.

```shell
git clone git@gitlab.in2p3.fr:LISA/LDPG/wg6_inrep/pytdi.git
cd pytdi
```

We recommend you install the pre-commit hooks with

```shell
uv run pre-commit install
```

You can then run commands with

```shell
uv run <YOUR-COMMAND>
```

To update your virtual environement with the PyTDI dependencies, use

```shell
uv sync
```

### Workflow

The project's development workflow is based on the issue-tracking system
provided by Gitlab, as well as peer-reviewed merge requests. This ensures
high-quality standards.

Issues are solved by creating branches and opening merge requests. Only the
assignee of the related issue and merge request can push commits on the branch.
Once all the changes have been pushed, the "draft" specifier on the merge
request is removed, and the merge request is assigned to a reviewer. They can
push new changes to the branch, or request changes to the original author by
re-assigning the merge request to them. When the merge request is accepted, the
branch is merged onto master, deleted, and the associated issue is closed.

### Pylint, mypy, black and pytest

We enforce [PEP 8 (Style Guide for Python
Code)](https://www.python.org/dev/peps/pep-0008/) with
[Pylint](http://pylint.pycqa.org/) syntax checking, and testing of the code via
unit and integration tests with the [pytest](https://docs.pytest.org/)
framework. We use [mypy](https://mypy.readthedocs.io) as static type checker,
and [Black](https://black.readthedocs.io) as the syntax formatter.

All in the continuous integration system and pre-commit hooks. Only if all tests
pass successfully a merge request can be merged.

VS Code tasks for each of these tools are avaialble. Open the command palette,
choose "Run task", and choose a task to run.

## How to cite

By releasing PyTDI as an open source software package we want to foster open
science and enable everyone to use it in their research free of charge. However,
please keep in mind that developing and maintaining such a tool takes time and
effort. Hence, we would appreciate to be associated with you research:

* Please cite the DOI (see badge above), and acknowledge the authors in any
  publication that uses PyTDI
* Do not hesitate to send an email for support and/or collaboration
