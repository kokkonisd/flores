User's Guide
************

This is a thorough guide to every feature of Flores. If this is your first time using
Flores, consider reading the :doc:`quickstart guide <quickstart>` first.


Templates
=========

Templates are found in the ``_templates`` directory. These are enriched HTML files that
are designed to do the "heavy lifting", while :ref:`pages <Pages>` and :ref:`posts
<Posts and drafts>` provide the content. They are also meant to be reusable.

In order to understand their syntax, it is best to take a look at the `official Jinja
documentation <https://jinja.palletsprojects.com/en/3.1.x/templates/>`_.

The name of the template file is what will be used to identify it in the Markdown files.
For example, a template file named ``foo.html`` will be referred to as ``foo`` in a
page file:

.. code-block:: text

   ---
   template: foo
   ---

   This is a page using the `foo` template.


Following standard `Jinja behavior
<https://jinja.palletsprojects.com/en/3.1.x/templates/#include>`_, templates can be
nested and included from other directories. For example, template file
``_templates/foo.html`` can include ``_templates/includes/bar.html`` via
``{% include "includes/bar.html" %}``.


Pages
=====

Pages are Markdown files with `Front Matter <https://jekyllrb.com/docs/front-matter/>`_.
They define the actual pages that will show up on the site, meaning that there is a
1-to-1 correspondance between a "source" file ``foo.md`` and a page ``foo.html``. They
are found in the ``_pages`` directory.

The Front Matter is surrounded by three dashes on either side, and is always found at
the start of the page file:

.. code-block:: text

   ---
   frontmatter goes here (YAML)
   ---
   content goes here (Markdown)


In the Front Matter of the page file, there is one mandatory YAML key that must always
be included: the ``template`` key, which denotes which template to use for the page.
This is simply the *name* of the template without the ``.html`` extension of the
template file; for example, if you wish to use the template file
``_templates/blog.html`` you would have the following page file:

.. code-block:: text

   ---
   template: blog
   ---
   This is the content of the page using the blog template.


However, outside of the mandatory ``template`` key, you can use other keys and make them
accessible to the page, either in the page file itself or in the template. We can, for
example, define header images as follows:

.. code-block:: text

   ---
   template: blog
   header_image: assets/images/foo.png
   ---
   This is the content of the page including a header image.


We could then use that ``header_image`` key in the ``blog.html`` template:

.. code-block:: html

   <!DOCTYPE html>
   <html>
       <body>
           <header>
               <img src="{{ page.header_image }}">
           </header>

           {{ page.content }}
       </body>
   </html>


We can even use the key inside of the page file itself:

.. code-block:: text

   ---
   template: blog
   header_image: assets/images/foo.png
   ---
   This is the content of the page including a header image.

   Here is the header image:

   ![header image]({{ page.header_image }})


As you can imagine, you can add any type of extra key you wish to make your pages and
templates more modular and reusable.


Permalinks
----------

Pages are created at the root of the site by default; if you wish for your page to be
created anywhere else on the site, you must specify a permalink. For example, if you
want your page ``categories.md`` to appear under ``/blog/categories`` instead of
``/categories``, you should do the following:

.. code-block:: text

   ---
   template: main
   permalink: "/blog/categories"
   ---
   This is the categories page.



Permalinks should **always** start with a slash (``/``), to explicitly denote that they
are absolute. Furthermore, there is no point in defining a permalink that's equal to
``"/"``, because that is the default behavior of pages without permalinks.

.. note::

   Permalinks are **not** allowed for :ref:`posts <Posts>`, :ref:`drafts <Drafts>` or
   :ref:`user data pages <User Data Pages>`. Those all have their own "namespace" on the
   site and should not be moved to unexpected places.


Posts and drafts
================

Posts
-----

Posts are found in the ``_posts`` directory. They represent blog posts, and will be
organized in the final site structure based on the date they were authored on. Every
post file is the same type of Markdown-Front Matter combination as the :ref:`pages
<Pages>` files.

The title of the post files, however, must follow a specific style: it must be written
in the format ``YYYY-MM-DD-<name>.md|markdown``. For example, we can have
``2022-01-09-foo.md``. This date is important, as it will be the assigned date for this
post.

There are *two* mandatory keys that must be present in a post's Front Matter: the
``template`` key (which, just like for the :ref:`pages <Pages>`, refers to the template
to be used for the post) and the ``title`` key. The ``title`` key defines the
human-readable title of the post, and as every other key it can be used in the templates
and in the post files themselves.

