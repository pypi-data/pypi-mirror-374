========================
PyAMS content ES package
========================

.. contents::


What is PyAMS?
==============

PyAMS (Pyramid Application Management Suite) is a small suite of packages written for applications
and content management with the Pyramid framework.

**PyAMS** is actually mainly used to manage web sites through content management applications (CMS,
see PyAMS_content package), but many features are generic and can be used inside any kind of web
application.

All PyAMS documentation is available on `ReadTheDocs <https://pyams.readthedocs.io>`_; source code
is available on `Gitlab <https://gitlab.com/pyams>`_ and pushed to `Github
<https://github.com/py-ams>`_. Doctests are available in the *doctests* source folder.


What is PyAMS_content_ES?
=========================

*PyAMS_content* is the base of content management packages for PyAMS. It relies on its
internal catalog for all features requiring content searching.

If you can use an Elasticsearch index, the *PyAMS_content_es* package extends *PyAMS_content*
to provide a set of custom utilities and adapters which relies on Elasticsearch instead of
internal catalog to do content searches! It also allows using additional features, like
full text search, including attachments, using ES *ingest-attachment* plug-in.

All you have to do is to include *pyams_content_es* package **INSTEAD OF** default
*pyams_content* in your Pyramid application configuration file, and to set a few properties
to define Elasticsearch connexion and index settings.

Look at *INSTALL.rst* to get instructions about how to configure an Elasticsearch index for
PyAMS...
