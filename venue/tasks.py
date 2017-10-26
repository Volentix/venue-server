from __future__ import absolute_import, unicode_literals
from .models import UserProfile, UptimeBatch, GlobalStats, SignatureCheck, PointsCalculation, DataUpdateTask, ScrapingError, ForumProfile
from django.utils import timezone
from celery import shared_task
from celery import chain
import traceback

def load_scraper(name):
    name = name.strip('.py')
    scraper = __import__('venue.scrapers.' + name, fromlist=[name])
    return scraper
    
@shared_task
def scrape_forum_profile(forum_profile_id, master_task_id):
    forum_profile = ForumProfile.objects.get(id=forum_profile_id)
    try:
        scraper = load_scraper(forum_profile.forum.scraper_name)
        total_posts, signature_found = scraper.execute(
            forum_profile.forum_user_id, forum_profile.signature_code)
        sigcheck = SignatureCheck(
            forum_profile=forum_profile,
            total_posts=total_posts,
            signature_found=signature_found
        )
        sigcheck.save()
    except Exception as exc:
        if master_task_id:
            data_update = DataUpdateTask(task_id=master_task_id)
            scrape_error = ScrapingError(
                error_type=type(exc).__name__,
                forum=forum_profile.forum, 
                forum_profile=forum_profile,
                traceback=traceback.format_exc()
            )
            scrape_error.save()
            data_update.scraping_errors.add(scrape_error)
        
@shared_task
def update_global_stats(master_task_id):
    users = UserProfile.objects.all()
    total_posts = 0
    total_posts_with_sig = 0
    total_days = 0
    for user in users:
        total_posts += user.get_total_posts()
        total_posts_with_sig += user.get_total_posts_with_sig()
        total_days += user.get_total_days()
    gstats = GlobalStats(
        total_posts=total_posts,
        total_posts_with_sig=total_posts_with_sig,
        total_days=total_days
    )
    gstats.save()
    
@shared_task
def calculate_points(master_task_id):
    batches = UptimeBatch.objects.filter(active=True)
    for batch in batches:
        for check in batch.regular_checks.all():
            calc = PointsCalculation(
                uptime_batch=batch,
                signature_check=check
            )
            calc.save()
            
@shared_task
def mark_master_task_complete(master_task_id):
    master_task = DataUpdateTask.objects.get(task_id=master_task_id)
    master_task.date_completed = timezone.now()
    master_task.success = True
    master_task.save()
            
@shared_task
def update_data():
    # Save this data update task
    task_id = update_data.request.id
    data_update = DataUpdateTask(task_id=task_id)
    data_update.save()
    # Execute the scraping of forum profiles
    forum_profiles = ForumProfile.objects.filter(active=True)
    scraping_tasks = scrape_forum_profile.starmap([(fp.id, task_id) for fp in forum_profiles])
    workflow = chain(
        scraping_tasks, # Execute scraping tasks
        update_global_stats.si(task_id), # Execute task to update global stats
        calculate_points.si(task_id), # Execute task to calculate points
        mark_master_task_complete.si(task_id) # Mark the data update run as complete
    )
    workflow.apply_async()