As for the :ref:`page files <Pages>`, you can define any number of arbitrary keys to use
in the Front Matter of the posts; however, there are some optional keys that have a
specific use and meaning. Here is a full list of those keys:

+------------+-----------+-----------------+---------------------------------+
| Key name   | Key type  | Handle          | Example                         |
+============+===========+=================+=================================+
| categories | list[str] | page.categories | categories: [art, css]          |
+------------+-----------+-----------------+---------------------------------+
| tags       | list[str] | page.tags       | tags: [hobby, outdoors]         |
+------------+-----------+-----------------+---------------------------------+
| time       | str       | page.time       | time: "12:13:15"                |
+------------+-----------+-----------------+---------------------------------+
| timezone   | str       | page.timezone   | timezone: "+0100"               |
+------------+-----------+-----------------+---------------------------------+

.. note::

    If you want all your posts to share a given timezone by default, you can provide
    one in the :ref:`config file <Configuration data>`. You can always override this
    value by specifying a different one in the post file itself.

Multiple keys are accessible for posts, regarding the date. Here is a list of their
handles and what they stand for, given the date ``2021-04-07 12:13:14 +0300``:

+--------------------------------+--------------+
| Handle                         | Value        |
+================================+==============+
| ``page.date.year``             | 2021         |
+--------------------------------+--------------+
| ``page.date.month``            | 4            |
+--------------------------------+--------------+
| ``page.date.month_padded``     | 04           |
+--------------------------------+--------------+
| ``page.date.month_name``       | April        |
+--------------------------------+--------------+
| ``page.date.month_name_short`` | Apr          |
+--------------------------------+--------------+
| ``page.data.day``              | 7            |
+--------------------------------+--------------+
| ``page.data.day_padded``       | 07           |
+--------------------------------+--------------+
| ``page.date.day_name``         | Wednesday    |
+--------------------------------+--------------+
| ``page.date.day_name_short``   | Wed          |
+--------------------------------+--------------+
| ``page.date.timestamp``        | 1617786794.0 |
+--------------------------------+--------------+

See :class:`flores.generator.PostDateInfo` for the full list of date attributes.

.. note::

    The key ``page.url`` is accessible for posts, and will give the full URL to the
    post. For example, the post ``_posts/2021-04-07-hello-world.md`` would be published
    under ``/2021/04/07/hello-world.html`` on the site. See the :doc:`list of available
    keys <available_keys>` for more info.


Drafts
------

Drafts are essentially the exact same thing as :ref:`posts <Posts>`, with the only
difference being that they are found in the ``_drafts`` directory. They are not
"published" in the final site by default (see the :ref:`building <Building the site>`
and :ref:`serving <Serving the site>` guides for how to enable drafts).

.. note::

    It is recommended to start writing a post in draft form in the ``_drafts``
    directory, and once that post is ready for publishing to then move it to the
    ``_posts`` directory.


Data
====

Data files are used to centralize some information that may be useful to access across
many different pages, templates, posts etc. The data files are written in JSON and they
are found in the ``_data`` directory.


Configuration data
------------------

While the name of the data files can be arbitrary, there is a special name reserved for
configuring the site itself: ``config.json``. This file can define the following keys
that alter the behavior of the website:

+--------------------+--------------------------------------------------------------+
| Key name           | Meaning                                                      |
+====================+==============================================================+
| ``pygments_style`` | The `Pygments style <https://pygments.org/styles/>`_ used to |
|                    | format code snippets on the site.                            |
+--------------------+--------------------------------------------------------------+
| ``timezone``       | The default timezone used in :ref:`posts <Posts>`.           |
+--------------------+--------------------------------------------------------------+
| ``images``         | The optimization applied to images; see the :ref:`assets     |
|                    | section <Images and other assets>`.                          |
+--------------------+--------------------------------------------------------------+

Of course, other optional keys can be defined in ``config.json`` and used throughout the
site. For example, it is recommended to define a title in this configuration file:

.. code-block:: json

   {
       "title": "My awesome site"
   }


Which you can then access, like any other key defined in ``config.json``, through the
``site.config`` handle: in this case, ``site.config.title``.


Other configuration files
-------------------------

Besides ``config.json``, you can define your own JSON data files to contain any type of
data. For example, here is ``companies.json``:

