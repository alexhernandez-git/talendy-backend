from api.utils.models import CModel
from django.db import models


class Post(CModel):

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    members = models.ManyToManyField("users.User", through="posts.PostMember", related_name="post_members")
    title = models.CharField(max_length=300)
    text = models.TextField(null=True, blank=True)
    karma_offered = models.IntegerField(default=0)

    ANYONE = 'AN'
    CONNECTIONS_ONLY = 'CO'
    PRIVACITY_TYPES = [
        (ANYONE, 'Anyone'),
        (CONNECTIONS_ONLY, 'Connections only'),
    ]

    privacity = models.CharField(
        max_length=2,
        choices=PRIVACITY_TYPES,
        default=ANYONE
    )

    community = models.ForeignKey("communities.Community", on_delete=models.SET_NULL, null=True, blank=True)

    ACTIVE = 'AC'
    SOLVED = 'SO'
    STATUS_TYPES = [
        (ACTIVE, 'Active'),
        (SOLVED, 'Solved'),
    ]

    status = models.CharField(
        max_length=2,
        choices=STATUS_TYPES,
        default=ACTIVE
    )


class PostImage(CModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(
        'posts images',
        upload_to='posts/images/',
        max_length=500
    )
    name = models.CharField(max_length=500)
    size = models.IntegerField()

    def save(self, **kwargs):

        try:
            this = PostImage.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)
        except:
            pass

        super(PostImage, self).save(**kwargs)
