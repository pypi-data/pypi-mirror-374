# TxHttpUtil
Synerty utility classes for serving a static site with twisted.web with user permissions.

Whats of interest?

* Protected resource with simple form login - Not suitable for public networks at this
stage
* A resource that underlays a multi level file system search under a standard twisted
Resource.putChild type resource tree.
* Twisted HTTP File Downloader
* Consistent request data, providing a Bytes IO like oboject and switching to a
NamedTemporaryFile if fileno, or name is called, or the data exceeds 5mb.
* Support for single page applications

# TODO

Unit tests for :
* Creating resource trees
* Getting resources from the resource tree
* Getting files from an underlay resource with two underlays
* Downloading files with the 
* Logging into the test site (Using Seleneium/Chrome WebDriver)
* Test uploading data under 5mb and over 5mb to and auto switching to NamedTemporaryFile
from BytesIO
