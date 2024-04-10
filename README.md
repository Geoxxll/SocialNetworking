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
https://github.com/legionscript/socialnetwork

https://www.youtube.com/watch?v=NyWY2OktDAs&ab_channel=SsaliJonathan

https://www.django-rest-framework.org/

https://docs.djangoproject.com/en/5.0/

API Documentation
=================

Retrieve list of authors, optionally paginated [GET]
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

Retrieve author with id [GET]
-----------------------------

Request:

    GET ://service/api/authors/{AUTHOR_ID} HTTP/1.1
    
Sample Input Data:

N/A

Sample Output Data:

    {
    "type":"author",
    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "host":"http://127.0.0.1:5454/",
    "displayName":"Lara Croft",
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "github": "http://github.com/laracroft",
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    }

Update author information [PUT]
-------------------------------

Request:

    PUT ://service/api/authors/{AUTHOR_ID} HTTP/1.1

Sample Input Data:

    {
    "type":"author",
    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "host":"http://127.0.0.1:5454/",
    "displayName":"Lara Croft",
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "github": "http://github.com/laracroft",
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    }

Sample Output Data:

    {
    "type":"author",
    "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "host":"http://127.0.0.1:5454/",
    "displayName":"Lara Croft",
    "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
    "github": "http://github.com/laracroft",
    "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
    }

Retrieve list of authors following author_id [GET]
------------------------------------------------------------------------

Request:

    GET ://service/authors/{AUTHOR_ID}/followers HTTP/1.1

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

Retrieve post at post_id [GET]
------------------------------

Request:

    GET ://service/authors/{AUTHOR_ID}/posts/{POST_ID} HTTP/1.1

Sample Input Data:

N/A

Sample Output Data:

    {
            "type":"post",
            "title":"A Friendly post 2",
            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/999999983dda1e11db47671c4a3bbd9e"
            "source":"http://lastplaceigotthisfrom.com/authors/xxxxxx/posts/yyyyy",
            "origin":"http://whereitcamefrom.com/authors/yyyyyy/posts/zzzzz",
            "description":"This post discusses nothing -- brief",
            "contentType":"text/plain",
            "content":"Much shorter post",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Lara Croft",
                "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "github": "http://github.com/laracroft",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/999999983dda1e11db47671c4a3bbd9e/comments"
            "published":"2015-03-09T13:07:04+00:00",
            "visibility":"FRIENDS"
    }

Update/edit post content [PUT]
------------------------------

Request:

    PUT ://service/authors/{AUTHOR_ID}/posts/{POST_ID} HTTP/1.1

Sample Input Data:

    {
            "type":"post",
            "title":"A Friendly post 2",
            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/999999983dda1e11db47671c4a3bbd9e"
            "source":"http://lastplaceigotthisfrom.com/authors/xxxxxx/posts/yyyyy",
            "origin":"http://whereitcamefrom.com/authors/yyyyyy/posts/zzzzz",
            "description":"This post discusses nothing -- brief",
            "contentType":"text/plain",
            "content":"Much shorter post",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Lara Croft",
                "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "github": "http://github.com/laracroft",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/999999983dda1e11db47671c4a3bbd9e/comments"
            "published":"2015-03-09T13:07:04+00:00",
            "visibility":"FRIENDS"
    }

Sample Output Data:

    {
            "type":"post",
            "title":"A Friendly post 2",
            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/999999983dda1e11db47671c4a3bbd9e"
            "source":"http://lastplaceigotthisfrom.com/authors/xxxxxx/posts/yyyyy",
            "origin":"http://whereitcamefrom.com/authors/yyyyyy/posts/zzzzz",
            "description":"This post discusses nothing -- brief",
            "contentType":"text/plain",
            "content":"Much shorter post",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Lara Croft",
                "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "github": "http://github.com/laracroft",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/999999983dda1e11db47671c4a3bbd9e/comments"
            "published":"2015-03-09T13:07:04+00:00",
            "visibility":"FRIENDS"
    }

Delete post at post_id [DELETE]
-------------------------------

Request:

    DELETE ://service/authors/{AUTHOR_ID}/posts/{POST_ID} HTTP/1.1

Sample Input Data:

N/A

Sample Output Data:

N/A
    
Retrieve list of posts by author_id, optionally paginated [GET]
---------------------------------------------------------------

Request:

    GET ://service/authors/{AUTHOR_ID}/posts HTTP/1.1

Sample Input Data:

N/A

Sample Output Data:

    {
        "type": "posts"
        "items":[
            {
            "type":"post",
            "title":"A Friendly post title about a post about web dev",
            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e"
            "source":"http://lastplaceigotthisfrom.com/authors/xxxxxx/posts/yyyyy",
            "origin":"http://whereitcamefrom.com/authors/yyyyyy/posts/zzzzz",
            "description":"This post discusses stuff -- brief",
            "contentType":"text/plain",
            "content":"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Lara Croft",
                "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "github": "http://github.com/laracroft",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments"
            "published":"2015-03-09T13:07:04+00:00",
            "visibility":"FRIENDS"
        },
        {
            "type":"post",
            "title":"A Friendly post 2",
            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/999999983dda1e11db47671c4a3bbd9e"
            "source":"http://lastplaceigotthisfrom.com/authors/xxxxxx/posts/yyyyy",
            "origin":"http://whereitcamefrom.com/authors/yyyyyy/posts/zzzzz",
            "description":"This post discusses nothing -- brief",
            "contentType":"text/plain",
            "content":"Much shorter post",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Lara Croft",
                "url":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e",
                "github": "http://github.com/laracroft",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "comments":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/999999983dda1e11db47671c4a3bbd9e/comments"
            "published":"2015-03-09T13:07:04+00:00",
            "visibility":"FRIENDS"
        }
    ]
    }

Retrieve list of comments from post_id, optionally paginated [GET]
------------------------------------------------------------------

Request:

    ://service/authors/{AUTHOR_ID}/posts/{POST_ID}/comments

Sample Input Data:

N/A

Sample Output Data:

    {
        "type": "comment"
        "items":[
            {
            "type":"comment",
            "author":{
                "type":"author",
                "id":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                "url":"http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Greg Johnson",
                "github": "http://github.com/gjohnson",
                "profileImage": "https://i.imgur.com/k7XVwpB.jpeg"
            },
            "comment":"Sick Olde English",
            "contentType":"text/markdown",
            "published":"2015-03-09T13:07:04+00:00",
            "id":"http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c",
            }
        ]
    }


AJAX Documentation 
------------------
Like: 
	AJAX is used to asynchronously like/unlike post by incrementing/decrementing the like count. This helps to update the count without reloading the page.

Fetch New Posts:
	AJAX is used to check if there is any new posts made in last 5 seconds. Posts are filtered and an html file is rendered which is injected to add the latest posts.

Update Follow buttons:
	Ajax is used to update the Follow/Cancel Request and unfollow button, based on if the user is friends or have sent a friend request. The buttons are changed dynamically to update the button.

Send friend request:
	We use ajax to create follow object to send friend requests and send it to that user’s inbox
Accepting friend request:
	When clicking on the accept request button, ajax is used to delete the follow object and create a follower object to show which user follows and the other user 