.. code-block:: json

   [
       {
           "title": "Foo & Co.",
           "position": "CTO",
           "year_range": "May 1981 - Sep 1989"
       },
       {
           "title": "Bar Ltd.",
           "position": "Software Engineer",
           "year_range": "Jun 2001 - Jul 2005"
       },
       {
           "title": "Baz Corp",
           "position": "Lead Software Architect",
           "year_range": "Apr 2029 - present"
       }
   ]


For data files that are **not** ``config.json``, you can access their contents through
the handle ``site.data``. For example, here you can access the list of companies through
``site.data.companies``, and access the specific year range of the second one via
``site.data.companies[1]["year_range"]``.

Using `Jinja template syntax <https://jinja.palletsprojects.com/en/3.1.x/templates/>`_,
you can iterate through all the companies and display them:

.. code-block:: html

    <ul>
        {% for company in site.data.companies %}
            <li>
                <h4> {{ company.title }} </h4>
                <h5> {{ company.position}} | {{ company.year_range }} </h5>
            </li>
        {% endfor %}
    </ul>


Images and other assets
=======================

General assets that are **not** :ref:`JavaScript files` or :ref:`stylesheets
<Stylesheets>` are expected to go in the ``_assets`` directory. This means that things
like images and other media, PDFs, text files etc. are all considered assets. Images
are treated separately and differently from other assets.


General assets
--------------

Non-image assets will be simply copied to the ``assets`` directory in the final site.
This means that if you have an asset file ``_assets/text/data/points.txt``, it will be
accessible on the site under ``/assets/text/data/points.txt``. All directory hierarchy
is preserved, and really the only thing that changes is the underscore in the name of
the assets directory.


Images
------

Images will be treated like any other asset by default and be copied exactly as they are
to the ``assets`` directory in the final site. However, that behavior can be altered
through the :ref:`config file <Configuration data>`: it is very common to apply basic
manipulations to images, such as optimizing them to reduce loading speeds, make images
of different sizes out of a root image to serve to different devices to optimize loading
speeds etc.

This configuration is handled through the config file, ``config.json``, and it is
specified under the ``images`` key. That key specifies a list that contains different
versions of images to output for each original image; if we only wish to optimize the
original images for example, we should only have one item in that list. Each list item
must specify three sub-keys:

+--------------+---------------------+----------------------+--------------------------+
| Key name     | Key type            | Example              | Meaning                  |
+==============+=====================+======================+==========================+
| ``size``     | ``float|int``       | ``size: 0.3``        | Generate an image whose  |
|              | in the range (0, 1] |                      | size is 30% of the       |
|              |                     |                      | original image.          |
+--------------+---------------------+----------------------+--------------------------+
| ``suffix``   | ``str``             | ``suffix: "-small"`` | Append "-small" to the   |
|              |                     |                      | name of the generated    |
|              |                     |                      | image; "foo.png"         |
|              |                     |                      | becomes "foo-small.png". |
+--------------+---------------------+----------------------+--------------------------+
| ``optimize`` | ``bool``            | ``optimize: true``   | Optimize the image by    |
|              |                     |                      | reducing its size        |
|              |                     |                      | without compromising     |
|              |                     |                      | quality.                 |
+--------------+---------------------+----------------------+--------------------------+

To give a concrete example, if we just want to apply basic optimization (compression) to
all images without producing extra variants, we would add this snippet to
``config.json``:

.. code-block:: json

   "images": [
       {
           "size": 1,
           "suffix": "",
           "optimize": true
       }
   ]


We could also generate three variants for each image, with medium and small variants
being respectively 60% and 30% of the original image size (for smaller screens):

.. code-block:: json

   "images": [
       {
           "size": 1,
           "suffix": "-large",
           "optimize": true
       },
       {
           "size": 0.6,
           "suffix": "-med",
           "optimize": true
       },
       {
           "size": 0.3,
           "suffix": "-small",
           "optimize": true
       }
   ]


For a given image ``foo.jpg``, this will generate three images: ``foo-large.jpg``,
``foo-med.jpg`` and ``foo-small.jpg``. These will be placed in the final ``assets``
directory of the site like the other assets, preserving any subdirectory structure.


JavaScript files
================

JavaScript files are expected to go in the ``_js`` directory, but they are treated like
normal, non-image :ref:`assets <General assets>`: they are simply copied over to the
site's ``js`` directory, preserving any subdirectory structure. For example,
``_js/site/main.js`` can be included in a template using:

.. code-block:: html

   <script src="js/site/main.js"></script>


Stylesheets
===========

Stylesheet files are expected to go in the ``_css`` directory. They are defined as any
file with the following extensions:

- ``.css``
- ``.scss``
- ``.sass``

