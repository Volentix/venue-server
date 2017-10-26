from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from constance import config
import decimal

class ForumSite(models.Model):
    """ Forum site names and addresses """
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    scraper_name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name

class Signature(models.Model):
    """ Signature types per forum site """
    name = models.CharField(max_length=30)
    forum_site = models.ForeignKey(ForumSite, related_name='signature_types')
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """ Custom internal user profiles """
    user = models.ForeignKey(User)
    
    def __str__(self):
        return self.user.username
        
    def get_total_posts(self):
        total_per_forum = []
        for site in self.forum_profiles.all():
            latest_batch = site.uptime_batches.last()
            if latest_batch.active:
                total_per_forum.append(latest_batch.get_total_posts())
        return sum(total_per_forum)
        
    def get_total_posts_with_sig(self):
        total_per_forum = []
        for site in self.forum_profiles.all():
            latest_batch = site.uptime_batches.last()
            if latest_batch.active:
                total_per_forum.append(latest_batch.get_total_posts_with_sig())
        return sum(total_per_forum)
        
    def get_total_days(self):
        total_per_forum = []
        for site in self.forum_profiles.all():
            latest_batch = site.uptime_batches.last()
            if latest_batch.active:
                total_per_forum.append(latest_batch.get_total_days())
        return sum(total_per_forum)
        
    def get_total_points(self):
        total_per_forum = []
        for site in self.forum_profiles.all():
            for batch in site.uptime_batches.all():
                uptime_points = batch.get_total_points()
                total_per_forum.append(uptime_points)
        return sum(total_per_forum)
        
    def get_total_tokens(self):
        total_points = self.get_total_points()
        tokens = (total_points * config.VTX_AVAILABLE) / 10000
        return round(tokens, 2)

class ForumProfile(models.Model):
    """ Record of forum profile details per user """
    user_profile = models.ForeignKey(UserProfile, related_name='forum_profiles')
    forum = models.ForeignKey(ForumSite, null=True, blank=True, related_name='users')
    forum_user_id = models.CharField(max_length=50)
    signature = models.ForeignKey(Signature, null=True, blank=True, related_name='users')
    signature_code = models.CharField(max_length=40)
    active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return '%s @ %s' % (self.forum_user_id, self.forum.name)

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
        earliest_check = self.regular_checks.first()
        latest_check = self.regular_checks.last()
        earliest_total = earliest_check.total_posts
        latest_total = latest_check.total_posts
        return latest_total - earliest_total
        
    def get_total_days(self):
        earliest_check = self.regular_checks.first()
        latest_check = self.regular_checks.last()
        earliest_check_date = earliest_check.date_checked
        latest_check_date = latest_check.date_checked
        tdiff = latest_check_date - earliest_check_date
        days = tdiff.total_seconds() / 86400 # converts total seconds to days
        return round(days, 2)
        
    def get_total_points(self):
        latest_calc = self.points_calculations.last()
        return latest_calc.total_points
        
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
            else:
                if self.signature_found:
                    batch = UptimeBatch(forum_profile=self.forum_profile)
                    batch.save()
                    self.uptime_batch = batch
        super(SignatureCheck, self).save(*args, **kwargs)

class PointsCalculation(models.Model):
    """ Results of calculations of points for the given uptime batch.
    The calculations are cumulative,which means that the latest row  """
    uptime_batch = models.ForeignKey(UptimeBatch, related_name='points_calculations')
    date_calculated = models.DateTimeField(default=timezone.now)
    signature_check = models.ForeignKey(SignatureCheck, related_name='points_calculations')
    post_points = models.DecimalField(max_digits=10, decimal_places=2)
    post_days_points = models.DecimalField(max_digits=10, decimal_places=2)
    influence_points = models.DecimalField(max_digits=10, decimal_places=2)
    total_points = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if self._state.adding == True:
            sigcheck = self.signature_check
            batch = self.uptime_batch
            latest_gs = GlobalStats.objects.last()
            # Calculate points for posts with sig
            self.post_points = decimal.Decimal(batch.get_total_posts_with_sig() * 6000) 
            self.post_points /= latest_gs.total_posts_with_sig
            # Calculate post days points
            self.post_days_points = decimal.Decimal(batch.get_total_days() * 3800)
            self.post_days_points /= latest_gs.total_days
            # Calculate influence points
            self.influence_points = decimal.Decimal(batch.get_total_posts() * 200) 
            self.influence_points /= latest_gs.total_posts
            # Calculate total points
            self.total_points = decimal.Decimal(self.post_points)
            self.total_points += decimal.Decimal(self.post_days_points)
            self.total_points += decimal.Decimal(self.influence_points)
        super(PointsCalculation, self).save(*args, **kwargs)
        
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
    task_id = models.CharField(max_length=35)
    date_started = models.DateTimeField(default=timezone.now)
    success = models.NullBooleanField(null=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    scraping_errors = models.ManyToManyField(ScrapingError)
    
    def __str__(self):
        return str(self.id)