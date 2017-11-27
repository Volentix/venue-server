from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.db import models
from constance import config
from hashids import Hashids
import decimal
import os

class ForumSite(models.Model):
    """ Forum site names and addresses """
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    scraper_name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name
        
class ForumUserRank(models.Model):
    """ Names of forum user ranks/positions """
    forum_site = models.ForeignKey(ForumSite, related_name='ranks')
    name = models.CharField(max_length=30)
    allowed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
        
def image_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "signature_%s.%s" % (instance.id, ext)
    return os.path.join('uploads', filename)
    
class Signature(models.Model):
    """ Signature types per forum site """
    name = models.CharField(max_length=30)
    forum_site = models.ForeignKey(ForumSite, related_name='signature_types')
    user_ranks = models.ManyToManyField(ForumUserRank, related_name='signatures')
    code = models.TextField()
    expected_links = models.TextField(blank=True)
    image = models.ImageField(upload_to=image_file_name, blank=True)
    active = models.BooleanField(default=True)
    date_added = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """ Custom internal user profiles """
    user = models.ForeignKey(User, related_name='profiles')
    email_confirmed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
        
    def get_total_posts_with_sig(self):
        total_per_forum = []
        for site in self.forum_profiles.filter(verified=True):
            for batch in site.uptime_batches.all():
                total_per_forum.append(batch.get_total_posts_with_sig())
        return sum(total_per_forum)
        
    def get_total_posts(self):
        value = 0
        if self.get_total_posts_with_sig():
            total_per_forum = []
            for site in self.forum_profiles.filter(verified=True):
                latest_batch = site.uptime_batches.last()
                if latest_batch:
                    total_per_forum.append(latest_batch.get_total_posts())
            value = sum(total_per_forum)
        return value
        
    def get_total_days(self):
        value = 0
        if self.get_total_posts_with_sig():
            total_per_forum = []
            for site in self.forum_profiles.filter(verified=True):
                for batch in site.uptime_batches.all():
                    total_per_forum.append(batch.get_total_days())
            value = sum(total_per_forum)
        return value
        
    def get_total_points(self):
        value = 0
        if self.get_total_posts_with_sig():
            total_per_forum = []
            for site in self.forum_profiles.filter(verified=True):
                for batch in site.uptime_batches.all():
                    uptime_points = batch.get_total_points()
                    total_per_forum.append(uptime_points)
            value = sum(total_per_forum)
        return value
        
    def get_total_tokens(self):
        total_points = self.get_total_points()
        tokens = (total_points * config.VTX_AVAILABLE) / 10000
        return round(tokens, 2)

class ForumProfile(models.Model):
    """ Record of forum profile details per user """
    user_profile = models.ForeignKey(UserProfile, related_name='forum_profiles')
    forum = models.ForeignKey(ForumSite, null=True, blank=True, related_name='users')
    forum_rank = models.ForeignKey(ForumUserRank, null=True, blank=True, related_name='users')
    forum_user_id = models.CharField(max_length=50, blank=True)
    profile_url = models.CharField(max_length=200)
    signature = models.ForeignKey(Signature, null=True, blank=True, related_name='users')
    verification_code = models.CharField(max_length=20, blank=True)
    active = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    date_verified = models.DateTimeField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return '%s @ %s' % (self.forum_user_id, self.forum.name)
        
    def save(self, *args, **kwargs):
        self.date_updated = timezone.now()
        super(ForumProfile, self).save(*args, **kwargs)
        if not self.verification_code:
            hashids = Hashids(min_length=8, salt=settings.SECRET_KEY)
            forum_profile_id, forum_user_id = self.id, self.forum_user_id
            verification_code = hashids.encode(forum_profile_id, int(forum_user_id))
            ForumProfile.objects.filter(id=self.id).update(verification_code=verification_code)
            
    class Meta:
        unique_together = ('forum', 'forum_user_id', 'verified')

class GlobalStats(models.Model):
    """ Records the sitewide or global stats """
    total_posts = models.IntegerField()
    total_posts_with_sig = models.IntegerField()
    total_days = models.DecimalField(max_digits=10, decimal_places=2)
    date_updated = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = 'Global stats'

class UptimeBatch(models.Model):
    """ Grouping of calculation results into periods of continuous uptime """
    forum_profile = models.ForeignKey(ForumProfile, related_name='uptime_batches')
    date_started = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    date_ended = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Uptime batches'
        
    def __str__(self):
        return str(self.id)
        
    def get_batch_number(self):
        batch_ids = self.forum_profile.uptime_batches.all().values_list('id', flat=True)
        return list(batch_ids).index(self.id) + 1
        
    def get_total_posts(self):
        latest_check = self.regular_checks.last()
        return latest_check.total_posts
        
    def get_total_posts_with_sig(self):
        value = 0
        if self.regular_checks.count() > 1:
            earliest_check = self.regular_checks.first()
            latest_check = self.regular_checks.last()
            earliest_total = earliest_check.total_posts
            latest_total = latest_check.total_posts
            value = latest_total - earliest_total
        return value
        
    def get_total_days(self):
        value = 0
        if self.regular_checks.count() > 1:
            earliest_check = self.regular_checks.first()
            latest_check = self.regular_checks.last()
            earliest_check_date = earliest_check.date_checked
            latest_check_date = latest_check.date_checked
            tdiff = latest_check_date - earliest_check_date
            days = tdiff.total_seconds() / 86400 # converts total seconds to days
            value = round(days, 2)
        return value
        
    def get_total_points(self):
        latest_calc = self.points_calculations.last()
        if latest_calc:
            return latest_calc.total_points
        else:
            return 0
        
    def get_first_check(self):
        return self.regular_checks.first()

