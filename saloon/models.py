from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.category_name
    

class Service(models.Model):  
    name = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=800, null=True)
    cost = models.IntegerField(null=True)
    duration = models.IntegerField(default=60, help_text="Duration in minutes")
    image = models.FileField(upload_to="saloon_gallery")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services", null=True) 

    def __str__(self):
        return self.name

    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_review_count(self):
        return self.reviews.count()


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, related_name='service_reviews', null=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['service', 'user']  # One review per service per user
    
    def __str__(self):
        service_name = self.service.name if self.service else "General"
        return f"Review by {self.user.username} for {service_name}"


class ServiceReview(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['service', 'user']  # One review per service per user
    
    def __str__(self):
        return f"{self.user.username}'s review for {self.service.name}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.id} - {self.user.username} - {self.amount}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']


# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class Staff(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the User model
#     full_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     phone = models.CharField(max_length=15)
#     address = models.TextField()
#     job_title = models.CharField(max_length=50)  # e.g., 'Hair Stylist', 'Nail Technician'
#     hire_date = models.DateField()  # Date the staff member was hired
#     salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional field for salary
#     is_active = models.BooleanField(default=True)  # To track if the staff is currently active
#     profile_picture = models.ImageField(upload_to='staff_pics/', null=True, blank=True)  # Optional image for the staff profile
#     available_days = models.CharField(max_length=255, null=True, blank=True)  # Days available to work (e.g., "Mon, Tue, Fri")
#     available_times = models.CharField(max_length=255, null=True, blank=True)  # Working hours for the staff
#     services_offered = models.ManyToManyField('Service', related_name='staff_services', blank=True)  # Services offered by the staff

#     def __str__(self):
#         return self.full_name

#     def is_available(self):
#         return self.is_active  # You can customize this method to add more availability logic (like checking the days/times)


# class Staff(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     phone_no = models.CharField(max_length=12, unique=True)
#     address = models.CharField(max_length=255)
#     job_title = models.CharField(max_length=50)