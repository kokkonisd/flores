Available keys
**************

Here is a complete list of keys that can be used in :ref:`templates <Templates>`,
:ref:`pages <Pages>`, :ref:`posts and drafts <Posts and drafts>` and
:ref:`user data pages <User Data Pages>`:

+--------------------------+---------------------------------+-------------------------+
| Key                      | Content                         | Availability            |
+==========================+=================================+=========================+
| ``site.config.*``        | The configuration of the site,  | Templates, pages,       |
|                          | containing all the keys defined | posts/drafts, user data |
|                          | in ``_data/config.json``. If    | pages                   |
|                          | the file is not defined, then   |                         |
|                          | the default config is used.     |                         |
+--------------------------+---------------------------------+-------------------------+
| ``site.data.*``          | The data defined in a           | Templates, pages,       |
|                          | :ref:`data file <Data>`,        | posts/drafts, user data |
|                          | indexed by the file's name      | pages                   |
|                          | (e.g. ``site.data.foo`` for the |                         |
|                          | file ``_data/foo.json``).       |                         |
+--------------------------+---------------------------------+-------------------------+
| ``site.pages``           | The complete list of pages that | Templates, pages,       |
|                          | are present on the site. See    | posts/drafts, user data |
|                          | :class:`flores.generator.Page`  |                         |
|                          | for more info.                  |                         |
+--------------------------+---------------------------------+-------------------------+
| ``site.posts``           | The complete list of posts that | Templates, pages,       |
|                          | are present on the site. See    | posts/drafts, user data |
|                          | :class:`flores.generator.Post`  | pages                   |
|                          | for more info.                  |                         |
+--------------------------+---------------------------------+-------------------------+
| ``site.blog.categories`` | The complete list of categories | Templates, pages,       |
|                          | collected from all blog posts   | posts/drafts, user data |
|                          | on the site.                    | pages                   |
+--------------------------+---------------------------------+-------------------------+
| ``site.blog.tags``       | The complete list of tags       | Templates, pages,       |
|                          | collected from all blog posts   | posts/drafts, user data |
|                          | on the site.                    | pages                   |
+--------------------------+---------------------------------+-------------------------+
| ``site.*``               | The :ref:`user data pages       | Templates, pages,       |
|                          | <User Data Pages>` that are     | posts/drafts, user data |
|                          | defined for the site. For       | pages                   |
|                          | example, user data pages stored |                         |
|                          | in the ``_recipes`` directory   |                         |
|                          | will be accessible via          |                         |
|                          | ``site.recipes``.               |                         |
+--------------------------+---------------------------------+-------------------------+
| ``page.*`` (for pages)   | All the attributes of the page  | Templates (when used by |
|                          | in the current context. See     | pages or user data      |
|                          | :class:`flores.generator.Page`  | pages), pages, user     |
|                          | for the full list.              | data pages              |
+--------------------------+---------------------------------+-------------------------+
| ``page.*`` (for          | All the attributes of the       | Templates (when used by |
| posts/drafts)            | post/draft in the current       | posts/drafts),          |
|                          | context. See                    | posts/drafts.           |
|                          | :class:`flores.generator.Post`  |                         |
|                          | for the full list.              |                         |
+--------------------------+---------------------------------+-------------------------+
