![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/agpl-license-web-badge-version-2-256x48.png "AGPL")

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/hasii2011/code-ally-basic/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/hasii2011/code-ally-basic/tree/master)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![PyPI version](https://badge.fury.io/py/codeallybasic.svg)](https://badge.fury.io/py/codeallybasic)

This project hosts common artifacts for various projects I am developing.  This is package does not include any wxPython dependency.

___

Written by <a href="mailto:email@humberto.a.sanchez.ii@gmail.com?subject=Hello Humberto">Humberto A. Sanchez II</a>  (C) 2025

## Note
For all kind of problems, requests, enhancements, bug reports, etc., please drop me an e-mail.

## Developer Notes
This project uses [buildlackey](https://github.com/hasii2011/buildlackey) for day to day development builds.

Also notice that this project does not include a `requirements.txt` file.  All dependencies are listed in the `pyproject.toml` file.

#### Install the main project dependencies

```bash
pip install .
```

#### Install the test dependencies

```bash
pip install .[test]
```

#### Install the deploy dependencies

```bash
pip install .[deploy]
```

Normally, not needed because the project uses a GitHub workflow that automatically deploys releases

---
I am concerned about GitHub's Copilot project

![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/SillyGitHub.png)

I urge you to read about the [Give up GitHub](https://GiveUpGitHub.org) campaign from [the Software Freedom Conservancy](https://sfconservancy.org).

While I do not advocate for all the issues listed there I do not like that a company like Microsoft may profit from open source projects.

I continue to use GitHub because it offers the services I need for free.  But, I continue to monitor their terms of service.

Any use of this project's code by GitHub Copilot, past or present, is done without my permission.  I do not consent to GitHub's use of this project's code in Copilot.
