## How to test a DoH server using Curl
``curl --doh-insecure --doh-url https://one.one.one.one/dns-query http://www.example.com``

## Using dig
vdig +https @one.one.one.one example.com A example.com AAAA``
