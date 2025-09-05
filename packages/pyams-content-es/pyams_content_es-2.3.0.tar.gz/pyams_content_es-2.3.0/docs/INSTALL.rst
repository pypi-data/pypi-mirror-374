===========================
Installing PyAMS_content_es
===========================

To use Elasticsearch with PyAMS_content, the first step is to install and configure an
Elasticsearch server. This step is not covered by this documentation, please see
Elasticsearch extensive documentation [https://elastic.co] to install a new server
(or a new cluster if you can) which will match your configuration.

The command lines provided below are those which can be used on a Debian GNU/Linux
distribution. If you use another system environment, you may have to change a few commands...


Installing Ingest pipeline
--------------------------

The *attachment* pipeline is required to index attachments contents; this pipeline relies on
an external plug-in, which have to be installed separately:

```
# /usr/share/elasticsearch/bin/elasticsearch-plugin install ingest-attachment
-> Installing ingest-attachment
-> Downloading ingest-attachment from elastic
[=================================================] 100%
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@     WARNING: plugin requires additional permissions     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
* java.lang.RuntimePermission accessClassInPackage.sun.java2d.cmm.kcms
* java.lang.RuntimePermission accessDeclaredMembers
* java.lang.RuntimePermission getClassLoader
* java.lang.reflect.ReflectPermission suppressAccessChecks
* java.security.SecurityPermission createAccessControlContext
See https://docs.oracle.com/javase/8/docs/technotes/guides/security/permissions.html
for descriptions of what these permissions allow and the associated risks.

Continue with installation? [y/N]y
-> Installed ingest-attachment
-> Please restart Elasticsearch to activate any plugins installed
```

Restart Elasticsearch and update ingest pipelines; this can be done using Kibana Dev Tools,
or with Curl; this command line assumes that your Elasticsearch is running on localhost on
port 9200; the target URL may be updated if you use HTTPS or if the server is on a remote
machine. `attachment.json` is provided in `docs` directory of *PyAMS_content_es* source
package:

```
# curl -XPUT http://localhost:9200/_ingest/pipeline/attachment -d @attachment.json
```


Creating index template
-----------------------

A file called `template.json` is provided in this directory; this template file is based
on a French site configuration, so you may have to adapt this configuration for your own 
language, or if you add custom extensions to default PyAMS configuration. Index patterns, 
number of replicas and number of shards can also be changed according to your environment.

To create a template called `pyams_index`, then just call:

```
# curl -XPUT http://localhost:9200/_index_template/pyams_index -d @template.json
```

Looking at your index templates with Kibana, you should find a new `pyams_index` template;
this one will be used as template for any new index matching given index patterns.


Pyramid configuration
---------------------

PyAMS provides a few configuration options which can be set in your Pyramid configuration file:

- `pyams_elastic.servers`: list of Elasticsearch servers; you can include protocol, username,
password and port, using RFC-1738 formatted URLs in the form `https://username:password@hostname:port`.
- `pyams_elastic.use_ssl`: boolean value used to specify if SSL must be used; default value
is *true*.
- `pyams_elastic.verify_certs`: you can set this option with a boolean value to specify
if SSL certificates should be verified or not.
- `pyams_elastic.ca_certs`: optional path to CA certificates.
- `pyams_elastic.client_cert`: optional path to PEM formatted SSL client certificate.
- `pyams_elastic.client_key`: optional path to PEM formatted SSL client key; this key can
also be part of the client certificate PEM file.
- `pyams_elastic.index`: name of the Elasticsearch index containing PyAMS documents.
- `pyams_elastic.timeout`: requests timeout, in seconds; default is *10*.
- `pyams_elastic.timeout_retries`: integer value used to specify the number of retries
on a request timeout; default is *0*.
- ```pyams_elastic.use_transaction```: boolean value used to specify if Elasticsearch client
should use transaction data manager; default is *true* and in this case, Elasticsearch requests 
are handled by a datamanager which executes requests only after a successful transaction commit;
otherwise, Elasticsearch requests are executed immediately.
- `pyams_elastic.disabled_indexing`: boolean value used to specify if index updates should be
disabled; default is *false*.

Please note that `pyams_elastic.` prefix to configuration options can be customized: you can
define several configurations in a single configuration file, using different prefixes, and set 
this prefix programmatically when calling `pyams_elastic.include.client_from_config` function.


Indexing content database
-------------------------

If you switch to Elasticsearch after creating your contents' database, you can reindex all your
database with the command line from your Pyramid environment:

```
# ./bin/pyams_es_index etc/production.ini
```

This command accepts arguments which can be used when you only want to reindex some parts of
your database. They are probably not required on a full index update.
