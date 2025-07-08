


def get_list_param(request, key):
    raw = request.query_params.getlist(key)
    values = []
    for r in raw:
        values.extend(r.split(','))
    return values