class SignatureCheck(models.Model):
    """ Results of regular scraping from forum profile pages """
    forum_profile = models.ForeignKey(ForumProfile, related_name='regular_checks')
    uptime_batch = models.ForeignKey(UptimeBatch, related_name='regular_checks')
    date_checked = models.DateTimeField(default=timezone.now)
    total_posts = models.IntegerField(default=0)
    signature_found = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.id)
    
    def save(self, *args, **kwargs):
        proceed_save = False
        if self._state.adding == True:
            # Automatically assign to old or new uptime batch
            batches = self.forum_profile.uptime_batches.filter(active=True)
            if batches.count():
                latest_batch = batches.last()
                if self.signature_found:
                    self.uptime_batch = latest_batch
                else:
                    latest_batch.active = False
                    latest_batch.date_ended = timezone.now()
                    latest_batch.save()
                proceed_save = True
            else:
                if self.signature_found:
                    batch = UptimeBatch(forum_profile=self.forum_profile)
                    batch.save()
                    self.uptime_batch = batch
                    proceed_save = True
        else:
            proceed_save = True
        if proceed_save:
            super(SignatureCheck, self).save(*args, **kwargs)

class PointsCalculation(models.Model):
    """ Results of calculations of points for the given signature check in an uptime batch. """
    uptime_batch = models.ForeignKey(UptimeBatch, related_name='points_calculations')
    date_calculated = models.DateTimeField(default=timezone.now)
    signature_check = models.ForeignKey(SignatureCheck, related_name='points_calculations')
    post_points = models.DecimalField(max_digits=10, decimal_places=2)
    post_days_points = models.DecimalField(max_digits=10, decimal_places=2)
    influence_points = models.DecimalField(max_digits=10, decimal_places=2)
    total_points = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        #if self._state.adding == True:
        sigcheck = self.signature_check
        batch = self.uptime_batch
        latest_gs = GlobalStats.objects.last()
        # Calculate points for posts with sig
        self.post_points = 0
        if batch.get_total_posts_with_sig() and latest_gs.total_posts_with_sig:
            # Get the sum of the posts with sig for the current batch and for all the 
            # inactive batches in the batch's forum profile
            sum_posts_with_sig = batch.get_total_posts_with_sig()
            for batch in self.uptime_batch.forum_profile.uptime_batches.filter(active=False):
                sum_posts_with_sig += batch.get_total_posts_with_sig()
            # Now ready to compute the post points
            self.post_points = decimal.Decimal(sum_posts_with_sig * 6000) 
            self.post_points /= latest_gs.total_posts_with_sig
        # Calculate post days points
        self.post_days_points = 0
        if batch.get_total_posts() and batch.get_total_posts_with_sig() and latest_gs.total_days:
            if batch.get_total_days():
                # Get the sum of the total days for the current batch and for all the 
                # inactive batches in the batch's forum profile
                sum_total_days = batch.get_total_days()
                for batch in self.uptime_batch.forum_profile.uptime_batches.filter(active=False):
                    sum_total_days += batch.get_total_days()
                # Ready to calculate the post days points
                self.post_days_points = decimal.Decimal(sum_total_days * 3800)
                self.post_days_points /= latest_gs.total_days
        # Calculate influence points
        self.influence_points = 0
        if batch.get_total_posts() and batch.get_total_posts_with_sig() and latest_gs.total_posts:
            self.influence_points = decimal.Decimal(batch.get_total_posts() * 200) 
            self.influence_points /= latest_gs.total_posts
        # Calculate total points
        self.total_points = decimal.Decimal(self.post_points)
        self.total_points += decimal.Decimal(self.post_days_points)
        self.total_points += decimal.Decimal(self.influence_points)
        super(PointsCalculation, self).save(*args, **kwargs)
        
    def get_total_tokens(self):
        total_points = self.total_points
        tokens = (total_points * config.VTX_AVAILABLE) / 10000
        return round(tokens, 2)
        
class ScrapingError(models.Model):
    """ Record of scraping errors """
    forum = models.ForeignKey(ForumSite, related_name='scraping_errors')
    forum_profile = models.ForeignKey(ForumProfile, related_name='scraping_errors')
    error_type = models.CharField(max_length=30)
    traceback = models.TextField()
    resolved = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    date_resolved = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return str(self.id)
    
class DataUpdateTask(models.Model):
    """ Record details about the execution run of scraping and data update tasks """
    task_id = models.CharField(max_length=50)
    date_started = models.DateTimeField(default=timezone.now)
    success = models.NullBooleanField(null=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    scraping_errors = models.ManyToManyField(ScrapingError)
    
    def __str__(self):
        return str(self.id)