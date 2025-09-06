===========
Change logs
===========

Version 0.0.4
=============

:date: 2025-07-29 (Asia/Tokyo)

Breaking changes
----------------

Features
--------

* Copy ``static_path`` assets.
  and add ``typst_static_path`` as configuration.
* Copy document assets (e.g. image files).
* Ignore comment nodes of docutils.
* Enable footnotes.

Fixes
-----

* Remove hash from ``image`` call wrapped by ``figure``.

Others
------

* Restructure element classes.
* Sort visitor/departure methods of translator.
* Experimental support Japanese document.
* Update workspace environment.

Version 0.0.3
=============

:date: 2025-07-26 (Asia/Tokyo)

Breaking changes
----------------

* Change key of ``typst_documents`` from ``'entry'`` to ``'entrypoint'``.
* Change template name of theme.

Features
--------

* Update structure of theme.
* Add theme 'basic' and split some features from 'manual'.
* Theme can pass assets (include any inherited themes)

Fixes
-----

Others
------

Version 0.0.2
=============

:date: 2025-07-23 (Asia/Tokyo)

Fixes
-----

* Controle version using import-metadata.

Others
------

* Restructure modules.

Version 0.0.1
=============

:date: 2025-07-21 (Asia/Tokyo)

First published release.

Features
--------

* Add builders.

Version 0.0.0
=============

:date: 2025-06-13 (Asia/Tokyo)

Initial commit.
