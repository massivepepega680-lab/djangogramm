import io
import random
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from faker import Faker
from PIL import Image as PilImage
from posts.models import Image, Like, Post, Tag


User = get_user_model()

class Command(BaseCommand):
    help = "Fills the database with dummy users, posts, and likes for testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            help="Number of users to create."
        )
        parser.add_argument(
            "--posts",
            type=int,
            help="Number of posts to create."
        )

    def handle(self, *args, **options):
        """Handles db clean-up, creation of tags, users, posts and like.
        Handles adding images to posts. All by calling other functions
        """
        self.stdout.write("Starting data population...")
        num_users = options["users"]
        num_posts = options["posts"]
        self.clean_database()
        tags = self.create_tags()
        users = self.create_users(num_users)
        posts = self.create_posts(users, tags, num_posts)
        self.create_likes(users, posts)
        self.stdout.write(self.style.SUCCESS("Successfully populated the database!"))

    def clean_database(self):
        self.stdout.write("Clearing old data...")
        User.objects.filter(is_superuser=False).delete()
        Tag.objects.all().delete()
        Post.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Cleared old data."))

    def create_tags(self):
        self.stdout.write("Creating tags...")
        tag_names = [
            "travel",
            "food",
            "sunset",
            "nature",
            "tech",
            "art",
            "music",
            "fitness",
            "diy",
            "coffee",
            "books"
        ]
        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        self.stdout.write(self.style.SUCCESS(f"Created {len(tags)} tags."))
        return tags

    def create_users(self, num_users):
        self.stdout.write(f"Creating {num_users} users...")
        faker = Faker()
        users = []
        for i in range(num_users):
            profile = faker.profile()
            user = User.objects.create_user(
                username=profile["username"] + str(i),
                email=faker.email(),
                password="password123"
            )
            user.full_name = profile["name"]
            user.bio = faker.sentence(nb_words=15)
            user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"Created {len(users)} users."))
        return users

    def create_posts(self, users, tags, num_posts):
        self.stdout.write(f"Creating {num_posts} posts with images...")
        faker = Faker()
        posts = []
        for _ in range(num_posts):
            author = random.choice(users)
            post = Post.objects.create(
                author=author,
                caption=faker.paragraph(nb_sentences=3)
            )
            post.tags.set(random.sample(tags, k=random.randint(1, 4)))
            self.add_images_to_post(post, faker)
            posts.append(post)
        self.stdout.write(self.style.SUCCESS(f"Created {len(posts)} posts."))
        return posts

    def add_images_to_post(self, post, faker):
        num_images = random.randint(1, 3)
        for i in range(num_images):
            image_buffer = io.BytesIO()
            dummy_img = PilImage.new("RGB", (800, 600), color=faker.safe_color_name())
            dummy_img.save(image_buffer, format="JPEG")
            image_file = ContentFile(image_buffer.getvalue(), name=f"{faker.uuid4()}.jpg")
            Image.objects.create(post=post, image=image_file, order=i)

    def create_likes(self, users, posts):
        self.stdout.write("Creating likes...")
        like_count = 0
        for post in posts:
            num_likes = random.randint(0, len(users) // 2)
            likers = random.sample(users, k=num_likes)
            for user in likers:
                Like.objects.get_or_create(user=user, post=post)
                like_count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {like_count} likes."))