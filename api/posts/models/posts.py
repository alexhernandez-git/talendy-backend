from api.utils.models import CModel
from django.contrib.gis.db import models


class Post(CModel):
    portal = models.ForeignKey("portals.Portal", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    members = models.ManyToManyField("users.User", through="posts.PostMember", related_name="post_members")
    karma_winner = models.ForeignKey("posts.PostMember", on_delete=models.SET_NULL,
                                     related_name="karma_winner", null=True, blank=True)
    members_count = models.IntegerField(default=0)
    title = models.CharField(max_length=300)
    text = models.TextField(null=True, blank=True)
    solution = models.TextField(null=True, blank=True)
    draft_solution = models.TextField(null=True, blank=True)
    karma_offered = models.IntegerField(default=100)
    last_message = models.ForeignKey(
        "posts.PostMessage", on_delete=models.SET_NULL, null=True, related_name="post_last_message"
    )
    shared_notes = models.TextField(null=True, blank=True)
    drawing = models.FileField(verbose_name="Drawing File",
                               upload_to='posts/drawings/',
                               max_length=500, null=True, blank=True)
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

    files_size = models.IntegerField(default=0)


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