If the files are pure, vanilla CSS, they will be copied directly to the final ``css``
directory of the site, just like :ref:`general assets <General assets>`.

However, if the files are SCSS or Sass, they will first be compiled to CSS automatically
and then they will be copied over to the final ``css`` directory of the site, as regular
CSS files.

To give an example, assume that we have a file ``_css/site/main.scss``:

.. code-block:: scss

    a {
        color: yellow;

        &:hover {
            color: red;
        }
    }


When the site is built, it will automatically be converted to ``css/site/main.css``:

.. code-block:: css

   a {
       color: yellow;
   }
   a:hover {
       color: red;
   }


As you can tell from the example, any subdirectory structure is preserved accross the
``_css`` and ``css`` directories.


User Data Pages
===============

Another feature of Flores that helps to augment the concent of pages are user data
pages. These are useful when you wish to group a few pages under a common category,
for example to present various projects, recipes, demos etc. on your site. Instead of
making separate :ref:`pages <Pages>` for these, you can use user data pages instead.

User data pages are found in a directory prefixed with an underscore; using the example
of hobby projects, we could create a directory called ``_projects/`` and store the
project pages there.

.. warning::

    You are free to use any name for the user data page directories, so long as it does
    not conflict with any of the :doc:`reserved directories <reserved_directories>`.
    If, for example, you store user data pages inside ``_css/``, they will **not** be
    treated as expected, as that directory is reserved for :ref:`stylesheets
    <Stylesheets>`.


Inside the ``_projects/`` directory, we can create :ref:`page files <Pages>` that
correspond to each project. For example, if we create the following two files:

- ``_projects/arcade_machine.md``
- ``_projects/3d_printer.md``

Two pages will be generated on the final site:

- ``/projects/arcade_machine.html``
- ``/projects/3d_printer.html``

The user data page files follow the exact same guidelines as the :ref:`regular page
files <Pages>`.


Building the site
=================

Building the site is done via the ``build`` subcommand:

.. code-block:: console

   $ flores build


This should be run by default in the project directory, i.e. the directory containing
all of the resources of the site. If you wish to run it from another directory, you can
manually specify which directory to build from:

.. code-block:: console

   $ flores build /path/to/directory/


If the build is successful, a ``_site`` directory will be created in the project
directory. This directory will contain the final site to be served.


Including drafts in build
-------------------------

A notable option of the ``build`` subcommand is the ``-d/--drafts`` option:

.. code-block:: console

   $ flores build -d


If used, this option will indicate to the generator to also include the drafts in the
final build. This can be useful when testing how a draft looks locally before
publishing.


Other build options
-------------------

You can explore the other options of the ``build`` subcommand by running:

.. code-block:: console

   $ flores build --help


Serving the site
================

.. warning::

   As mentioned in the docstring of the :class:`flores.server.Server` class, this is
   **NOT** meant to be used as a production server. It is meant to be used as a local
   preview/testing server that allows you to visualize the changes made to the site.

You can build and serve the site locally using the ``serve`` subcommand:

.. code-block:: console

   $ flores serve


Again, as for :ref:`building <Building the site>`, you can specify a project directory
(the current directory is used by default):

.. code-block:: console

   $ flores serve /path/to/directory/


Making the local site accessible to your network
------------------------------------------------

If you want to test how the site looks on other devices (assuming those devices are on
the same network as the device serving the site), you can bind the server to the host
device's local IP address:

.. code-block:: console

   $ flores serve -a <local_ip_address>


You can then visit the site from other devices on the network by visiting that address.


Including drafts in serve
-------------------------

As with :ref:`building <Including drafts in build>`, you can choose to include drafts
in the locally served site:

.. code-block:: console

   $ flores serve -d


Auto-rebuild
------------

When used to preview local changes, it is often useful to have the server refresh the
build every time a change is made to an asset, without having to re-launch the ``build``
or ``serve`` subcommands. This can be achieved through the ``-r/--auto-rebuild`` option:

.. code-block:: console

   $ flores serve -r


However, if a lot of images are treated during the build (see :ref:`image optimization
<Images>`) this might make the refresh rate drop a lot. To avoid this, you can supply
the ``-I/--disable-image-rebuild`` option, which avoids rebuilding images:

.. code-block:: console

   $ flores serve -r -I


The tradeoff here is a faster refresh rate for non-optimized images.


Other serve options
-------------------

You can explore the other options of the ``serve`` subcommand by running:

.. code-block:: console

   $ flores serve --help
