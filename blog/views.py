from django.shortcuts import render
# Create your views here.
from django.db.models import Count, Avg, Max
from django.shortcuts import render,HttpResponse,redirect
from django.contrib import auth
from blog.models import Article,UserInfo,Category,Tag,Blog,Comment,Category,Article2Tag,ArticleUpDown
# Create your views here.

def login(request):
    if request.method=='POST':
        user=request.POST.get('user')
        pwd=request.POST.get('pwd')
        user=auth.authenticate(username=user,password=pwd)
        # 去覆盖了Django里的User表内找对应用户是否存在
        if user:
            auth.login(request,user)
            # 如果存在写入session
            return redirect('/index/')
    return render(request,'login.html')


def index(request):
    article_list=Article.objects.all()
    print(request.user.username)
    return render(request,"index.html",{"article_list":article_list})


def logout(request):
    auth.logout(request)
    return redirect('/index/')


def homesite(request,username,**kwargs):
    """
    查询个人博客站点
    :param request:
    :return:
    """
    # 查询当前站点的用户对象
    user=UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request,'not_found.html')
    # 查询当前站点对象
    blog=user.blog

    # 查询当前用户发布的所有文章
    if not kwargs:  #如果是按照分类、标签和日期归档进行点击查看对应文章
        # ，则只需要把对应的文章记录从表里查询出来即可，也就是只需要把文章对象queryset对应改变传入模板内即可
        article_list=Article.objects.filter(user__username=username)
    else:
        select=kwargs.get('select')
        cont=kwargs.get('cont')
        if select=='category':
            article_list = Article.objects.filter(user__username=username).filter(category__title=cont)
        elif select=='tag':
            article_list=Article.objects.filter(user__username=username).filter(tags__title=cont)
        else:
            year, month = cont.split("/")
            article_list = Article.objects.filter(user__username=username).filter(create_time__year=year,
                                                                          create_time__month=month)
    #
    # # 查询当前站点每一个分类的名称以及对应的文章数
    # category_list = Category.objects.filter(blog=blog)
    #
    # # 查询当前站点每一个标签的名称以及对应的文章数
    # tag_list = Tag.objects.filter(blog=blog)
    #
    # date_list = Article.objects.filter(user=user).extra(select={"Y_m_date": "strftime('%%Y/%%m',create_time)"}).values(
    #     "Y_m_date").annotate(c=Count("title")).values_list("Y_m_date", "c")

    return render(request,'homesite.html',locals())



def article_detail(request,username,article_id):
    user=UserInfo.objects.filter(username=username).first()
    blog=user.blog
    article_obj=Article.objects.filter(pk=article_id).first()
    comment_list=Comment.objects.filter(article_id=article_id)
    return render(request,'article_detail.html',locals())



import json
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse

def Up_down(request):
    pro=json.loads(request.POST.get('pro'))
    title=request.POST.get('title')
    article = Article.objects.filter(title=title).first()
    user_id=request.user.pk
    response={'state':True}
    obj=ArticleUpDown.objects.filter(article__nid=article.pk,user_id=user_id).first()
    if  not obj:
        with transaction.atomic():
            ArticleUpDown.objects.create(user_id=user_id,article=article,is_up=pro)
            if pro:
                Article.objects.filter(pk=article.pk).update(up_count=F('up_count')+1)
            else:
                Article.objects.filter(pk=article.pk).update(down_count=F('down_count') + 1)
    else:
        response['state']=False
        response['handled']=obj.is_up
    return JsonResponse(response)


def comment(request):
    article_id=request.POST.get('article_id')
    content=request.POST.get('content')
    pid=request.POST.get('pid')
    with transaction.atomic():
        comment=Comment.objects.create(user_id=request.user.pk,article_id=article_id,content=content,parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F('comment_count')+1)
    response={"state":True}
    response['timer']=comment.create_time.strftime('%Y-%m-%d %X')
    response['content']=comment.content
    response['user']=request.user.username
    return JsonResponse(response)



def back(request):
    """
    后台管理视图
    :param request:
    :return:
    """
    user = request.user
    article_list = Article.objects.filter(user=user)
    return render(request, "backend/backend.html", locals())


def add_article(request):
    if request.method == "POST":

        title = request.POST.get("title")
        content = request.POST.get("content")
        user = request.user
        cate_pk = request.POST.get("cate")
        tags_pk_list = request.POST.getlist("tags")

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        # 文章过滤：
        for tag in soup.find_all():
            # print(tag.name)
            if tag.name in ["script", ]:
                tag.decompose()

        # 切片文章文本
        desc = soup.text[0:150]

        article_obj = Article.objects.create(title=title, content=str(soup), user=user, category_id=cate_pk, desc=desc)

        for tag_pk in tags_pk_list:
            Article2Tag.objects.create(article_id=article_obj.pk, tag_id=tag_pk)
        #文章和标签是多对多的关系，但是由于建表的时候用了through这个语法，所以第三张表的关系需要我们自己去加
        #不能够再用这个字段的方法，例如：add,set等方法。只能循环这个标签列表，循环创建第三张表中的记录。
        #批量添加表的记录，先将表对象放入列表中，再去用bulk_create(表对象列表)的方法去添加。
        return redirect("/backend/")


    else:

        blog = request.user.blog
        cate_list = Category.objects.filter(blog=blog)
        tags = Tag.objects.filter(blog=blog)
        return render(request, "backend/add_article.html", locals())


from LRblog import settings
import os


def upload(request):
    print(request.FILES)
    obj = request.FILES.get("upload_img")
    name = obj.name

    path = os.path.join(settings.BASE_DIR, "static", "upload", name)
    with open(path, "wb") as f:
        for line in obj:
            f.write(line)

    import json

    res = {
        "error": 0,
        "url": "/static/upload/" + name
    }

    return HttpResponse(json.dumps(res))



def modify(request):
    if request.method=='get':
        article_obj=Article.objects.filter(nid=request.GET.get('nid'))
        blog = request.user.blog
        cate_list = Category.objects.filter(blog=blog)
        tags = Tag.objects.filter(blog=blog)
        return render(request,'backend/add_article.html',locals())

    pass


def omit(request):
    pass