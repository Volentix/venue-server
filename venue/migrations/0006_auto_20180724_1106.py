# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-07-24 11:06
from __future__ import unicode_literals

from django.db import migrations
from constance import config


MEMBER_SIGNATURES = [
    {
        'id': 'ced8d577-92a3-42e4-96ac-418fb01e7ed9',
        'name': 'Member Design 1',
        'forum_site_id': '4b8b11d1-14bb-46a7-ac8b-397587235b28',
        'user_ranks': [
            '09a7ad5e-1da4-4e7b-8799-93cf70ceb6f0'
        ],
        'code': '''[center][b][size=8pt][url=http://volentix.io/][u]     V O L E N T I X[/u][/url]   █   [url=http://volentix.io/]Decentralized Change[/url]   █   [url=http://volentix.io/]3rd Party DAPP Platform[/url]
[url=http://volentix.io/]▬ •  VENUE  • ▬  Social Rewards Platform[/url]   █   [url=https://bit.ly/2Jj7Tes]ANN[/url]   [url=https://twitter.com/Volentix/]TWITTER[/url]   [url=https://t.me/volentix]TELEGRAM[/url]   █   [url=http://volentix.io/]▬ • VDEX • ▬  Decentralized Exchange[/url]
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬    ( V ) BETA TESTER  |  Designed by Zpectrum    ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬[/size][/b][/center]''',
        'test_signature': 'When words fail, music speaks',
        'image': 'https://s3.ca-central-1.amazonaws.com/venue-static/signatures/member_1.png',
        'active': True,
        'date_added': '2018-07-24 12:03:50+00:00'
    },
    {
        'id': '764ab6b6-fb92-40ad-839c-4f26ee86eed8',
        'name': 'Member Design 2',
        'forum_site_id': '4b8b11d1-14bb-46a7-ac8b-397587235b28',
        'user_ranks': [
            '09a7ad5e-1da4-4e7b-8799-93cf70ceb6f0'
        ],
        'code': '''[center][b][size=8pt]▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
[url=https://volentix.io/]VESPUCCI  ►  VENUE    ▌  [size=9pt]VOLENTIX  |  Decentralized Change[/size]  ▐    VDEX  ◄  [u]VCHAIN    [/u][/url]
▬▬▬▬▬▬  |  [url=https://bit.ly/2Jj7Tes]ANN[/url]  •  [url=https://twitter.com/Volentix/]TWITTER[/url]  •  [url=https://t.me/volentix]TELEGRAM[/url]   █   ( V ) BETA TESTER  •  Designed by Zpectrum  |  ▬▬▬▬▬▬[/size][/b][/center]''',
        'test_signature': 'Embrace the glorious mess that you are',
        'image': 'https://s3.ca-central-1.amazonaws.com/venue-static/signatures/member_2.png',
        'active': True,
        'date_added': '2018-07-24 12:03:50+00:00'
    },
    {
        'id': '764ab6b6-fb92-40ad-839c-4f26ee86eed8',
        'name': 'Member Design 3',
        'forum_site_id': '4b8b11d1-14bb-46a7-ac8b-397587235b28',
        'user_ranks': [
            '09a7ad5e-1da4-4e7b-8799-93cf70ceb6f0'
        ],
        'code': '''[center][b][size=8pt][url=http://volentix.io/][u]          V O L E N T I X[/u][/url]  █  [url=http://volentix.io/]Decentralized Change[/url]  █  ( V ) BETA TESTER  ★  Designed by Zpectrum
▌▌  [url=http://volentix.io/]3rd Party DAPP Platform[/url]   ▌▌  ▬▬▬▬  [url=https://bit.ly/2Jj7Tes]ANN[/url]  [url=https://twitter.com/Volentix/]Twitter[/url]  [url=https://t.me/volentix]Telegram[/url]  ▬▬▬▬
[url=http://volentix.io/]Analytical Engine • VESPUCCI   |   VCHAIN • Blockchain Technology  |  Social Rewards Platform • VENUE   |   VDEX • Decentralized Exchange[/url][/size][/b][/center]''',
        'test_signature': 'The meaning of life is to give life meaning',
        'image': 'https://s3.ca-central-1.amazonaws.com/venue-static/signatures/member_3.png',
        'active': True,
        'date_added': '2018-07-24 12:03:50+00:00'
    }
]


def add_member_signatures(apps, schema_editor):
    Signature = apps.get_model('venue', 'Signature')
    # Remove existing sigs, if any
    existing_sigs = Signature.objects.filter(
        user_ranks__name='Member'
    )
    existing_sigs.delete()
    # Save the Member rank signatures
    for sig_details in MEMBER_SIGNATURES:
        signature = Signature(**sig_details)
        signature.save()


def allow_members(apps, schema_editor):
    ForumUserRank = apps.get_model('venue', 'ForumUserRank')
    try:
        member_rank = ForumUserRank.objects.get(
            name='Member',
            forum_site__name='bitcointalk.org'
        )
        member_rank.allowed = True
        member_rank.save()
    except ForumUserRank.DoesNotExist:
        pass


def adjust_bonuses(apps, schema_editor):
    ForumUserRank = apps.get_model('venue', 'ForumUserRank')
    ForumPost = apps.get_model('venue', 'ForumPost')
    ranks = {
        'Full Member': 1.0,
        'Sr. Member': 2.0
    }
    for rank_name, bonus_pct in ranks.items():
        try:
            # Adjust bonus percentages in ranks
            forum_rank = ForumUserRank.objects.get(
                name=rank_name,
                forum_site__name='bitcointalk.org'
            )
            forum_rank.bonus_percentage = bonus_pct
            forum_rank.save()
            # Adjust bonus points in existing forum posts
            posts = ForumPost.objects.filter(
                forum_profile__forum_rank=forum_rank
            )
            for post in posts:
                post.influence_bonus_pct = bonus_pct
                bonus_pts = (bonus_pct / 100) * config.POST_POINTS_MULTIPLIER
                post.influence_bonus_pts = bonus_pts
                total_pts = float(post.base_points) + bonus_pts
                post.total_points = total_pts
                post.save()
        except ForumUserRank.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('venue', '0005_auto_20180716_1228'),
    ]

    operations = [
        migrations.RunPython(add_member_signatures),
        migrations.RunPython(allow_members),
        migrations.RunPython(adjust_bonuses)
    ]
