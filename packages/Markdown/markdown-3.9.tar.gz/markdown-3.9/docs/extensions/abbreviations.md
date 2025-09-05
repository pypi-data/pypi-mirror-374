title: Abbreviations Extension

Abbreviations
=============

Summary
-------

The Abbreviations extension adds the ability to define abbreviations.
Specifically, any defined abbreviation is wrapped in  an `<abbr>` tag.

The Abbreviations extension is included in the standard Markdown library.

Syntax
------

Abbreviations are defined using the syntax established in
[PHP Markdown Extra][php].

[php]: http://www.michelf.com/projects/php-markdown/extra/#abbr

Thus, the following text (taken from the above referenced PHP documentation):

```md
The HTML specification
is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]:  World Wide Web Consortium
```

will be rendered as:

```html
<p>The <abbr title="Hyper Text Markup Language">HTML</abbr> specification
is maintained by the <abbr title="World Wide Web Consortium">W3C</abbr>.</p>
```

The backslash (`\`) is not permitted in an abbreviation. Any abbreviation
definitions which include one or more backslashes between the square brackets
will not be recognized as an abbreviation definition.

Usage
-----

See [Extensions](index.md) for general extension usage. Use `abbr` as the name
of the extension.

The following options are provided to configure the output:

* **`glossary`**:
    A dictionary where the `key` is the abbreviation and the `value` is the definition.

A trivial example:

```python
markdown.markdown(some_text, extensions=['abbr'])
```

Disabling Abbreviations
-----------------------

When using the `glossary` option, there may be times when you need to turn off
a specific abbreviation. To do this, set the abbreviation to `''` or `""`.

```md
The HTML abbreviation is disabled on this page.

*[HTML]: ''
```