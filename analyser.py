#!/usr/bin/env python3
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
import argparse
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class WhatsAppAnalyzer:
    def __init__(self, filepath_or_buffer, output_dir='output'):
        self.filepath_or_buffer = filepath_or_buffer
        self.messages = []
        self.df = None
        self.output_dir = output_dir
        if self.output_dir: os.makedirs(self.output_dir, exist_ok=True)

    def _read_lines(self):
        """Return list of lines from a path or a file-like object."""
        if isinstance(self.filepath_or_buffer, str):
            with open(self.filepath_or_buffer, 'r', encoding='utf-8') as fp: return fp.readlines()
        if hasattr(self.filepath_or_buffer, 'read'):
            raw = self.filepath_or_buffer.read()
            if isinstance(raw, bytes): raw = raw.decode()
            return raw.splitlines()
        raise ValueError('filepath_or_buffer must be a path or file-like object')
        
    def parse_chat(self):
        """Parse WhatsApp chat export file"""
        # Pattern for WhatsApp messages (handles multiple date formats)
        patterns = [
            r'(\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\s*[-–]\s*([^:]+?):\s*(.*)',
            r'(\[\d{1,2}/\d{1,2}/\d{2,4},?\s+\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM|am|pm)?\])\s*([^:]+?):\s*(.*)',
        ]
        
        lines = self._read_lines()
        
        for line in lines:
            matched = False
            for pattern in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    timestamp_str = match.group(1).strip('[]')
                    sender = match.group(2).strip()
                    message = match.group(3).strip()
                    
                    # Try different timestamp formats
                    timestamp = None
                    for fmt in ['%m/%d/%y, %I:%M %p', '%d/%m/%Y, %H:%M',
                                '%m/%d/%Y, %I:%M %p', '%d/%m/%y, %H:%M',
                                '%m/%d/%y, %H:%M', '%d/%m/%Y, %H:%M:%S']:
                        try:
                            timestamp = datetime.strptime(timestamp_str, fmt)
                            break
                        except ValueError: continue
                    
                    if timestamp:
                        self.messages.append({
                            'timestamp': timestamp,
                            'sender': sender,
                            'message': message
                        })
                        matched = True
                        break
        
        if not self.messages: raise ValueError("No messages found. Please check the chat export format.")
        
        self.df = pd.DataFrame(self.messages)
        self.df = self.df.sort_values('timestamp').reset_index(drop=True)
        print(f"✓ Parsed {len(self.df)} messages from {len(self.df['sender'].unique())} participants")

    def _save_or_return(self, fig, filename=None):
        if filename and self.output_dir:
            out = os.path.join(self.output_dir, filename)
            fig.savefig(out)
            print(f"✓ Saved {filename}")
        return fig
        
    def calculate_response_times(self):
        """Calculate response times between messages"""
        response_times = []
        
        for i in range(1, len(self.df)):
            prev_sender = self.df.iloc[i-1]['sender']
            curr_sender = self.df.iloc[i]['sender']
            
            # Only count if different person responds
            if prev_sender != curr_sender:
                time_diff = (self.df.iloc[i]['timestamp'] - 
                           self.df.iloc[i-1]['timestamp']).total_seconds() / 60
                
                # Filter out unreasonably long gaps (> 24 hours)
                if 0 < time_diff < 1440:
                    response_times.append({
                        'responder': curr_sender,
                        'response_time_minutes': time_diff
                    })
        
        return pd.DataFrame(response_times)
    
    def plot_response_time_percentiles(self):
        """Plot P50, P90, P95, P99 response times"""
        rt_df = self.calculate_response_times()
        
        if rt_df.empty:
            print("⚠ No response time data available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Overall percentiles
        percentiles = [50, 90, 95, 99]
        values = [np.percentile(rt_df['response_time_minutes'], p) for p in percentiles]
        
        colors = ['#2ecc71', '#f39c12', '#e74c3c', '#c0392b']
        bars = ax1.bar([f'P{p}' for p in percentiles], values, color=colors, alpha=0.7)
        ax1.set_ylabel('Response Time (minutes)')
        ax1.set_title('Response Time Percentiles (Programmer Style)', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}m',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Per person percentiles
        for sender in rt_df['responder'].unique():
            sender_data = rt_df[rt_df['responder'] == sender]['response_time_minutes']
            if len(sender_data) > 5:  # Only if enough data points
                p50 = np.percentile(sender_data, 50)
                p90 = np.percentile(sender_data, 90)
                ax2.scatter(p50, p90, s=200, alpha=0.6, label=sender[:20])
        
        ax2.set_xlabel('P50 Response Time (minutes)')
        ax2.set_ylabel('P90 Response Time (minutes)')
        ax2.set_title('Response Time by Person', fontsize=14, fontweight='bold')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        fig = plt.gcf()
        print("✓ Generated response time percentiles chart")
        return self._save_or_return(fig, '01_response_time_percentiles.png')

    def plot_response_time_heatmap(self):
        """Plot response time by hour of day"""
        rt_df = self.calculate_response_times()
        
        if rt_df.empty:
            return
        
        # Merge with timestamps
        rt_df = rt_df.join(self.df[['timestamp']].iloc[1:].reset_index(drop=True))
        rt_df['hour'] = rt_df['timestamp'].dt.hour
        rt_df['day_of_week'] = rt_df['timestamp'].dt.dayofweek
        
        # Create heatmap data
        heatmap_data = rt_df.groupby(['day_of_week', 'hour'])['response_time_minutes'].median().unstack(fill_value=0)
        
        plt.figure(figsize=(14, 6))
        sns.heatmap(heatmap_data, cmap='RdYlGn_r', annot=False, fmt='.0f', 
                   cbar_kws={'label': 'Median Response Time (minutes)'})
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        plt.yticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5], 
                  ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rotation=0)
        plt.title('Response Time Heatmap: When Are They Fastest?', fontsize=14, fontweight='bold')
        plt.tight_layout()
        fig = plt.gcf()
        print("✓ Generated response time heatmap")
        return self._save_or_return(fig, '02_response_time_heatmap.png')

    def plot_message_volume(self):
        """Plot message volume by person"""
        message_counts = self.df['sender'].value_counts()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Bar chart
        colors = plt.cm.Set3(range(len(message_counts)))
        bars = ax1.barh(range(len(message_counts)), message_counts.values, color=colors)
        ax1.set_yticks(range(len(message_counts)))
        ax1.set_yticklabels([name[:30] for name in message_counts.index])
        ax1.set_xlabel('Number of Messages')
        ax1.set_title('Who Talks More?', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Add percentages
        total = message_counts.sum()
        for i, (bar, count) in enumerate(zip(bars, message_counts.values)):
            pct = (count / total) * 100
            ax1.text(count, i, f' {count} ({pct:.1f}%)', 
                    va='center', fontsize=9)
        
        # Pie chart
        ax2.pie(message_counts.values, labels=[name[:20] for name in message_counts.index], 
               autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.set_title('Message Share', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        fig = plt.gcf()
        print("✓ Generated message volume chart")
        return self._save_or_return(fig, '03_message_volume.png')

    def plot_activity_patterns(self):
        """Plot activity by hour and day"""
        self.df['hour'] = self.df['timestamp'].dt.hour
        self.df['day_of_week'] = self.df['timestamp'].dt.dayofweek
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # By hour
        hourly = self.df.groupby('hour').size()
        ax1.bar(hourly.index, hourly.values, color='#3498db', alpha=0.7)
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Number of Messages')
        ax1.set_title('Most Active Hours: When Does This Chat Explode?', fontsize=14, fontweight='bold')
        ax1.set_xticks(range(24))
        ax1.grid(axis='y', alpha=0.3)
        
        # Highlight late night (12am-6am)
        late_night_mask = (hourly.index >= 0) & (hourly.index < 6)
        ax1.bar(hourly.index[late_night_mask], hourly.values[late_night_mask], 
               color='#e74c3c', alpha=0.7, label='Late Night Activity')
        ax1.legend()
        
        # By day of week
        daily = self.df.groupby('day_of_week').size()
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        colors_day = ['#3498db']*5 + ['#2ecc71']*2  # Different color for weekends
        ax2.bar(range(7), daily.values, color=colors_day, alpha=0.7)
        ax2.set_xlabel('Day of Week')
        ax2.set_ylabel('Number of Messages')
        ax2.set_title('Weekend Warrior vs Weekday Ghost', fontsize=14, fontweight='bold')
        ax2.set_xticks(range(7))
        ax2.set_xticklabels(days)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        fig = plt.gcf()
        print("✓ Generated activity patterns chart")
        return self._save_or_return(fig, '04_activity_patterns.png')

    def plot_conversation_initiators(self):
        """Who starts conversations more?"""
        self.df['time_gap'] = self.df['timestamp'].diff().dt.total_seconds() / 3600  # hours
        
        # Consider new conversation if gap > 6 hours
        conversation_starters = self.df[self.df['time_gap'] > 6]['sender'].value_counts()
        
        if conversation_starters.empty:
            print("⚠ Not enough data for conversation initiators")
            return
        
        plt.figure(figsize=(10, 6))
        colors = plt.cm.Pastel1(range(len(conversation_starters)))
        bars = plt.bar(range(len(conversation_starters)), conversation_starters.values, color=colors)
        plt.xticks(range(len(conversation_starters)), 
                  [name[:20] for name in conversation_starters.index], rotation=45, ha='right')
        plt.ylabel('Number of Conversations Started')
        plt.title('Who Initiates Conversations More? (Carrying This Friendship)', 
                 fontsize=14, fontweight='bold')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, val in zip(bars, conversation_starters.values):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        fig = plt.gcf()
        print("✓ Generated conversation initiators chart")
        return self._save_or_return(fig, '05_conversation_initiators.png')

    def plot_double_text_frequency(self):
        """Analyze double texting (multiple messages before response)"""
        double_texts = []
        current_streak = 1
        current_sender = self.df.iloc[0]['sender']
        
        for i in range(1, len(self.df)):
            if self.df.iloc[i]['sender'] == current_sender:
                current_streak += 1
            else:
                if current_streak > 1:
                    double_texts.append({
                        'sender': current_sender,
                        'streak': current_streak
                    })
                current_sender = self.df.iloc[i]['sender']
                current_streak = 1
        
        if not double_texts:
            print("⚠ No double texting detected")
            return
        
        dt_df = pd.DataFrame(double_texts)
        sender_stats = dt_df.groupby('sender').agg({
            'streak': ['count', 'mean', 'max']
        }).round(2)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Frequency
        freq = dt_df['sender'].value_counts()
        ax1.barh(range(len(freq)), freq.values, color='#e74c3c', alpha=0.7)
        ax1.set_yticks(range(len(freq)))
        ax1.set_yticklabels([name[:25] for name in freq.index])
        ax1.set_xlabel('Double Text Incidents')
        ax1.set_title('Double Text Frequency (Desperation Meter)', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Max streak
        max_streaks = dt_df.groupby('sender')['streak'].max().sort_values(ascending=False)
        ax2.barh(range(len(max_streaks)), max_streaks.values, color='#9b59b6', alpha=0.7)
        ax2.set_yticks(range(len(max_streaks)))
        ax2.set_yticklabels([name[:25] for name in max_streaks.index])
        ax2.set_xlabel('Max Consecutive Messages')
        ax2.set_title('Longest Message Streak (Before Getting a Response)', 
                     fontsize=14, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        fig = plt.gcf()
        print("✓ Generated double text analysis")
        return self._save_or_return(fig, '06_double_text_frequency.png')
    
    def plot_message_length_analysis(self):
        """Analyze message lengths"""
        self.df['message_length'] = self.df['message'].str.len()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Distribution
        for sender in self.df['sender'].unique():
            sender_data = self.df[self.df['sender'] == sender]['message_length']
            ax1.hist(sender_data, bins=50, alpha=0.5, label=sender[:20])
        
        ax1.set_xlabel('Message Length (characters)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Message Length Distribution', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.set_xlim(0, 500)
        ax1.grid(axis='y', alpha=0.3)
        
        # Average by person
        avg_length = self.df.groupby('sender')['message_length'].mean().sort_values(ascending=False)
        colors = plt.cm.viridis(np.linspace(0, 1, len(avg_length)))
        bars = ax2.barh(range(len(avg_length)), avg_length.values, color=colors)
        ax2.set_yticks(range(len(avg_length)))
        ax2.set_yticklabels([name[:25] for name in avg_length.index])
        ax2.set_xlabel('Average Message Length (characters)')
        ax2.set_title('Paragraph Sender vs One-Word Responder', fontsize=14, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # Add labels
        for i, (bar, val) in enumerate(zip(bars, avg_length.values)):
            ax2.text(val, i, f' {val:.0f}', va='center', fontsize=9)
        
        plt.tight_layout()
        fig = plt.gcf()
        print("✓ Generated message length analysis")
        return self._save_or_return(fig, '07_message_length_analysis.png')
    
    def plot_emoji_analysis(self):
        """Analyze emoji usage"""
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        emoji_data = []
        for _, row in self.df.iterrows():
            emojis = emoji_pattern.findall(row['message'])
            for emoji in emojis:
                emoji_data.append({'sender': row['sender'], 'emoji': emoji})
        
        if not emoji_data:
            print("⚠ No emojis found in chat")
            return
        
        emoji_df = pd.DataFrame(emoji_data)
        
        fig, axes = plt.subplots(1, min(3, len(self.df['sender'].unique())), 
                                figsize=(15, 5))
        if len(self.df['sender'].unique()) == 1:
            axes = [axes]
        
        for idx, sender in enumerate(list(self.df['sender'].unique())[:3]):
            sender_emojis = emoji_df[emoji_df['sender'] == sender]['emoji'].value_counts().head(10)
            
            if len(sender_emojis) > 0:
                axes[idx].barh(range(len(sender_emojis)), sender_emojis.values, color='#f39c12', alpha=0.7)
                axes[idx].set_yticks(range(len(sender_emojis)))
                axes[idx].set_yticklabels([f'{emoji} ({count})' 
                                          for emoji, count in sender_emojis.items()])
                axes[idx].set_xlabel('Frequency')
                axes[idx].set_title(f'{sender[:20]} Top Emojis', fontsize=12, fontweight='bold')
                axes[idx].grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        fig = plt.gcf()
        print("✓ Generated emoji analysis")
        return self._save_or_return(fig, '08_emoji_analysis.png')
    
    def plot_question_frequency(self):
        """Analyze who asks more questions"""
        self.df['has_question'] = self.df['message'].str.contains(r'\?')
        question_counts = self.df[self.df['has_question']].groupby('sender').size()
        total_messages = self.df.groupby('sender').size()
        question_rate = (question_counts / total_messages * 100).sort_values(ascending=False)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Raw counts
        colors = plt.cm.Set2(range(len(question_counts)))
        ax1.bar(range(len(question_counts)), question_counts.values, color=colors, alpha=0.7)
        ax1.set_xticks(range(len(question_counts)))
        ax1.set_xticklabels([name[:15] for name in question_counts.index], rotation=45, ha='right')
        ax1.set_ylabel('Number of Questions')
        ax1.set_title('Who Asks More Questions?', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Percentage
        ax2.bar(range(len(question_rate)), question_rate.values, color=colors, alpha=0.7)
        ax2.set_xticks(range(len(question_rate)))
        ax2.set_xticklabels([name[:15] for name in question_rate.index], rotation=45, ha='right')
        ax2.set_ylabel('Question Rate (%)')
        ax2.set_title('Questions as % of Messages', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '09_question_frequency.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated question frequency analysis")
    
    def plot_conversation_gaps(self):
        """Analyze longest gaps in conversation"""
        self.df['time_gap'] = self.df['timestamp'].diff()
        top_gaps = self.df.nlargest(10, 'time_gap')[['timestamp', 'time_gap', 'sender']]
        
        plt.figure(figsize=(12, 6))
        gap_hours = top_gaps['time_gap'].dt.total_seconds() / 3600
        colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(gap_hours)))
        bars = plt.barh(range(len(gap_hours)), gap_hours, color=colors)
        
        plt.yticks(range(len(gap_hours)), 
                  [f"{row['timestamp'].strftime('%Y-%m-%d')} ({row['sender'][:15]})" 
                   for _, row in top_gaps.iterrows()])
        plt.xlabel('Gap Duration (hours)')
        plt.title('Longest Conversation Gaps (Hall of Shame)', fontsize=14, fontweight='bold')
        plt.grid(axis='x', alpha=0.3)
        
        # Add labels
        for i, (bar, val) in enumerate(zip(bars, gap_hours)):
            days = val / 24
            label = f'{days:.1f}d' if days >= 1 else f'{val:.1f}h'
            plt.text(val, i, f' {label}', va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '10_conversation_gaps.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated conversation gaps analysis")
    
    def plot_daily_streak(self):
        """Calculate daily messaging streak"""
        daily_counts = self.df.groupby(self.df['timestamp'].dt.date).size()
        dates = pd.date_range(daily_counts.index.min(), daily_counts.index.max())
        daily_series = daily_counts.reindex(dates, fill_value=0)
        
        # Find longest streak
        current_streak = 0
        max_streak = 0
        for count in daily_series:
            if count > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        plt.figure(figsize=(14, 6))
        plt.plot(daily_series.index, daily_series.values, linewidth=2, color='#3498db')
        plt.fill_between(daily_series.index, daily_series.values, alpha=0.3, color='#3498db')
        plt.xlabel('Date')
        plt.ylabel('Messages per Day')
        plt.title(f'Daily Message Activity (Longest Streak: {max_streak} days)', 
                 fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '11_daily_streak.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated daily streak chart")
    
    def generate_summary_stats(self):
        """Generate a summary statistics report"""
        rt_df = self.calculate_response_times()
        
        stats = {
            'Total Messages': len(self.df),
            'Participants': len(self.df['sender'].unique()),
            'Date Range': f"{self.df['timestamp'].min().date()} to {self.df['timestamp'].max().date()}",
            'Days Active': (self.df['timestamp'].max() - self.df['timestamp'].min()).days,
            'Avg Messages/Day': f"{len(self.df) / max((self.df['timestamp'].max() - self.df['timestamp'].min()).days, 1):.1f}",
            'P50 Response Time': f"{np.percentile(rt_df['response_time_minutes'], 50):.1f} min" if not rt_df.empty else 'N/A',
            'P90 Response Time': f"{np.percentile(rt_df['response_time_minutes'], 90):.1f} min" if not rt_df.empty else 'N/A',
            'P99 Response Time': f"{np.percentile(rt_df['response_time_minutes'], 99):.1f} min" if not rt_df.empty else 'N/A',
        }
        
        # Create summary visualization
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.axis('off')
        
        title_text = "WhatsApp Chat Analytics Summary"
        subtitle_text = "(Programmer Style Stats)"
        
        y_pos = 0.95
        ax.text(0.5, y_pos, title_text, ha='center', va='top', 
               fontsize=20, fontweight='bold')
        y_pos -= 0.08
        ax.text(0.5, y_pos, subtitle_text, ha='center', va='top', 
               fontsize=14, style='italic', color='gray')
        y_pos -= 0.1
        
        for key, value in stats.items():
            ax.text(0.25, y_pos, key + ':', ha='left', va='top', 
                   fontsize=12, fontweight='bold')
            ax.text(0.75, y_pos, str(value), ha='right', va='top', 
                   fontsize=12, color='#2c3e50')
            y_pos -= 0.08
        
        # Add top contributors
        y_pos -= 0.05
        ax.text(0.5, y_pos, 'Top Contributors', ha='center', va='top',
               fontsize=14, fontweight='bold', color='#e74c3c')
        y_pos -= 0.08
        
        top_senders = self.df['sender'].value_counts().head(3)
        for sender, count in top_senders.items():
            pct = (count / len(self.df)) * 100
            ax.text(0.5, y_pos, f"[TOP] {sender[:30]}: {count} msgs ({pct:.1f}%)",
                   ha='center', va='top', fontsize=11)
            y_pos -= 0.06
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, '00_summary_stats.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated summary statistics")
        
        return stats
    
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("\n🚀 Starting WhatsApp Chat Analysis...\n")
        
        self.parse_chat()
        
        print("\n📈 Generating visualizations...\n")
        
        self.generate_summary_stats()
        self.plot_response_time_percentiles()
        self.plot_response_time_heatmap()
        self.plot_message_volume()
        self.plot_activity_patterns()
        self.plot_conversation_initiators()
        self.plot_double_text_frequency()
        self.plot_message_length_analysis()
        self.plot_emoji_analysis()
        self.plot_question_frequency()
        self.plot_conversation_gaps()
        self.plot_daily_streak()
        
        print(f"\n✅ Analysis complete! All charts saved to '{self.output_dir}/' directory\n")
        print("📊 Generated visualizations:")
        print("   - 00_summary_stats.png")
        print("   - 01_response_time_percentiles.png")
        print("   - 02_response_time_heatmap.png")
        print("   - 03_message_volume.png")
        print("   - 04_activity_patterns.png")
        print("   - 05_conversation_initiators.png")
        print("   - 06_double_text_frequency.png")
        print("   - 07_message_length_analysis.png")
        print("   - 08_emoji_analysis.png")
        print("   - 09_question_frequency.png")
        print("   - 10_conversation_gaps.png")
        print("   - 11_daily_streak.png")


def main():
    parser = argparse.ArgumentParser(
        description='WhatsApp Chat Analyzer - Generate programmer-style analytics from your exported chats'
    )
    parser.add_argument('chat_file', help='Path to WhatsApp chat export file (.txt)')
    parser.add_argument('-o', '--output', default='output', 
                       help='Output directory for generated charts (default: output)')
    
    args = parser.parse_args()
    
    analyzer = WhatsAppAnalyzer(args.chat_file, args.output)
    analyzer.generate_all_visualizations()


if __name__ == '__main__':
    main()