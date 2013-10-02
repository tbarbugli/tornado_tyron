Tornado Tyron
=============

A small app to push events.

You can use tyron to forward events to subscribed clients.

Subscribe to channels
====================
Clients subscribes to channel using the /\<channel\>/ tyron url entry point.

Publish to clients
==================
You can push events to clients via redis pubsub.
Tyron subscribes to *one* redis pubsub channel (see settings).

Message Format
==============
Messages published on redis must follow this json format:

`{"channel": "user_channel", "data": "...."}`

`channel` is used by tyron to route the message in `data` to clients
subscribed to it (that is, clients that are waiting on /\<user_channel\>/)

`data` is returned to clients as text/plain (so its up to your client to decide what to do with it)


Example:
========

tyron starts and listen for messages published on the channel tyron

client side: POST to /hiphop/

server side (cmd issued to redis): PUBLISH "tyron" "{\"data\": \"this is a message\", \"channel\": \"hiphop\"}"

tyron sends "this is a message" to clients subscribed to hiphop and closes the connection


Timeouts:
=========

Connections are not kept open forever, tyron times out connections after 600 seconds (thats configurable).


Install
=======

pip install tornado_tyron


Running Tyron
=============

tornado_tyron [OPTIONS]

  --pubsub_channel                 Redis pub/sub channel (default tyron_pubsub)
  --redis_db                       Redis host db (default 0)
  --redis_hostname                 Redis host address (default localhost)
  --redis_password                 Redis password (default 0)
  --redis_port                     Redis host port (default 6379)
  --timeout                        Timeout (default 600)
  --webserver_port                 Webserver port (default 8080)


File Descriptors
================

As the number of clients connected to tyron grows so the amount of the file descriptors in use (fd) does.
It is very possible that your current limit is very low by default (eg. 1024 for ubuntu).
When tyron runs out of fd you tyron will stop functioning correctly (and it will probably saturate one cpu core)
Make sure that you have the correct limit when you run tyron.


Running tyron via supervisord
-----------------------------

If you are planning to use supervisord to manage your tyron process keep in mind that you might need to adjust minfds (minimum amount of file descriptors)
in supervisord.conf to something higher than the default (1024) values (tyron will inherit that as fd limit)



