# About web resources look-up

The update routine of YAAM, when verifying if a new version of an addon is available, tries to optimize remote (web) metadata fetching by means of an HTTP HEAD requests instead of an HTTP GET.

## Ratio

As per the [HTTP standard](https://www.rfc-editor.org/rfc/rfc7231#section-4.3.2) the HEAD method is identical to the GET method but which body will be empty, therefore *should* faster than a GET requests due to avoiding downloading the content.

> The HEAD method is identical to GET except that the server MUST NOT return a message-body in the response. The metainformation contained in the HTTP headers in response to a HEAD request SHOULD be identical to the information sent in response to a GET request. This method can be used for obtaining metainformation about the entity implied by the request without transferring the entity-body itself. This method is often used for testing hypertext links for validity, accessibility, and recent modification.

## Bottleneck

Sometimes the perfomance gain might be minimal or butchered if the server [is too observant of the HTTP standards and doesn't optimize HEAD requests](https://www.rfc-editor.org/rfc/rfc7231#section-3.3)

> The server SHOULD send the same header fields in response to a HEAD request as it would have sent if the request had been a GET, except that the payload header fields (Section 3.3) MAY be omitted.

The may be omitted is the key to the bottleneck: if the remote resource is BIG, the payload metadata computation will be computationally expensive (content-length, I'm looking at you). To my understanding the isn't an standardized header field that let the server ignore payload metadata computation and therefore I presume it is left to the server implementation whether to optimize HEAD requests with or without payload header fields.
