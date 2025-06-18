'''
自定义分页组件
'''
from django.utils.safestring import mark_safe

class Pagination():
    def __init__(self, request, queryset, page_size=10, page_param="page", plus=2):
        page = request.GET.get(page_param, '1')
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        self.page = page
        self.page_size = page_size

        self.start = (page - 1) * page_size
        self.end = page * page_size

        self.page_queryset = queryset[self.start: self.end]

        total_count = queryset.count()

        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1
        self.total_page_count = total_page_count
        self.plus = plus


    def html(self):
        if self.total_page_count <= 2 * self.plus + 1:
            start_page = 1
            end_page = self.total_page_count
        else:
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus + 1
            else:
                if (self.page + self.plus) > self.total_page_count:
                    start_page = self.total_page_count - 2 * self.plus
                    end_page = self.total_page_count
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus
        page_str_list = []
        # 首页
        page_str_list.append('<li class="page-item"><a class="page-link" href="?page={}" aria-label="Previous">'
                             '首页</a></li>'.format(1))
        # 上一页
        if self.page > 1:
            prev = ('<li class="page-item"><a class="page-link" href="?page={}" aria-label="Previous">'
                    '<span aria-hidden="true">&laquo;</span></a></li>').format(self.page - 1)
        else:
            prev = ('<li class="page-item"><a class="page-link" href="?page={}" aria-label="Previous">'
                    '<span aria-hidden="true">&laquo;</span></a></li>').format(1)
        page_str_list.append(prev)
        # 页面
        for i in range(start_page, end_page + 1):
            if i == self.page:
                ele = '<li class="page-item active"><a class="page-link" href="?page={}">{}</a></li>'.format(i, i)
            else:
                ele = '<li class="page-item"><a class="page-link" href="?page={}">{}</a></li>'.format(i, i)
            page_str_list.append(ele)
        #下一页
        if self.page < self.total_page_count:
            prev = ('<li class="page-item"><a class="page-link" href="?page={}">'
                    '<span aria-hidden="true">&raquo;</span></a></li>').format(self.page + 1)
        else:
            if self.total_page_count == 0:
                prev = ('<li class="page-item"><a class="page-link" href="?page={}">'
                        '<span aria-hidden="true">&raquo;</span></a></li>').format(1)
            else:
                prev = ('<li class="page-item"><a class="page-link" href="?page={}">'
                        '<span aria-hidden="true">&raquo;</span></a></li>').format(self.total_page_count)
        page_str_list.append(prev)

        # 尾页
        if self.total_page_count == 0:
            prev = ('<li class="page-item"><a class="page-link" href="?page={}" aria-label="Next">'
                             '尾页</a></li>').format(1)
            page_str_list.append(prev)
        else:
            page_str_list.append('<li class="page-item"><a class="page-link" href="?page={}" aria-label="Next">'
                             '尾页</a></li>'.format(self.total_page_count))



        # 跳转
        # search_string = """
        #         <li class="page-item">
        #             <form style="float: left;margin-left: -1px" method="get">
        #                 <input name="page" style="position: relative;float: left;display: inline-block;width: 80px;border-radius: 10px"
        #                 type="text" class="form-control" placeholder="页码">
        #                 <button style="border-radius: 0" class="btn btn-default" type="submit">跳转</button>
        #             </form>
        #         </li>
        #     """
        # page_str_list.append(search_string)
        page_string = mark_safe("".join(page_str_list))
        return page_string