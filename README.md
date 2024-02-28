CMPUT404-project-socialdistribution
===================================

CMPUT404-project-socialdistribution

See [the web page](https://uofa-cmput404.github.io/general/project.html) for a description of the project.

Make a distributed social network!

Contributing
============

Sahir Momin -
Lei Xiao - 
Travis Lee -
Anh Dinh -
Jawad Chowdhury

Contributors / Licensing
========================

Generally everything is LICENSE'D under the Apache 2 license by Abram Hindle.

All text is licensed under the CC-BY-SA 4.0 http://creativecommons.org/licenses/by-sa/4.0/deed.en_US

Contributors:

    Karim Baaba
    Ali Sajedi
    Kyle Richelhoff
    Chris Pavlicek
    Derek Dowling
    Olexiy Berjanskii
    Erin Torbiak
    Abram Hindle
    Braedy Kuzma
    Nhan Nguyen 

Sources/References
==================



API Documentation
=================

Retrieve list of authors, optionally paginated (GET)
----------------------------------------------------

Request:

    GET ://service/api/authors/?page={int}&size={int}  HTTP/1.1
    
Sample Input Data:

N/A
    
Sample Output Data:

    {
    "type": "followers",      
    "items":[
        {
            "type":"author",
            "id":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
            "url":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
            "host":"http://127.0.0.1:5454/",
            "displayName":"Greg Johnson",
            "github": "http://github.com/gjohnson",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        },
        {
            "type":"author",
            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
            "host":"http://127.0.0.1:5454/",
            "displayName":"Lara Croft",
            "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
            "github": "http://github.com/laracroft",
            "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
        }
    ]
    }

Retrieve author with id (GET)
-----------------------------

Request:

    GET ://service/api/authors/{AUTHOR_ID} HTTP/1.1
    
Sample Input Data:

N/A

Sample Output Data:

    {
    "type":"author",
    // ID of the Author
    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    // the home host of the author
    "host":"http://127.0.0.1:5454/",
    // the display name of the author
    "displayName":"Lara Croft",
    // url to the authors profile
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    // HATEOS url for Github API
    "github": "http://github.com/laracroft",
    // Image from a public domain
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    }

Update author information (PUT)
-------------------------------

Request:

    PUT ://service/api/authors/{AUTHOR_ID} HTTP/1.1

Sample Input Data:

    {
    "type":"author",
    // ID of the Author
    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    // the home host of the author
    "host":"http://127.0.0.1:5454/",
    // the display name of the author
    "displayName":"Lara Croft",
    // url to the authors profile
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    // HATEOS url for Github API
    "github": "http://github.com/laracroft",
    // Image from a public domain
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    }

Sample Output Data:

