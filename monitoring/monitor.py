import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os

from .core.search_client import EpsteinSearchClient
from .core.linkedin_parser import LinkedInParser
from .database.models import Database, Contact, Match, Alert, MonitorJob

logger = logging.getLogger(__name__)


class MonitoringSystem:
    
    def __init__(self, db: Database, sendgrid_api_key: Optional[str] = None):
        self.db = db
        self.sendgrid_api_key = sendgrid_api_key or os.getenv('SENDGRID_API_KEY')
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        logger.info("Starting monitoring system")
        self.scheduler.start()
        self._load_jobs()
    
    def stop(self):
        logger.info("Stopping monitoring system")
        self.scheduler.shutdown()
    
    def _load_jobs(self):
        session = self.db.get_session()
        try:
            jobs = session.query(MonitorJob).filter(MonitorJob.is_active == True).all()
            
            for job in jobs:
                self.add_monitoring_job(
                    job_id=job.id,
                    csv_path=job.csv_path,
                    email_recipient=job.email_recipient,
                    check_interval_hours=job.check_interval_hours
                )
                logger.info(f"Loaded monitoring job: {job.name}")
        finally:
            session.close()
    
    def add_monitoring_job(
        self,
        job_id: int,
        csv_path: str,
        email_recipient: str,
        check_interval_hours: int = 24
    ):
        self.scheduler.add_job(
            func=self._check_for_updates,
            trigger=IntervalTrigger(hours=check_interval_hours),
            args=[job_id, csv_path, email_recipient],
            id=f'monitor_{job_id}',
            replace_existing=True
        )
        logger.info(f"Added monitoring job {job_id} with {check_interval_hours}h interval")
    
    def remove_monitoring_job(self, job_id: int):
        try:
            self.scheduler.remove_job(f'monitor_{job_id}')
            logger.info(f"Removed monitoring job {job_id}")
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
    
    async def _check_for_updates(
        self,
        job_id: int,
        csv_path: str,
        email_recipient: str
    ):
        logger.info(f"Running monitoring check for job {job_id}")
        
        session = self.db.get_session()
        try:
            job = session.query(MonitorJob).get(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return
            
            job.last_run = datetime.utcnow()
            job.next_run = datetime.utcnow() + timedelta(hours=job.check_interval_hours)
            session.commit()
            
            contacts = LinkedInParser.parse_csv(csv_path)
            
            new_matches = []
            async with EpsteinSearchClient() as client:
                for contact in contacts:
                    existing_match = session.query(Match).join(Contact).filter(
                        Contact.full_name == contact.full_name
                    ).first()
                    
                    results = await client.search_name(contact.full_name)
                    current_mention_count = len(results)
                    
                    if existing_match:
                        if current_mention_count > existing_match.total_mentions:
                            new_mentions = current_mention_count - existing_match.total_mentions
                            new_matches.append({
                                'name': contact.full_name,
                                'new_mentions': new_mentions,
                                'total_mentions': current_mention_count
                            })
                            logger.info(f"Found {new_mentions} new mentions for {contact.full_name}")
                    elif current_mention_count > 0:
                        new_matches.append({
                            'name': contact.full_name,
                            'new_mentions': current_mention_count,
                            'total_mentions': current_mention_count
                        })
                        logger.info(f"Found new match: {contact.full_name} ({current_mention_count} mentions)")
            
            if new_matches:
                for match in new_matches:
                    alert = Alert(
                        job_id=job_id,
                        contact_name=match['name'],
                        new_mentions_count=match['new_mentions'],
                        message=f"Found {match['new_mentions']} new mentions for {match['name']}"
                    )
                    session.add(alert)
                
                session.commit()
                
                if self.sendgrid_api_key and email_recipient:
                    await self._send_alert_email(job.name, new_matches, email_recipient)
            else:
                logger.info(f"No new matches found for job {job_id}")
        
        except Exception as e:
            logger.error(f"Error in monitoring check for job {job_id}: {e}")
        finally:
            session.close()
    
    async def _send_alert_email(
        self,
        job_name: str,
        new_matches: List[Dict[str, Any]],
        recipient: str
    ):
        try:
            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            
            subject = f"Epstein Monitor Alert: {len(new_matches)} New Matches"
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background:
                    .content {{ padding: 20px; }}
                    .match {{ 
                        background:
                        padding: 15px; 
                        margin: 10px 0; 
                        border-left: 4px solid
                    }}
                    .warning {{ color:
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>🔍 Epstein Document Monitor Alert</h2>
                    <p>Job: {job_name}</p>
                </div>
                <div class="content">
                    <p>New matches found in Epstein court documents:</p>
                    
                    {''.join([f'''
                    <div class="match">
                        <strong>{match['name']}</strong><br>
                        {match['new_mentions']} new mentions<br>
                        Total mentions: {match['total_mentions']}
                    </div>
