# Python Semantic Release Demo

Project showcasing a possible setup to utilize [python-semamtic-release][psr] (PSR) with [uv][uv] and [ruff][ruff].

To build this has cost me more time than anticipated. Before I started with this demo,
I already had a profound understanding of the semantic version [specification][semver], of [conventional commits][conv],
and some experience with CI/CD ppelines.
From there it took me 30 hours to read through PSR's documentation, understand their uv project setup guide and to create this pipeline.

This pipeline is not quite what I would want to use everywhere, but it will do for simple projects.
Now it is time to create an app which would create this pipeline in a freshly initiated project.
I shall call it [ci-starter][ci-starter]. Hopefully, the pipelines produced by the ci-starter will evolve into something more sophisticated.

[psr]: https://python-semantic-release.readthedocs.io/en/latest/index.html
[uv]: https://docs.astral.sh/uv
[ruff]: https://docs.astral.sh/ruff
[semver]: https://semver.org
[ci-starter]: https://github.com/fleetingbytes/ci-starter
