# Contributing

Keep the engine deterministic and explicit.

Changes that add learned inference, probabilistic ranking, external services, or
automatic truth claims should be proposed as a separate contract rather than
quietly changing the registry semantics.

Before opening a pull request:

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
```
