from rest_framework.pagination import (
    LimitOffsetPagination,
    remove_query_param,
    replace_query_param
)


class Pagination(LimitOffsetPagination):
    default_limit = 10

    def get_next_link(self):
        if self.offset + self.limit >= self.count:
            return None

        return replace_query_param(
            '?' + self.request.META['QUERY_STRING'],
            self.offset_query_param,
            self.offset + self.limit
        )

    def get_previous_link(self):
        if self.offset <= 0:
            return None

        url = '?' + self.request.META['QUERY_STRING']

        if self.offset - self.limit <= 0:
            return remove_query_param(url, self.offset_query_param)

        return replace_query_param(url, self.offset_query_param, self.offset - self.limit)
