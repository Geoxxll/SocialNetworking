def construct_default_author_uri(obj, request, host):
    author_id = obj.id
    return f"{host}api/authors/{author_id}/"

