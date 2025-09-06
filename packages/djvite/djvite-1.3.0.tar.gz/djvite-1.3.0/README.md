DjVite
======

![logo](./djvite.svg)

Integrates [Vite](https://vite.dev/) resources into a [Django](https://www.djangoproject.com/) web site.

Web requests are first served through **vite** dev server, then either proxified to **django** dev server or served directly.

This simulates a **nginx** proxy and **wsgi** server.

How to use
----------

- Add `djvite` to your `INSTALLED_APPS` django config.
- Define your static directories:
```python
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = ['dist']
```
- Load the `djvite` plugin into your templates:
```html
<html>{% load djvite %}
...
</html>
```
- Inject any *script* or *link* from *vite* into your template:
    - `{% vite hotreload %}` enables vite hot module reload in dev mode
    - `{% vite '/src/main.js' %}`
    - `{% vite '/src/style.css' %}`
- Add `DjVitePlugin` to your `vite.config.js` file:
```javascript
import { defineConfig } from 'vite'
import DjVitePlugin from 'djvite'
export default defineConfig({
  plugins: [DjVitePlugin({verbose: true})],
})
```

Notes:

You can add any attributes to the `vite` tag and it will be added to the final tags.

You can specifiy multiple sources within one `vite` tag, separate them with spaces.

You can use the `get_nginx_config` command to generate a working nginx static configuration.

Configuration
-------------

In **django** settings:
- `DJVITE` dict, with the following keys:
  - `DEV_MODE` (boolean, default `True`)
  When `False`, resources are resolved using the `vite-manifest.json` file that list bundle files. This file is generated using `vite build`.
  - `MODULE_EXTS` (extension list, default ot `['.js']`)
  Use this to provide other extensions to be served as module, for instance `['.js', '.ts', '.jsx', '.tsx']` in Typescript React application.
  - `VITE_MANIFEST_PATH` (`Path | str`, default to `vite.manifest.json`)
  Location to search for the Vite manifest. Used when `DEV_MODE` is `False`.

In **vite** config plugin:
- `options` object for `DjVitePlugin`.
    - `verbose` default to `false`.
    - `djangoPort` default to `DJANGO_PORT` environment variable or `8000` if not defined.
    - `djangoTemplatesGlob` default to the globbing pattern `**/templates`.
    - `manifestPath` default to `vite.manifest.json`.
