# Django Typst

A [Django] template engine that uses [Typst] to render Portable Document Format (PDF)
files.

## Installation and Configuration

The Django Typst engine is available from PyPI so you can install it with all the
usual tools:

```shell
pip install django_typst
# or
uv add django_typst
# or
poetry add django_typst
```

Once installed, to make the typst engine available, you need to add it to the
`TEMPLATES` configuration in your `settings.py`. e.g.:

```python
TEMPLATES = [
    ...
    {
        "BACKEND": "django_typst.TypstEngine",
        "NAME": "typst",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {
            "ROOT": None,
            "FONT_PATHS": [],
            "IGNORE_SYSTEM_FONTS": False,
            "PDF_STANDARD": "1.7",
            "PPI": None,
        }
    },
]
```

Note that this should be in _addition_ to the standard Django template engine that was
already there.

All the `OPTIONS` are... optional and the values above represent their defaults should
no alternative be provided.

| Option              | Description                                    | Default  |
| ------------------- | ---------------------------------------------- | -------- |
| ROOT                | The root path to use for relative paths        | `None`\* |
| FONT_PATHS          | Paths to look in for fonts                     | `[]`     |
| IGNORE_SYSTEM_FONTS | Only consider fonts in the defined font paths  | `False`  |
| PDF_STANDARD        | PDF revision to target (`1.7`, `a2-b`, `a3-b`) | `"1.7"`  |
| PPI                 | Pixel Per Inch for included PNG                | `None`   |

\* _The engine with use the folder the template is in as the root if one is not
specified._

## Usage

To use this engine with one of the standard Django class based views you only need to
set the `template_engine` class property to the value `"typst"`. You should also set the
`content_type` property to the value `"application/pdf"` to ensure the PDF is returned
with the correct content type. For example, in a simple `TemplateView` it would look
like this:

```python
from django.views import generic

class MyTemplateView(generic.TemplateView):
  template_engine = "typst"
  content_type = "application/pdf"

  ...
```

## Handling Context

Context data passed into the template it is first encoded in [TOML] format. Note this
means that only data types that can be serialized as TOML can be passed as context
variables. We use [tomlkit] to serialize the context. In practice this means the
following types can be included in the context:

- `str`
- `int`
- `float`
- `bool`
- `datetime.datetime`, `.time`, and `.date`
- `list`
- `dict`

In addition to these types, you can also include `decimal.Decimal`, `uuid.UUID` objects,
which are rendered to strings before serializing.

There is also special handling for the Django `HTTPRequest` object, which is converted
to a dict before serializing. The contents of that dict are:

```python
{
    "path": request.path,
    "path_info": request.path_info,
    "method": request.method,
    "content_type": request.content_type,
    "content_params": request.content_params,
    "headers": {},  # header-name: header-value
}
```

To then make use of context within a Typst template you must parse the incoming toml
data by adding the following to the top of the typst file:

```typst
#let ctx = toml(bytes(sys.inputs.context))
```

This will deserialize the context and assign it to the typst variable `ctx` which can
then be used in the template like any other variable. For example if you context was
something like:

```python
{
  "name": "J Moss",
  "flight": "QF1",
}
```

Then in your template you will be able to reference it with:

```typst
#ctx.name your flight number is #ctx.flight
```

Or even better is to parse the context as follows:

```typst
// Parse context or use defaults
#let ctx = if ("context" in sys.inputs) {
  toml(bytes(sys.inputs.context))
} else {
  (
    "name": "A Citizen",
    "flight": "DL31"
  )
}
```

This version sets a default if `context` is not passed in. This allows you to test the
template in isolation - say with the [Tinymist] Extension to VSCode or even just running
`typst` directly on it.

<!-- Links -->

[django]: https://www.djangoproject.com/
[tinymist]: https://github.com/Myriad-Dreamin/tinymist
[toml]: https://toml.io/en/
[tomlkit]: https://tomlkit.readthedocs.io/en/latest/
[typst]: https://typst.app/
