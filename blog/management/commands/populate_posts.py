import os
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from blog.models import Post
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from slugify import slugify
import time

class Command(BaseCommand):
    help = 'Populates the database with 30 actual posts from various news sources'

    def handle(self, *args, **kwargs):
        # Get or create a user to be the author of all posts
        author, created = User.objects.get_or_create(
            username='news_aggregator',
            defaults={
                'email': 'news@example.com',
                'password': 'unusablepassword'
            }
        )

        # List of sources to scrape from
        sources = [
            {
                'name': 'BBC',
                'url': 'https://www.bbc.com/news',
                'article_selector': 'a.gs-c-promo-heading',
                'base_url': 'https://www.bbc.com',
                'content_selector': 'div.ssrcss-11r1m41-RichTextComponentWrapper p',
                'title_selector': 'h1#main-heading'
            },
            {
                'name': 'CNN',
                'url': 'https://www.cnn.com/world',
                'article_selector': 'a.container__link',
                'base_url': 'https://www.cnn.com',
                'content_selector': 'div.article__content p.paragraph',
                'title_selector': 'h1.headline__text'
            },
            {
                'name': 'Punch',
                'url': 'https://punchng.com/topics/news/',
                'article_selector': 'h2.post-title a',
                'base_url': 'https://punchng.com',
                'content_selector': 'div.post-content p',
                'title_selector': 'h1.post-title'
            }
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        posts_created = 0
        max_posts = 30
        failed_attempts = 0
        max_failed_attempts = 10

        while posts_created < max_posts and failed_attempts < max_failed_attempts:
            # Randomly select a source
            source = random.choice(sources)
            
            try:
                # Get the main page
                response = requests.get(source['url'], headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find article links
                article_links = soup.select(source['article_selector'])
                random.shuffle(article_links)  # Shuffle to get random articles
                
                for link in article_links:
                    if posts_created >= max_posts:
                        break
                        
                    try:
                        article_url = link.get('href')
                        if not article_url.startswith('http'):
                            article_url = urljoin(source['base_url'], article_url)
                        
                        # Get the article page
                        article_response = requests.get(article_url, headers=headers, timeout=10)
                        article_response.raise_for_status()
                        article_soup = BeautifulSoup(article_response.text, 'html.parser')
                        
                        # Extract title
                        title_element = article_soup.select_one(source['title_selector'])
                        if not title_element:
                            continue
                        title = title_element.get_text().strip()
                        
                        # Extract content
                        content_elements = article_soup.select(source['content_selector'])
                        content = '\n\n'.join([p.get_text().strip() for p in content_elements if p.get_text().strip()])
                        
                        if not content:
                            continue
                            
                        # Create slug
                        slug = slugify(title)
                        
                        # Create the post
                        Post.objects.create(
                            title=title,
                            content=content,
                            author=author,
                            slug=slug
                        )
                        
                        posts_created += 1
                        self.stdout.write(self.style.SUCCESS(f'Successfully created post: {title}'))
                        time.sleep(2)  # Be polite to the servers
                        
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Error processing article: {str(e)}'))
                        continue
                        
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error accessing {source["name"]}: {str(e)}'))
                failed_attempts += 1
                continue
                
        self.stdout.write(self.style.SUCCESS(f'Successfully created {posts_created} posts'))