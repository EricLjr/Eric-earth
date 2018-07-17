from django import template
from django.db.models import Count,Max
from blog.models import UserInfo,Article,Category,Comment,Tag

register=template.Library()

@register.inclusion_tag('simple.html')
def easy_query(username):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog
    # 查询当前站点每一个分类的名称以及对应的文章数
    category_list = Category.objects.filter(blog=blog)

    # 查询当前站点每一个标签的名称以及对应的文章数
    tag_list = Tag.objects.filter(blog=blog)

    date_list = Article.objects.filter(user=user).extra(select={"Y_m_date": "strftime('%%Y/%%m',create_time)"}).values(
        "Y_m_date").annotate(c=Count("title")).values_list("Y_m_date", "c")
    return {'blog':blog,'username':username,'category_list': category_list,'tag_list':tag_list,'date_list':date_list}
