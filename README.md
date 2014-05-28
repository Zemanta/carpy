carpy
=====

Make your application swim like a fish in the water

Collect application metrics in real time with statsd and graphite


Roadmap
-------

**v0.0.1**

- Transaction and function timing module
- Manual function decorators and wrappers
- StatsD timing and error reporting
- Web UI proof of concept with timing charts, request rates, error rates
 
**v0.1**

- WSGI wrapper
- Some module wrappers (urllib, MySQL, pycassa, memcached, ...)
- Optional request logging (with python logging module)
- Usable web UI
- Open Source

**v0.2 (backend rewrite)**

- Cassandra backend for metrics
- Request logging to server
- Alering
- Web UI 2.0


Graphite data model
-------------------

    carpy -+
           +-> test_app -+
                         +-> my_server -+
                         |              +-> get_user -+
                         |                            +-> [ok]
                         |                            +-> [error]
                         |                            +-> [apdex]
                         |                            +-> children -+
                         |                                           +-> get_user_data -+
                         |                                                              +-> [ok]
                         |                                                              +-> [error]
                         |
                         +-> my_server2 +
                                        +-> get_user -+
                                        |             +-> [ok]
                                        |             +-> [error]
                                        |             +-> [apdex]
                                        |             +-> children -+
                                        |                           +-> get_user_data -+
                                        |                                              +-> [ok]
                                        |                                              +-> [error]
                                        +-> set_user -+
                                                      +-> [ok]
                                                      +-> [error]
                                                      +-> [apdex]
                                                      +-> children -+
                                                                    +-> set_user_data -+
                                                                                       +-> [ok]
                                                                                       +-> [error]

    [ok/error] -+
                +-> mean
                +-> median
                +-> upper
                +-> upper_95
                +-> lower
                +-> count
          
          
